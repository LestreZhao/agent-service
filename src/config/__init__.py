from .env import (
    # OpenAI 配置
    OPENAI_MODEL,
    OPENAI_BASE_URL,
    OPENAI_API_KEY,
    # Claude 配置
    CLAUDE_MODEL,
    CLAUDE_BASE_URL,
    CLAUDE_API_KEY,
    # Google 配置
    GOOGLE_MODEL,
    GOOGLE_BASE_URL,
    GOOGLE_API_KEY,
    # Qwen 配置
    QWEN_MODEL,
    QWEN_BASE_URL,
    QWEN_API_KEY,
    # DeepSeek 配置
    DEEPSEEK_MODEL,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_API_KEY,
    # Ollama 配置
    OLLAMA_MODEL,
    OLLAMA_BASE_URL,
    OLLAMA_API_KEY,
    # 其他配置
    FIRECRAWL_API_KEY,
    AGENT_FILE_BASE_URL,
    DISABLE_MD_FILE_GENERATION,
)
from .tools import TAVILY_MAX_RESULTS

# Team configuration
TEAM_MEMBERS = ["researcher", "coder", "reporter", "db_analyst", "document_parser", "chart_generator"]  # 已移除browser智能体

__all__ = [
    # OpenAI 配置
    "OPENAI_MODEL",
    "OPENAI_BASE_URL", 
    "OPENAI_API_KEY",
    # Claude 配置
    "CLAUDE_MODEL",
    "CLAUDE_BASE_URL",
    "CLAUDE_API_KEY",
    # Google 配置
    "GOOGLE_MODEL",
    "GOOGLE_BASE_URL",
    "GOOGLE_API_KEY",
    # Qwen 配置
    "QWEN_MODEL",
    "QWEN_BASE_URL",
    "QWEN_API_KEY",
    # DeepSeek 配置
    "DEEPSEEK_MODEL",
    "DEEPSEEK_BASE_URL",
    "DEEPSEEK_API_KEY",
    # Ollama 配置
    "OLLAMA_MODEL",
    "OLLAMA_BASE_URL",
    "OLLAMA_API_KEY",
    # 其他配置
    "TEAM_MEMBERS",
    "TAVILY_MAX_RESULTS",
    "FIRECRAWL_API_KEY",
    "AGENT_FILE_BASE_URL",
    "DISABLE_MD_FILE_GENERATION",
]
