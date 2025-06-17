import logging
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from src.config import TEAM_MEMBERS
from src.graph import build_graph
from src.utils.json_cleaner import clean_json_response
from langchain_community.adapters.openai import convert_message_to_dict
import uuid
from ..agents.llm import get_llm_by_provider

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Default level is INFO
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def enable_debug_logging():
    """Enable debug level logging for more detailed execution information."""
    logging.getLogger("src").setLevel(logging.DEBUG)


logger = logging.getLogger(__name__)

# Create the graph
graph = build_graph()

# Cache for coordinator messages
coordinator_cache = []
MAX_CACHE_SIZE = 2


async def run_agent_workflow(
    user_input_messages: list,
    debug: bool = False,
    deep_thinking_mode: bool = False,
    search_before_planning: bool = False,
):
    """Run the agent workflow with the given user input.

    Args:
        user_input_messages: The user request messages
        debug: If True, enables debug level logging

    Returns:
        The final state after the workflow completes
    """
    if not user_input_messages:
        raise ValueError("Input could not be empty")

    if debug:
        enable_debug_logging()

    logger.info(f"Starting workflow with user input: {user_input_messages}")

    workflow_id = str(uuid.uuid4())

    streaming_llm_agents = [*TEAM_MEMBERS, "planner", "coordinator"]

    # Reset coordinator cache at the start of each workflow
    global coordinator_cache
    coordinator_cache = []
    global is_handoff_case
    is_handoff_case = False

    # 用于追踪当前计划步骤
    current_plan_steps = []
    current_step_index = -1

    # TODO: extract message content from object, specifically for on_chat_model_stream
    async for event in graph.astream_events(
        {
            # Constants
            "TEAM_MEMBERS": TEAM_MEMBERS,
            # Runtime Variables
            "messages": user_input_messages,
            "deep_thinking_mode": deep_thinking_mode,
            "search_before_planning": search_before_planning,
        },
        version="v2",
        config={"recursion_limit": 50},
    ):
        kind = event.get("event")
        data = event.get("data")
        name = event.get("name")
        metadata = event.get("metadata")
        node = (
            ""
            if (metadata.get("checkpoint_ns") is None)
            else metadata.get("checkpoint_ns").split(":")[0]
        )
        langgraph_step = (
            ""
            if (metadata.get("langgraph_step") is None)
            else str(metadata["langgraph_step"])
        )
        run_id = "" if (event.get("run_id") is None) else str(event["run_id"])

        # 调试：打印所有 on_chain_end 事件
        if kind == "on_chain_end":
            logger.debug(f"on_chain_end event - name: {name}, data keys: {list(data.keys()) if data else 'None'}")
            if data and "output" in data:
                output_type = type(data["output"])
                logger.debug(f"  output type: {output_type}")
                if isinstance(data["output"], dict):
                    logger.debug(f"  output keys: {list(data['output'].keys())}")

        # 检查是否有状态更新，获取计划步骤信息
        if kind == "on_chain_end" and name == "planner":
            logger.info(f"Planner chain ended, checking for plan in output")
            # 尝试不同的方式获取 planner 的输出
            if data:
                logger.debug(f"Planner output data: {data}")
                
        # 另一种方式：监听 planner 的消息流
        if kind == "on_chat_model_end" and node == "planner":
            logger.info("Planner model ended, checking for plan")
            # 这里可能包含了 planner 生成的内容
            if data and "output" in data:
                logger.debug(f"Planner model output: {data['output']}")
                
        # 监听消息流，查找包含计划的消息
        if kind == "on_chat_model_stream" and node == "planner":
            content = data.get("chunk", {}).content if data.get("chunk") else None
            if content:
                # 累积 planner 的输出
                if not hasattr(run_agent_workflow, '_planner_buffer'):
                    run_agent_workflow._planner_buffer = ""
                run_agent_workflow._planner_buffer += content
                
        # 当 planner 结束时，解析累积的内容
        if kind == "on_chain_end" and name == "planner":
            if hasattr(run_agent_workflow, '_planner_buffer'):
                try:
                    plan_content = run_agent_workflow._planner_buffer
                    logger.info(f"Accumulated planner content: {plan_content[:100]}...")
                    
                    # 使用统一的JSON清理函数
                    cleaned_plan_content = clean_json_response(plan_content)
                    
                    plan_data = json.loads(cleaned_plan_content)
                    if isinstance(plan_data, dict) and "steps" in plan_data:
                        current_plan_steps = plan_data["steps"]
                        current_step_index = 0
                        logger.info(f"Plan parsed successfully, {len(current_plan_steps)} steps found")
                        # 发送计划步骤信息
                        plan_event = {
                            "event": "plan_generated",
                            "data": {
                                "plan_steps": current_plan_steps,
                                "total_steps": len(current_plan_steps),
                            },
                        }
                        logger.info(f"Yielding plan_generated event")
                        yield plan_event
                    # 清空缓冲区
                    run_agent_workflow._planner_buffer = ""
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse plan: {e}")
                    logger.debug(f"Original plan content: {plan_content}")
                    logger.debug(f"Cleaned plan content: {cleaned_plan_content if 'cleaned_plan_content' in locals() else 'N/A'}")
                    run_agent_workflow._planner_buffer = ""

        # 当 supervisor 开始执行时，检查它要调用哪个 agent
        if kind == "on_chain_start" and name in TEAM_MEMBERS and current_plan_steps:
            logger.info(f"Agent {name} started, checking for matching step")
            # 查找当前 agent 对应的步骤
            for i, step in enumerate(current_plan_steps):
                if step.get("agent_name") == name and i >= current_step_index:
                    current_step_index = i
                    # 发送当前步骤信息
                    step_event = {
                        "event": "step_started",
                        "data": {
                            "step_index": i + 1,  # 1-based index for user
                            "total_steps": len(current_plan_steps),
                            "step_info": step,
                        },
                    }
                    logger.info(f"Yielding step_started event for step {i+1}: {step_event}")
                    yield step_event
                    break

        # 当 agent 完成执行时，发送步骤完成事件
        if kind == "on_chain_end" and name in TEAM_MEMBERS and current_plan_steps:
            logger.info(f"Agent {name} ended, checking for matching step")
            # 查找当前 agent 对应的步骤
            for i, step in enumerate(current_plan_steps):
                if step.get("agent_name") == name:
                    step_end_event = {
                        "event": "step_end",
                        "data": {
                            "step_index": i + 1,
                            "total_steps": len(current_plan_steps),
                            "step_info": step,
                        },
                    }
                    logger.info(f"Yielding step_end event for step {i+1}")
                    yield step_end_event
                    break

        if kind == "on_chain_start" and name in streaming_llm_agents:
            if name == "planner":
                yield {
                    "event": "start_of_workflow",
                    "data": {"workflow_id": workflow_id, "input": user_input_messages},
                }
            ydata = {
                "event": "start_of_agent",
                "data": {
                    "agent_name": name,
                    "agent_id": f"{workflow_id}_{name}_{langgraph_step}",
                },
            }
        elif kind == "on_chain_end" and name in streaming_llm_agents:
            ydata = {
                "event": "end_of_agent",
                "data": {
                    "agent_name": name,
                    "agent_id": f"{workflow_id}_{name}_{langgraph_step}",
                },
            }
        elif kind == "on_chat_model_start" and node in streaming_llm_agents:
            ydata = {
                "event": "start_of_llm",
                "data": {"agent_name": node},
            }
        elif kind == "on_chat_model_end" and node in streaming_llm_agents:
            ydata = {
                "event": "end_of_llm",
                "data": {"agent_name": node},
            }
        elif kind == "on_chat_model_stream" and node in streaming_llm_agents:
            content = data["chunk"].content
            if content is None or content == "":
                if not data["chunk"].additional_kwargs.get("reasoning_content"):
                    # Skip empty messages
                    continue
                ydata = {
                    "event": "message",
                    "data": {
                        "message_id": data["chunk"].id,
                        "delta": {
                            "reasoning_content": (
                                data["chunk"].additional_kwargs["reasoning_content"]
                            )
                        },
                    },
                }
            else:
                # Check if the message is from the coordinator
                if node == "coordinator":
                    # 检查是否包含handoff函数调用（包括各种格式）
                    if ("handoff_to_planner" in content or 
                        "```python" in content or 
                        "```" in content):
                        is_handoff_case = True
                        continue  # 完全跳过包含handoff或代码块的消息
                    
                    # 如果已经识别为handoff情况，跳过所有后续coordinator消息
                    if is_handoff_case:
                        continue
                    
                    # 正常的coordinator消息（如问候、回答等）
                    if len(coordinator_cache) < MAX_CACHE_SIZE:
                        coordinator_cache.append(content)
                        cached_content = "".join(coordinator_cache)
                        
                        # 再次检查缓存的完整内容（包括各种格式）
                        if ("handoff_to_planner" in cached_content or 
                            "```python" in cached_content or 
                            "```" in cached_content):
                            is_handoff_case = True
                            coordinator_cache = []  # 清空缓存
                            continue
                        
                        if len(coordinator_cache) < MAX_CACHE_SIZE:
                            continue
                        
                        # 发送缓存的消息
                        ydata = {
                            "event": "message",
                            "data": {
                                "message_id": data["chunk"].id,
                                "delta": {"content": cached_content},
                            },
                        }
                        coordinator_cache = []  # 清空缓存
                    else:
                        # 直接发送消息
                        ydata = {
                            "event": "message",
                            "data": {
                                "message_id": data["chunk"].id,
                                "delta": {"content": content},
                            },
                        }
                elif node == "db_analyst":
                    # 过滤db_analyst的thought内容
                    if (content.strip().startswith("thought:") or 
                        "thought:" in content.lower() or
                        content.strip().startswith("我需要") or
                        content.strip().startswith("让我") or
                        content.strip().startswith("I need") or
                        content.strip().startswith("Let me")):
                        continue  # 跳过thought相关内容
                    
                    # 发送正常的分析内容
                    ydata = {
                        "event": "message",
                        "data": {
                            "message_id": data["chunk"].id,
                            "delta": {"content": content},
                        },
                    }
                else:
                    # For other agents, send the message directly
                    ydata = {
                        "event": "message",
                        "data": {
                            "message_id": data["chunk"].id,
                            "delta": {"content": content},
                        },
                    }
        elif kind == "on_tool_start" and node in TEAM_MEMBERS:
            ydata = {
                "event": "tool_call",
                "data": {
                    "tool_call_id": f"{workflow_id}_{node}_{name}_{run_id}",
                    "tool_name": name,
                    "tool_input": data.get("input"),
                },
            }
        elif kind == "on_tool_end" and node in TEAM_MEMBERS:
            ydata = {
                "event": "tool_call_result",
                "data": {
                    "tool_call_id": f"{workflow_id}_{node}_{name}_{run_id}",
                    "tool_name": name,
                    "tool_result": data["output"].content if data.get("output") else "",
                },
            }
        else:
            continue
        yield ydata

    if is_handoff_case:
        yield {
            "event": "end_of_workflow",
            "data": {
                "workflow_id": workflow_id,
                "messages": [
                    convert_message_to_dict(msg)
                    for msg in data["output"].get("messages", [])
                ],
            },
        }
