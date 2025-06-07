"""
Server script for running the FusionAI API.

This module provides a simple script to start the FusionAI FastAPI server
with uvicorn.
"""

import logging
import os
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

def display_model_configuration():
    """显示当前模型配置信息"""
    logger.info("=" * 60)
    logger.info("FusionAI 模型配置信息")
    logger.info("=" * 60)
    
    # 显示环境配置
    logger.info("环境配置:")
    logger.info(f"  REASONING_MODEL: {os.getenv('REASONING_MODEL', '未设置')}")
    logger.info(f"  BASIC_MODEL: {os.getenv('BASIC_MODEL', '未设置')}")
    logger.info(f"  VL_MODEL: {os.getenv('VL_MODEL', '未设置')}")
    
    # 显示API Key状态
    logger.info("API Key状态:")
    logger.info(f"  GOOGLE_API_KEY: {'✓ 已配置' if os.getenv('GOOGLE_API_KEY') else '✗ 未配置'}")
    logger.info(f"  REASONING_API_KEY: {'✓ 已配置' if os.getenv('REASONING_API_KEY') else '✗ 未配置'}")
    logger.info(f"  BASIC_API_KEY: {'✓ 已配置' if os.getenv('BASIC_API_KEY') else '✗ 未配置'}")
    logger.info(f"  VL_API_KEY: {'✓ 已配置' if os.getenv('VL_API_KEY') else '✗ 未配置'}")
    
    # 尝试加载LLM实例并显示实际类型
    try:
        from src.agents.llm import get_llm_by_type
        
        logger.info("LLM实例类型:")
        
        # Reasoning LLM
        try:
            reasoning_llm = get_llm_by_type('reasoning')
            provider = type(reasoning_llm).__name__
            if 'Google' in provider:
                provider_name = "Google Gemini"
            elif 'DeepSeek' in provider:
                provider_name = "DeepSeek"
            elif 'OpenAI' in provider:
                provider_name = "OpenAI兼容"
            else:
                provider_name = provider
            logger.info(f"  Reasoning: {provider_name} ({provider})")
        except Exception as e:
            logger.error(f"  Reasoning: 加载失败 - {e}")
        
        # Basic LLM
        try:
            basic_llm = get_llm_by_type('basic')
            provider = type(basic_llm).__name__
            if 'Google' in provider:
                provider_name = "Google Gemini"
            elif 'DeepSeek' in provider:
                provider_name = "DeepSeek"
            elif 'OpenAI' in provider:
                provider_name = "OpenAI兼容"
            else:
                provider_name = provider
            logger.info(f"  Basic: {provider_name} ({provider})")
        except Exception as e:
            logger.error(f"  Basic: 加载失败 - {e}")
        
        # Vision LLM
        try:
            vision_llm = get_llm_by_type('vision')
            provider = type(vision_llm).__name__
            if 'Google' in provider:
                provider_name = "Google Gemini"
            elif 'DeepSeek' in provider:
                provider_name = "DeepSeek"
            elif 'OpenAI' in provider:
                provider_name = "OpenAI兼容"
            else:
                provider_name = provider
            logger.info(f"  Vision: {provider_name} ({provider})")
        except Exception as e:
            logger.error(f"  Vision: 加载失败 - {e}")
            
    except Exception as e:
        logger.error(f"无法加载LLM模块: {e}")
    
    logger.info("=" * 60)

if __name__ == "__main__":
    logger.info("Starting FusionAI API server")
    
    # 显示模型配置
    display_model_configuration()
    
    uvicorn.run(
        "src.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
