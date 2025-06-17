import os
from dotenv import load_dotenv

# Load environment variables (.env file takes precedence over system env vars)
load_dotenv(override=True)

# OpenAI configuration
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Claude configuration
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
CLAUDE_BASE_URL = os.getenv("CLAUDE_BASE_URL")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

# Google configuration
GOOGLE_MODEL = os.getenv("GOOGLE_MODEL", "gemini-2.5-pro-preview-06-05")
GOOGLE_BASE_URL = os.getenv("GOOGLE_BASE_URL")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Qwen configuration
QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen2-7b-instruct")
QWEN_BASE_URL = os.getenv("QWEN_BASE_URL")
QWEN_API_KEY = os.getenv("QWEN_API_KEY")

# DeepSeek configuration
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# Ollama configuration
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")

# Crawler configuration
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

# File server configuration
AGENT_FILE_BASE_URL = os.getenv("AGENT_FILE_BASE_URL", "https://agentfile.fusiontech.cn")

# MD file generation control
DISABLE_MD_FILE_GENERATION = os.getenv("DISABLE_MD_FILE_GENERATION", "false").lower() in ["true", "1", "yes"]
