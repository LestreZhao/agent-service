import logging
import json
import uuid
import re
from copy import deepcopy
from datetime import datetime
from typing import Literal
from langchain_core.messages import HumanMessage
from langgraph.types import Command
from langgraph.graph import END

from src.agents.llm import get_llm_by_type
from src.config import TEAM_MEMBERS
from src.config.agents import AGENT_LLM_MAP
from src.tools.search import tavily_tool
from src.utils.file_manager import ExecutionFileManager
from src.utils.json_cleaner import clean_json_response
from .types import State, Router

logger = logging.getLogger(__name__)

RESPONSE_FORMAT = "Response from {}:\n\n<response>\n{}\n</response>\n\n*Please execute the next step.*"

# 初始化文件管理器
file_manager = ExecutionFileManager()


def research_node(state: State) -> Command[Literal["supervisor"]]:
    """Node for the researcher agent that performs research tasks."""
    from src.agents import research_agent
    logger.info("Research agent starting task")
    result = research_agent.invoke(state)
    logger.info("Research agent completed task")
    logger.debug(f"Research agent response: {result['messages'][-1].content}")
    
    # 生成执行总结文件
    task_id = state.get("task_id")
    execution_summaries = state.get("execution_summaries", [])
    
    if task_id:
        try:
            summary = file_manager.save_execution_summary(
                task_id=task_id,
                agent_name="researcher", 
                result_content=result["messages"][-1].content,
                original_messages=state["messages"]
            )
            execution_summaries.append(summary)
            logger.info(f"研究总结已保存到: {summary['file_path']}")
        except Exception as e:
            logger.error(f"保存研究总结失败: {e}")
    
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=RESPONSE_FORMAT.format(
                        "researcher", result["messages"][-1].content
                    ),
                    name="researcher",
                )
            ],
            "execution_summaries": execution_summaries
        },
        goto="supervisor",
    )


def code_node(state: State) -> Command[Literal["supervisor"]]:
    """Node for the coder agent that executes Python code."""
    from src.agents import coder_agent
    logger.info("Code agent starting task")
    result = coder_agent.invoke(state)
    logger.info("Code agent completed task")
    logger.debug(f"Code agent response: {result['messages'][-1].content}")
    
    # 生成执行总结文件
    task_id = state.get("task_id")
    execution_summaries = state.get("execution_summaries", [])
    
    if task_id:
        try:
            summary = file_manager.save_execution_summary(
                task_id=task_id,
                agent_name="coder", 
                result_content=result["messages"][-1].content,
                original_messages=state["messages"]
            )
            execution_summaries.append(summary)
            logger.info(f"代码执行总结已保存到: {summary['file_path']}")
        except Exception as e:
            logger.error(f"保存代码执行总结失败: {e}")
    
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=RESPONSE_FORMAT.format(
                        "coder", result["messages"][-1].content
                    ),
                    name="coder",
                )
            ],
            "execution_summaries": execution_summaries
        },
        goto="supervisor",
    )


def browser_node(state: State) -> Command[Literal["supervisor"]]:
    """Node for the browser agent that performs web browsing tasks."""
    from src.agents import browser_agent
    logger.info("Browser agent starting task")
    result = browser_agent.invoke(state)
    logger.info("Browser agent completed task")
    logger.debug(f"Browser agent response: {result['messages'][-1].content}")
    
    # 生成执行总结文件
    task_id = state.get("task_id")
    execution_summaries = state.get("execution_summaries", [])
    
    if task_id:
        try:
            summary = file_manager.save_execution_summary(
                task_id=task_id,
                agent_name="browser", 
                result_content=result["messages"][-1].content,
                original_messages=state["messages"]
            )
            execution_summaries.append(summary)
            logger.info(f"浏览器操作总结已保存到: {summary['file_path']}")
        except Exception as e:
            logger.error(f"保存浏览器操作总结失败: {e}")
    
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=RESPONSE_FORMAT.format(
                        "browser", result["messages"][-1].content
                    ),
                    name="browser",
                )
            ],
            "execution_summaries": execution_summaries
        },
        goto="supervisor",
    )


def db_analyst_node(state: State) -> Command[Literal["supervisor"]]:
    """Node for the database analyst agent that performs database queries and analysis."""
    from src.agents import db_analyst_agent
    logger.info("Database analyst agent starting task")
    result = db_analyst_agent.invoke(state)
    logger.info("Database analyst agent completed task")
    logger.debug(f"Database analyst agent response: {result['messages'][-1].content}")
    
    # 生成执行总结文件
    task_id = state.get("task_id")
    execution_summaries = state.get("execution_summaries", [])
    
    if task_id:
        try:
            summary = file_manager.save_execution_summary(
                task_id=task_id,
                agent_name="db_analyst", 
                result_content=result["messages"][-1].content,
                original_messages=state["messages"]
            )
            execution_summaries.append(summary)
            logger.info(f"数据分析总结已保存到: {summary['file_path']}")
        except Exception as e:
            logger.error(f"保存数据分析总结失败: {e}")
    
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=RESPONSE_FORMAT.format(
                        "db_analyst", result["messages"][-1].content
                    ),
                    name="db_analyst",
                )
            ],
            "execution_summaries": execution_summaries
        },
        goto="supervisor",
    )


def document_parser_node(state: State) -> Command[Literal["supervisor"]]:
    """Node for the document parser agent that processes and analyzes documents."""
    from src.agents import document_parser_agent
    logger.info("Document parser agent starting task")
    result = document_parser_agent.invoke(state)
    logger.info("Document parser agent completed task")
    logger.debug(f"Document parser agent response: {result['messages'][-1].content}")
    
    # 生成执行总结文件
    task_id = state.get("task_id")
    execution_summaries = state.get("execution_summaries", [])
    
    if task_id:
        try:
            summary = file_manager.save_execution_summary(
                task_id=task_id,
                agent_name="document_parser", 
                result_content=result["messages"][-1].content,
                original_messages=state["messages"]
            )
            execution_summaries.append(summary)
            logger.info(f"文档解析总结已保存到: {summary['file_path']}")
        except Exception as e:
            logger.error(f"保存文档解析总结失败: {e}")
    
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=RESPONSE_FORMAT.format(
                        "document_parser", result["messages"][-1].content
                    ),
                    name="document_parser",
                )
            ],
            "execution_summaries": execution_summaries
        },
        goto="supervisor",
    )


def chart_generator_node(state: State) -> Command[Literal["supervisor"]]:
    """Node for the chart generator agent that creates ECharts visualizations."""
    from src.agents import chart_generator_agent
    logger.info("Chart generator agent starting task")
    result = chart_generator_agent.invoke(state)
    logger.info("Chart generator agent completed task")
    logger.debug(f"Chart generator agent response: {result['messages'][-1].content}")
    
    # 生成执行总结文件
    task_id = state.get("task_id")
    execution_summaries = state.get("execution_summaries", [])
    
    if task_id:
        try:
            summary = file_manager.save_execution_summary(
                task_id=task_id,
                agent_name="chart_generator", 
                result_content=result["messages"][-1].content,
                original_messages=state["messages"]
            )
            execution_summaries.append(summary)
            logger.info(f"图表生成总结已保存到: {summary['file_path']}")
        except Exception as e:
            logger.error(f"保存图表生成总结失败: {e}")
    
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=RESPONSE_FORMAT.format(
                        "chart_generator", result["messages"][-1].content
                    ),
                    name="chart_generator",
                )
            ],
            "execution_summaries": execution_summaries
        },
        goto="supervisor",
    )


def supervisor_node(state: State) -> Command[Literal[*TEAM_MEMBERS, "__end__"]]:
    """Supervisor node that decides which agent should act next."""
    from src.prompts.template import apply_prompt_template
    logger.info("Supervisor evaluating next action")
    messages = apply_prompt_template("supervisor", state)
    response = (
        get_llm_by_type(AGENT_LLM_MAP["supervisor"])
        .with_structured_output(Router)
        .invoke(messages)
    )
    goto = response["next"]
    logger.debug(f"Current state messages: {state['messages']}")
    logger.debug(f"Supervisor response: {response}")

    if goto == "FINISH":
        goto = "__end__"
        logger.info("Workflow completed")
    else:
        logger.info(f"Supervisor delegating to: {goto}")

    return Command(goto=goto, update={"next": goto})


def planner_node(state: State) -> Command[Literal["supervisor", "__end__"]]:
    """Planner node that generate the full plan."""
    from src.prompts.template import apply_prompt_template
    logger.info("Planner generating full plan")
    messages = apply_prompt_template("planner", state)
    # whether to enable deep thinking mode
    llm = get_llm_by_type("basic")
    if state.get("deep_thinking_mode"):
        llm = get_llm_by_type("reasoning")
    if state.get("search_before_planning"):
        searched_content = tavily_tool.invoke({"query": state["messages"][-1].content})
        messages = deepcopy(messages)
        messages[
            -1
        ].content += f"\n\n# Relative Search Results\n\n{json.dumps([{'titile': elem['title'], 'content': elem['content']} for elem in searched_content], ensure_ascii=False)}"
    stream = llm.stream(messages)
    full_response = ""
    for chunk in stream:
        full_response += chunk.content
    logger.debug(f"Current state messages: {state['messages']}")
    logger.debug(f"Planner response: {full_response}")

    # 使用新的JSON清理函数
    cleaned_response = clean_json_response(full_response)

    goto = "supervisor"
    try:
        json.loads(cleaned_response)
        
        # 保存计划文件
        task_id = state.get("task_id")
        if task_id:
            plan_file_path = file_manager.save_plan(task_id, cleaned_response)
            logger.info(f"计划已保存到: {plan_file_path}")
        
    except json.JSONDecodeError as e:
        logger.warning(f"Planner response is not a valid JSON: {e}")
        logger.debug(f"Original response: {full_response}")
        logger.debug(f"Cleaned response: {cleaned_response}")
        goto = "__end__"

    return Command(
        update={
            "messages": [HumanMessage(content=cleaned_response, name="planner")],
            "full_plan": cleaned_response,
        },
        goto=goto,
    )


def coordinator_node(state: State) -> Command[Literal["planner", "__end__"]]:
    """Coordinator node that communicate with customers."""
    from src.prompts.template import apply_prompt_template
    logger.info("Coordinator talking.")
    
    # 初始化任务信息（如果还没有初始化）
    if not state.get("task_id"):
        task_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + str(uuid.uuid4())[:8]
        output_directory = file_manager.create_task_directory(task_id)
        logger.info(f"初始化新任务: {task_id}")
        logger.info(f"输出目录: {output_directory}")
    else:
        task_id = state["task_id"]
        output_directory = state["output_directory"]
    
    messages = apply_prompt_template("coordinator", state)
    response = get_llm_by_type(AGENT_LLM_MAP["coordinator"]).invoke(messages)
    logger.debug(f"Current state messages: {state['messages']}")
    logger.debug(f"coordinator response: {response}")

    goto = "__end__"
    update_data = {
        "task_id": task_id,
        "output_directory": output_directory,
        "execution_summaries": state.get("execution_summaries", [])
    }
    
    if "handoff_to_planner" in response.content:
        goto = "planner"

    return Command(
        goto=goto,
        update=update_data
    )


def reporter_node(state: State) -> Command[Literal["__end__"]]:
    """Reporter node that generates final comprehensive report."""
    logger.info("Reporter agent generating final comprehensive report")
    
    task_id = state.get("task_id")
    if not task_id:
        logger.error("没有找到task_id，无法生成最终报告")
        return Command(goto="__end__")
    
    try:
        # 直接使用LLM和模板生成报告，避免循环导入
        from src.prompts.template import apply_prompt_template
        
        logger.info(f"开始为任务 {task_id} 生成最终报告")
        messages = apply_prompt_template("reporter", state)
        
        # 获取reporter使用的LLM
        llm = get_llm_by_type(AGENT_LLM_MAP["reporter"])
        
        # 创建包含工具的智能体
        from src.tools.file_info_tool import task_files_json_tool
        from langgraph.prebuilt import create_react_agent
        
        temp_reporter_agent = create_react_agent(
            llm,
            tools=[task_files_json_tool]
        )
        
        # 调用智能体生成报告
        result = temp_reporter_agent.invoke({"messages": messages})
        logger.info("Reporter agent completed final report generation")
        
        # 获取reporter的响应内容
        final_content = result["messages"][-1].content
        
        # 生成执行总结文件
        execution_summaries = state.get("execution_summaries", [])
        
        if task_id:
            try:
                summary = file_manager.save_execution_summary(
                    task_id=task_id,
                    agent_name="reporter", 
                    result_content=final_content,
                    original_messages=state["messages"]
                )
                execution_summaries.append(summary)
                logger.info(f"Reporter总结已保存到: {summary['file_path']}")
            except Exception as e:
                logger.error(f"保存Reporter总结失败: {e}")
        
        logger.debug(f"Reporter最终内容: {final_content[:500]}...")
        
        return Command(
            update={
                "messages": [
                    HumanMessage(
                        content=final_content,
                        name="reporter",
                    )
                ],
                "execution_summaries": execution_summaries
            },
            goto="__end__",
        )
        
    except Exception as e:
        logger.error(f"Reporter生成最终报告失败: {e}")
        error_message = f"抱歉，Reporter在生成最终报告时遇到错误: {str(e)}"
        
        return Command(
            update={
                "messages": [
                    HumanMessage(
                        content=error_message,
                        name="reporter",
                    )
                ]
            },
            goto="__end__",
        )
