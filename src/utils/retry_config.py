import time
import logging
from typing import Callable, Any, Optional
from functools import wraps
import google.api_core.exceptions

logger = logging.getLogger(__name__)

def retry_on_api_error(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: tuple = (
        google.api_core.exceptions.InternalServerError,
        google.api_core.exceptions.ServiceUnavailable,
        google.api_core.exceptions.TooManyRequests,
        ConnectionError,
        TimeoutError
    )
):
    """
    为 Google API 调用添加重试装饰器
    
    Args:
        max_retries: 最大重试次数
        base_delay: 基础延迟时间(秒)
        max_delay: 最大延迟时间(秒)
        exponential_base: 指数退避的基数
        exceptions: 需要重试的异常类型
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception: Optional[Exception] = None
            
            for attempt in range(max_retries + 1):
                try:
                    logger.debug(f"尝试调用 {func.__name__}，第 {attempt + 1} 次")
                    result = func(*args, **kwargs)
                    
                    if attempt > 0:
                        logger.info(f"{func.__name__} 在第 {attempt + 1} 次尝试后成功")
                    
                    return result
                    
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(f"{func.__name__} 在 {max_retries + 1} 次尝试后仍然失败")
                        break
                    
                    # 计算延迟时间（指数退避）
                    delay = min(base_delay * (exponential_base ** attempt), max_delay)
                    
                    logger.warning(f"{func.__name__} 第 {attempt + 1} 次调用失败: {e}")
                    logger.info(f"等待 {delay:.1f} 秒后重试...")
                    
                    time.sleep(delay)
                
                except Exception as e:
                    # 对于不在重试列表中的异常，直接抛出
                    logger.error(f"{func.__name__} 遇到不可重试的异常: {e}")
                    raise
            
            # 如果所有重试都失败，抛出最后一个异常
            if last_exception:
                raise last_exception
            
        return wrapper
    return decorator

def get_api_status_message(exception: Exception) -> str:
    """
    根据异常类型返回用户友好的状态消息
    """
    if isinstance(exception, google.api_core.exceptions.InternalServerError):
        return "Google AI 服务暂时不可用，请稍后重试"
    elif isinstance(exception, google.api_core.exceptions.TooManyRequests):
        return "API 调用频率过高，请稍后重试"
    elif isinstance(exception, google.api_core.exceptions.ServiceUnavailable):
        return "AI 服务暂时维护中，请稍后重试"
    elif isinstance(exception, (ConnectionError, TimeoutError)):
        return "网络连接问题，请检查网络后重试"
    else:
        return f"AI 服务异常: {str(exception)}"

# 预定义的重试配置
GOOGLE_API_RETRY_CONFIG = {
    "max_retries": 3,
    "base_delay": 2.0,
    "max_delay": 30.0,
    "exponential_base": 2.0
}

DOCUMENT_ANALYSIS_RETRY_CONFIG = {
    "max_retries": 2,
    "base_delay": 1.0,
    "max_delay": 15.0,
    "exponential_base": 1.5
} 