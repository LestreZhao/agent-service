import logging
import sys
import os
from datetime import datetime

def setup_logging(enable_file_logging: bool = False):
    """配置详细的日志记录"""
    
    # 设置日志格式
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s'
    
    # 配置处理器
    handlers = [
        # 输出到控制台
        logging.StreamHandler(sys.stdout)
    ]
    
    # 如果需要文件日志，创建目录和文件处理器
    if enable_file_logging:
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        handlers.append(
            logging.FileHandler(
                os.path.join(log_dir, f"document_analysis_{datetime.now().strftime('%Y%m%d')}.log"),
                encoding='utf-8'
            )
        )
    
    # 配置根日志记录器
    logging.basicConfig(
        level=logging.INFO,  # 改为INFO级别，减少日志噪音
        format=log_format,
        handlers=handlers
    )
    
    # 设置特定模块的日志级别
    logging.getLogger('src.tools.document_tool').setLevel(logging.DEBUG)
    logging.getLogger('src.tools.document_parser').setLevel(logging.DEBUG)
    
    # 减少其他库的日志噪音
    logging.getLogger('minio').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    
    if enable_file_logging:
        print(f"日志记录已配置 - 输出到控制台和文件")
    else:
        print(f"日志记录已配置 - 仅输出到控制台")

# 在导入时自动配置日志（默认只输出到控制台）
setup_logging(enable_file_logging=False) 