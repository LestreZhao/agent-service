from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from typing import Optional, Dict, Any
import logging

from src.config import (
    OPENAI_MODEL, OPENAI_BASE_URL, OPENAI_API_KEY,
    CLAUDE_MODEL, CLAUDE_BASE_URL, CLAUDE_API_KEY,
    GOOGLE_MODEL, GOOGLE_BASE_URL, GOOGLE_API_KEY,
    QWEN_MODEL, QWEN_BASE_URL, QWEN_API_KEY,
    DEEPSEEK_MODEL, DEEPSEEK_BASE_URL, DEEPSEEK_API_KEY,
    OLLAMA_MODEL, OLLAMA_BASE_URL, OLLAMA_API_KEY,
)
from src.config.agents import LLMProvider

logger = logging.getLogger(__name__)

# 厂商配置映射
PROVIDER_CONFIGS = {
    "openai": {
        "model": OPENAI_MODEL,
        "base_url": OPENAI_BASE_URL,
        "api_key": OPENAI_API_KEY,
        "llm_class": ChatOpenAI,
        "api_key_param": "api_key",
        "base_url_param": "base_url"
    },
    "claude": {
        "model": CLAUDE_MODEL,
        "base_url": CLAUDE_BASE_URL,
        "api_key": CLAUDE_API_KEY,
        "llm_class": ChatAnthropic,  # Claude使用专门的Anthropic接口
        "api_key_param": "api_key",
        "base_url_param": "base_url"
    },
    "google": {
        "model": GOOGLE_MODEL,
        "base_url": GOOGLE_BASE_URL,
        "api_key": GOOGLE_API_KEY,
        "llm_class": ChatGoogleGenerativeAI,
        "api_key_param": "google_api_key",
        "base_url_param": None  # Google不使用base_url
    },
    "qwen": {
        "model": QWEN_MODEL,
        "base_url": QWEN_BASE_URL,
        "api_key": QWEN_API_KEY,
        "llm_class": ChatOpenAI,  # 通义千问使用OpenAI兼容接口
        "api_key_param": "api_key",
        "base_url_param": "base_url"
    },
    "deepseek": {
        "model": DEEPSEEK_MODEL,
        "base_url": DEEPSEEK_BASE_URL,
        "api_key": DEEPSEEK_API_KEY,
        "llm_class": ChatDeepSeek,
        "api_key_param": "api_key",
        "base_url_param": "api_base"  # DeepSeek使用api_base
    },
    "ollama": {
        "model": OLLAMA_MODEL,
        "base_url": OLLAMA_BASE_URL,
        "api_key": OLLAMA_API_KEY,
        "llm_class": ChatOpenAI,  # Ollama使用OpenAI兼容接口
        "api_key_param": "api_key",
        "base_url_param": "base_url"
    }
}


def create_llm_by_provider(
    provider: LLMProvider,
    temperature: float = 0.0,
    **kwargs
) -> ChatOpenAI | ChatDeepSeek | ChatGoogleGenerativeAI | ChatAnthropic:
    """
    根据厂商名称创建LLM实例
    
    Args:
        provider: 厂商名称
        temperature: 温度参数
        **kwargs: 其他参数
        
    Returns:
        LLM实例
    """
    if provider not in PROVIDER_CONFIGS:
        raise ValueError(f"不支持的厂商: {provider}. 支持的厂商: {list(PROVIDER_CONFIGS.keys())}")
    
    config = PROVIDER_CONFIGS[provider]
    llm_class = config["llm_class"]
    
    # 构建LLM参数
    llm_kwargs = {
        "model": config["model"],
        "temperature": temperature,
        **kwargs
    }
    
    # 处理API密钥
    api_key_param = config["api_key_param"]
    api_key = config["api_key"]
    if api_key_param and api_key:
        llm_kwargs[api_key_param] = api_key
    
    # 处理Base URL
    base_url_param = config["base_url_param"]
    base_url = config["base_url"]
    if base_url_param and base_url:
        llm_kwargs[base_url_param] = base_url
    
    logger.info(f"创建 {provider} LLM实例: {config['model']}")
    return llm_class(**llm_kwargs)


# 缓存LLM实例
_llm_cache: Dict[LLMProvider, Any] = {}


def get_llm_by_provider(provider: LLMProvider) -> ChatOpenAI | ChatDeepSeek | ChatGoogleGenerativeAI | ChatAnthropic:
    """
    根据厂商获取LLM实例，支持缓存
    
    Args:
        provider: 厂商名称
        
    Returns:
        LLM实例
    """
    if provider in _llm_cache:
        return _llm_cache[provider]
    
    llm = create_llm_by_provider(provider)
    _llm_cache[provider] = llm
    return llm


def get_provider_config(provider: LLMProvider) -> Dict[str, Any]:
    """
    获取厂商配置信息
    
    Args:
        provider: 厂商名称
        
    Returns:
        厂商配置信息
    """
    if provider not in PROVIDER_CONFIGS:
        raise ValueError(f"不支持的厂商: {provider}")
    
    config = PROVIDER_CONFIGS[provider]
    return {
        "provider": provider,
        "model": config["model"],
        "llm_class": config["llm_class"].__name__,
        "base_url": config["base_url"],
        "api_key_configured": bool(config["api_key"]),
        "api_key_param": config["api_key_param"],
        "base_url_param": config["base_url_param"]
    }


def list_supported_providers() -> Dict[str, Dict[str, Any]]:
    """
    列出所有支持的厂商配置
    
    Returns:
        厂商配置信息
    """
    result = {}
    for provider in PROVIDER_CONFIGS.keys():
        result[provider] = get_provider_config(provider)
    return result


# 向后兼容的函数
def create_openai_llm(
    model: str,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    temperature: float = 0.0,
    **kwargs,
) -> ChatOpenAI:
    """创建OpenAI LLM实例（向后兼容）"""
    llm_kwargs = {"model": model, "temperature": temperature, **kwargs}
    if base_url:
        llm_kwargs["base_url"] = base_url
    if api_key:
        llm_kwargs["api_key"] = api_key
    return ChatOpenAI(**llm_kwargs)


def create_deepseek_llm(
    model: str,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    temperature: float = 0.0,
    **kwargs,
) -> ChatDeepSeek:
    """创建DeepSeek LLM实例（向后兼容）"""
    llm_kwargs = {"model": model, "temperature": temperature, **kwargs}
    if base_url:
        llm_kwargs["api_base"] = base_url
    if api_key:
        llm_kwargs["api_key"] = api_key
    return ChatDeepSeek(**llm_kwargs)


def create_google_llm(
    model: str,
    api_key: Optional[str] = None,
    temperature: float = 0.0,
    **kwargs,
) -> ChatGoogleGenerativeAI:
    """创建Google LLM实例（向后兼容）"""
    llm_kwargs = {"model": model, "temperature": temperature, **kwargs}
    if api_key:
        llm_kwargs["google_api_key"] = api_key
    return ChatGoogleGenerativeAI(**llm_kwargs)


if __name__ == "__main__":
    # 测试所有厂商配置
    print("🔍 厂商配置测试:")
    providers = list_supported_providers()
    for provider, config in providers.items():
        print(f"  {provider:<10}: {config['model']:<30} | {config['llm_class']:<25} | API Key: {'✅' if config['api_key_configured'] else '❌'}")
    
    # 测试LLM创建
    print(f"\n🚀 测试LLM创建:")
    for provider in ["openai", "deepseek"]:  # 只测试有配置的厂商
        try:
            config = get_provider_config(provider)
            if config["api_key_configured"]:
                llm = get_llm_by_provider(provider)
                print(f"  ✅ {provider}: {type(llm).__name__} - {config['model']}")
            else:
                print(f"  ❌ {provider}: API Key未配置")
        except Exception as e:
            print(f"  ❌ {provider}: 创建失败 - {e}")
