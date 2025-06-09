from typing import Literal

# Define available LLM types
LLMType = Literal["basic", "reasoning", "vision"]

# Define agent-LLM mapping
AGENT_LLM_MAP: dict[str, LLMType] = {
    "coordinator": "reasoning",  # 协调默认使用basic llm
    "planner": "reasoning",  # 计划默认使用basic llm
    "supervisor": "reasoning",  # 决策使用basic llm
    "researcher": "reasoning",  # 简单搜索任务使用basic llm
    "coder": "basic",  # 编程任务使用basic llm

    "reporter": "basic",  # 编写报告使用basic llm
    "db_analyst": "basic",  # 数据库分析使用basic llm
    "document_parser": "basic",  # 文档解析使用basic llm
    "chart_generator": "basic",  # 图表生成使用basic llm
}
