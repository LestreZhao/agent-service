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
    """显示模型配置信息"""
    try:
        from src.utils.startup_info import startup_display
        startup_display.display_startup_info()
    except ImportError as e:
        logger.error(f"无法导入启动信息模块: {e}")
    except Exception as e:
        logger.error(f"显示启动信息时出错: {e}")


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
