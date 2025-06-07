from .env import (
    # Reasoning LLM
    REASONING_MODEL,
    REASONING_BASE_URL,
    REASONING_API_KEY,
    # Basic LLM
    BASIC_MODEL,
    BASIC_BASE_URL,
    BASIC_API_KEY,
    # Vision-language LLM
    VL_MODEL,
    VL_BASE_URL,
    VL_API_KEY,
    # Google API
    GOOGLE_API_KEY,
    # Other configurations
    CHROME_INSTANCE_PATH,
    FIRECRAWL_API_KEY,
)
from .tools import TAVILY_MAX_RESULTS

# Team configuration - 临时禁用 browser 智能体以避免浏览器启动问题
TEAM_MEMBERS = ["researcher", "coder", "reporter", "db_analyst", "document_parser", "chart_generator", "browser"]  # 添加图表生成智能体和浏览器智能体

__all__ = [
    # Reasoning LLM
    "REASONING_MODEL",
    "REASONING_BASE_URL",
    "REASONING_API_KEY",
    # Basic LLM
    "BASIC_MODEL",
    "BASIC_BASE_URL",
    "BASIC_API_KEY",
    # Vision-language LLM
    "VL_MODEL",
    "VL_BASE_URL",
    "VL_API_KEY",
    # Google API
    "GOOGLE_API_KEY",
    # Other configurations
    "TEAM_MEMBERS",
    "TAVILY_MAX_RESULTS",
    "CHROME_INSTANCE_PATH",
    "FIRECRAWL_API_KEY",
]
