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
    """Reporter node that reads all execution summaries and generates final integration."""
    from src.prompts.template import apply_prompt_template
    logger.info("Reporter generating final integration")
    
    task_id = state.get("task_id")
    if not task_id:
        logger.error("没有找到task_id，无法生成最终整合")
        return Command(goto="__end__")
    
    # 读取所有执行总结文件
    try:
        summaries = file_manager.read_all_summaries(task_id)
        files_info = file_manager.get_task_files_info(task_id)
        
        logger.info(f"读取到 {len(summaries)} 个执行总结文件")
        for summary in summaries:
            logger.info(f"  - {summary['agent_name']}: {summary['file_path']}")
        
        # 构建整合提示内容
        integration_context = f"""
# 任务整合要求

基于以下执行总结文件，生成最终的用户友好输出：

## 原始计划
{state.get('full_plan', '无计划信息')}

## 执行总结文件
"""
        
        for summary in summaries:
            integration_context += f"""
### {summary['agent_name'].upper()} 总结
文件路径: {summary['file_path']}

{summary['content'][:1000]}...

---
"""
        
        integration_context += """

## 整合输出要求

请生成一个专业的、用户友好的最终报告，包括：
1. 礼貌的用户问候
2. 任务完成情况总结
3. 按类型组织的关键结果
4. 生成的文件列表
5. 后续服务提示

输出格式要求：
- 使用markdown格式
- 结构清晰，层次分明
- 语言专业且友好
- 重点突出关键成果
"""
        
        # 调用LLM生成最终整合
        messages = apply_prompt_template("reporter", state)  # 使用reporter模板
        
        # 替换最后一条消息为整合上下文
        if messages:
            messages[-1].content = integration_context
        
        response = get_llm_by_type("basic").invoke(messages)
        final_content = response.content
        
        # 保存最终整合文件
        final_file_path = file_manager.save_final_integration(task_id, final_content)
        logger.info(f"最终整合报告已保存到: {final_file_path}")
        
        # 生成用户展示内容
        display_content = f"""
# 🎯 任务执行完成

尊敬的用户，我已完成您的任务请求。以下是详细的执行结果：

## 📊 执行概览

- **任务ID**: {task_id}
- **完成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **执行节点数**: {len(summaries)}
- **生成文件数**: {len(files_info.get('summary_files', [])) + 2}  # +2 for plan and final

## 📁 生成文件

### 📋 执行计划
- `plan.md` - 原始任务执行计划

### 📄 执行总结文件
"""

        for summary in summaries:
            agent_name = summary['agent_name']
            file_name = f"{agent_name}_summary.md"
            display_content += f"- `{file_name}` - {agent_name.capitalize()} 节点执行总结\n"

        display_content += f"""
### 🎯 最终整合报告
- `final_integration.md` - 完整的任务执行总结和结论

## 💡 查看方式

所有文件已保存到目录: `{files_info.get('task_directory', 'unknown')}`

您可以通过以下方式查看：
1. 直接打开markdown文件进行预览
2. 使用markdown阅读器查看格式化内容
3. 集成到您的文档系统中

{final_content}

---

如需进一步讨论或有任何问题，请随时告知。
"""
        
        logger.debug(f"最终整合内容: {display_content[:500]}...")
        
        return Command(
            update={
                "messages": [
                    HumanMessage(
                        content=display_content,
                        name="reporter",
                    )
                ]
            },
            goto="__end__",
        )
        
    except Exception as e:
        logger.error(f"生成最终整合失败: {e}")
        error_message = f"抱歉，在生成最终报告时遇到错误: {str(e)}"
        
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
