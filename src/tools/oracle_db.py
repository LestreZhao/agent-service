import cx_Oracle
from typing import Dict, Any, List, Optional
from langchain_core.tools import tool
import functools
import logging
from src.config.database import ORACLE_DB_CONFIG, validate_db_config, get_connection_string

logger = logging.getLogger(__name__)

def handle_db_error(func):
    """数据库操作错误处理装饰器"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = f"数据库操作错误: {str(e)}"
            logger.error(error_msg)
            return error_msg
    return wrapper


def get_oracle_connection():
    """获取Oracle数据库连接"""
    if not validate_db_config():
        raise ValueError(
            "数据库连接参数未完整配置，请设置环境变量: "
            "ORACLE_HOST, ORACLE_SERVICE_NAME, ORACLE_USERNAME, ORACLE_PASSWORD"
        )
    
    try:
        dsn = cx_Oracle.makedsn(
            ORACLE_DB_CONFIG["host"], 
            ORACLE_DB_CONFIG["port"], 
            service_name=ORACLE_DB_CONFIG["service_name"]
        )
        connection = cx_Oracle.connect(
            user=ORACLE_DB_CONFIG["username"],
            password=ORACLE_DB_CONFIG["password"],
            dsn=dsn
        )
        logger.info(f"成功连接到Oracle数据库: {get_connection_string()}")
        return connection
    except Exception as e:
        logger.error(f"连接Oracle数据库失败: {str(e)}")
        raise


@tool
@handle_db_error
def get_table_info(table_name: Optional[str] = None, schema_name: Optional[str] = None) -> str:
    """
    获取数据库表信息和字段信息
    
    Args:
        table_name: 表名，如果不提供则列出所有表
        schema_name: 模式名，如果不提供则使用当前用户模式
    
    Returns:
        表信息的字符串描述
    """
    conn = get_oracle_connection()
    cursor = conn.cursor()
    
    try:
        if table_name is None:
            # 获取所有表列表
            if schema_name:
                sql = "SELECT table_name FROM all_tables WHERE owner = :schema ORDER BY table_name"
                cursor.execute(sql, {"schema": schema_name.upper()})
            else:
                sql = "SELECT table_name FROM user_tables ORDER BY table_name"
                cursor.execute(sql)
            
            tables = cursor.fetchall()
            result = "数据库中的表列表:\n"
            for table in tables:
                result += f"- {table[0]}\n"
            return result
        else:
            # 获取指定表的详细信息
            if schema_name:
                sql = """
                SELECT column_name, data_type, data_length, nullable, data_default
                FROM all_tab_columns 
                WHERE table_name = :table_name AND owner = :schema
                ORDER BY column_id
                """
                cursor.execute(sql, {"table_name": table_name.upper(), "schema": schema_name.upper()})
            else:
                sql = """
                SELECT column_name, data_type, data_length, nullable, data_default
                FROM user_tab_columns 
                WHERE table_name = :table_name
                ORDER BY column_id
                """
                cursor.execute(sql, {"table_name": table_name.upper()})
            
            columns = cursor.fetchall()
            if not columns:
                return f"未找到表 {table_name}"
            
            result = f"表 {table_name} 的字段信息:\n"
            result += "字段名 | 数据类型 | 长度 | 可空 | 默认值\n"
            result += "-" * 60 + "\n"
            
            for col in columns:
                column_name, data_type, data_length, nullable, default_value = col
                length_info = f"({data_length})" if data_length else ""
                nullable_info = "是" if nullable == "Y" else "否"
                default_info = str(default_value) if default_value else ""
                result += f"{column_name} | {data_type}{length_info} | {data_length or ''} | {nullable_info} | {default_info}\n"
            
            return result
            
    finally:
        cursor.close()
        conn.close()


@tool
@handle_db_error
def execute_oracle_query(sql: str, fetch_size: int = 100) -> str:
    """
    执行Oracle SQL查询
    
    Args:
        sql: 要执行的SQL查询语句
        fetch_size: 最大返回行数，默认100行
    
    Returns:
        查询结果的字符串格式
    """
    # 安全检查：只允许SELECT语句
    sql_upper = sql.strip().upper()
    if not sql_upper.startswith("SELECT"):
        return "错误：只允许执行SELECT查询语句"
    
    # 检查是否包含危险关键字
    dangerous_keywords = ["DELETE", "UPDATE", "INSERT", "DROP", "CREATE", "ALTER", "TRUNCATE"]
    for keyword in dangerous_keywords:
        if keyword in sql_upper:
            return f"错误：查询中包含不允许的关键字: {keyword}"
    
    conn = get_oracle_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(sql)
        
        # 获取列名
        columns = [desc[0] for desc in cursor.description]
        
        # 获取数据
        rows = cursor.fetchmany(fetch_size)
        
        if not rows:
            return "查询无结果"
        
        # 格式化输出
        result = "查询结果:\n"
        result += " | ".join(columns) + "\n"
        result += "-" * (len(" | ".join(columns)) + 10) + "\n"
        
        for row in rows:
            formatted_row = []
            for item in row:
                if item is None:
                    formatted_row.append("NULL")
                else:
                    formatted_row.append(str(item))
            result += " | ".join(formatted_row) + "\n"
        
        if len(rows) == fetch_size:
            result += f"\n注意：结果已限制为前{fetch_size}行"
        
        return result
        
    finally:
        cursor.close()
        conn.close()


@tool
@handle_db_error
def get_table_relationships(table_name: str, schema_name: Optional[str] = None) -> str:
    """
    获取表的外键关系信息
    
    Args:
        table_name: 表名
        schema_name: 模式名
    
    Returns:
        表关系信息的字符串描述
    """
    conn = get_oracle_connection()
    cursor = conn.cursor()
    
    try:
        if schema_name:
            sql = """
            SELECT 
                a.constraint_name,
                a.column_name,
                c_pk.table_name r_table_name,
                b.column_name r_column_name
            FROM all_cons_columns a
            JOIN all_constraints c ON a.owner = c.owner AND a.constraint_name = c.constraint_name
            JOIN all_constraints c_pk ON c.r_owner = c_pk.owner AND c.r_constraint_name = c_pk.constraint_name
            JOIN all_cons_columns b ON c_pk.owner = b.owner AND c_pk.constraint_name = b.constraint_name
            WHERE c.constraint_type = 'R'
            AND a.table_name = :table_name
            AND a.owner = :schema
            ORDER BY a.constraint_name, a.position
            """
            cursor.execute(sql, {"table_name": table_name.upper(), "schema": schema_name.upper()})
        else:
            sql = """
            SELECT 
                a.constraint_name,
                a.column_name,
                c_pk.table_name r_table_name,
                b.column_name r_column_name
            FROM user_cons_columns a
            JOIN user_constraints c ON a.constraint_name = c.constraint_name
            JOIN user_constraints c_pk ON c.r_constraint_name = c_pk.constraint_name
            JOIN user_cons_columns b ON c_pk.constraint_name = b.constraint_name
            WHERE c.constraint_type = 'R'
            AND a.table_name = :table_name
            ORDER BY a.constraint_name, a.position
            """
            cursor.execute(sql, {"table_name": table_name.upper()})
        
        relationships = cursor.fetchall()
        
        if not relationships:
            return f"表 {table_name} 没有外键关系"
        
        result = f"表 {table_name} 的外键关系:\n"
        result += "约束名 | 本表字段 | 引用表 | 引用字段\n"
        result += "-" * 50 + "\n"
        
        for rel in relationships:
            constraint_name, column_name, r_table_name, r_column_name = rel
            result += f"{constraint_name} | {column_name} | {r_table_name} | {r_column_name}\n"
        
        return result
        
    finally:
        cursor.close()
        conn.close()


# 导出工具
oracle_table_info_tool = get_table_info
oracle_query_tool = execute_oracle_query
oracle_relationships_tool = get_table_relationships 