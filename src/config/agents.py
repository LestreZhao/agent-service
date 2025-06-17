from typing import Literal

# Define available LLM providers
LLMProvider = Literal["openai", "claude", "google", "qwen", "deepseek", "ollama"]

# Define agent-LLM provider mapping
AGENT_LLM_MAP: dict[str, LLMProvider] = {
    "coordinator": "qwen",      # 任务协调员 - 使用OpenAI
    "planner": "qwen",          # 任务规划员 - 使用OpenAI
    "supervisor": "qwen",       # 任务监督员 - 使用OpenAI
    "researcher": "qwen",       # 研究员 - 使用OpenAI
    "coder": "qwen",         # 程序员 - 使用DeepSeek
    "reporter": "openai",        # 报告员 - 使用OpenAI
    "db_analyst": "google",    # 数据库分析师 - 使用DeepSeek
    "document_parser": "openai", # 文档解析员 - 使用OpenAI
    "chart_generator": "openai", # 图表生成员 - 使用OpenAI
}
