import os
from typing import Dict, Any

# Oracle数据库连接配置
# 建议通过环境变量或配置文件来设置这些值
ORACLE_DB_CONFIG: Dict[str, Any] = {
    "host": os.getenv("ORACLE_HOST", ""),
    "port": int(os.getenv("ORACLE_PORT", "1521")),
    "service_name": os.getenv("ORACLE_SERVICE_NAME", ""),
    "username": os.getenv("ORACLE_USERNAME", ""),
    "password": os.getenv("ORACLE_PASSWORD", ""),
}

def validate_db_config() -> bool:
    """验证数据库配置是否完整"""
    required_fields = ["host", "service_name", "username", "password"]
    return all(ORACLE_DB_CONFIG.get(field) for field in required_fields)

def get_connection_string() -> str:
    """获取Oracle连接字符串（用于日志记录，不包含密码）"""
    return f"{ORACLE_DB_CONFIG['username']}@{ORACLE_DB_CONFIG['host']}:{ORACLE_DB_CONFIG['port']}/{ORACLE_DB_CONFIG['service_name']}" 