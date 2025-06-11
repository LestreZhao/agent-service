import os
from dotenv import load_dotenv

# Load environment variables (.env file takes precedence over system env vars)
load_dotenv(override=True)

# Reasoning LLM configuration (for complex reasoning tasks)
REASONING_MODEL = os.getenv("REASONING_MODEL", "gpt-4o")
REASONING_BASE_URL = os.getenv("REASONING_BASE_URL")
REASONING_API_KEY = os.getenv("REASONING_API_KEY")

# Non-reasoning LLM configuration (for straightforward tasks)
BASIC_MODEL = os.getenv("BASIC_MODEL", "gpt-4o-mini")
BASIC_BASE_URL = os.getenv("BASIC_BASE_URL")
BASIC_API_KEY = os.getenv("BASIC_API_KEY")

# Vision-language LLM configuration (for tasks requiring visual understanding)
VL_MODEL = os.getenv("VL_MODEL", "gpt-4o")
VL_BASE_URL = os.getenv("VL_BASE_URL")
VL_API_KEY = os.getenv("VL_API_KEY")

# Google API configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")



# Crawler configuration
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

# File server configuration
AGENT_FILE_BASE_URL = os.getenv("AGENT_FILE_BASE_URL", "https://agentfile.fusiontech.cn")

# MD file generation control
DISABLE_MD_FILE_GENERATION = os.getenv("DISABLE_MD_FILE_GENERATION", "false").lower() in ["true", "1", "yes"]
