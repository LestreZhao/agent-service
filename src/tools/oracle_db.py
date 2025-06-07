import cx_Oracle
import re
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
    获取数据库表信息和字段信息（包含注释）
    
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
            # 获取所有表列表（包含表注释）
            if schema_name:
                sql = """
                SELECT t.table_name, tc.comments
                FROM all_tables t
                LEFT JOIN all_tab_comments tc ON t.owner = tc.owner AND t.table_name = tc.table_name
                WHERE t.owner = :schema 
                ORDER BY t.table_name
                """
                cursor.execute(sql, {"schema": schema_name.upper()})
            else:
                sql = """
                SELECT t.table_name, tc.comments
                FROM user_tables t
                LEFT JOIN user_tab_comments tc ON t.table_name = tc.table_name
                ORDER BY t.table_name
                """
                cursor.execute(sql)
            
            tables = cursor.fetchall()
            result = "数据库中的表列表:\n"
            result += "表名 | 表注释\n"
            result += "-" * 50 + "\n"
            for table in tables:
                table_name, table_comment = table
                comment = table_comment if table_comment else "无注释"
                result += f"{table_name} | {comment}\n"
            return result
        else:
            # 获取指定表的详细信息（包含字段注释）
            if schema_name:
                sql = """
                SELECT 
                    tc.column_name,
                    tc.data_type,
                    tc.data_length,
                    tc.nullable,
                    tc.data_default,
                    cc.comments
                FROM all_tab_columns tc
                LEFT JOIN all_col_comments cc ON tc.owner = cc.owner 
                    AND tc.table_name = cc.table_name 
                    AND tc.column_name = cc.column_name
                WHERE tc.table_name = :table_name AND tc.owner = :schema
                ORDER BY tc.column_id
                """
                cursor.execute(sql, {"table_name": table_name.upper(), "schema": schema_name.upper()})
            else:
                sql = """
                SELECT 
                    tc.column_name,
                    tc.data_type,
                    tc.data_length,
                    tc.nullable,
                    tc.data_default,
                    cc.comments
                FROM user_tab_columns tc
                LEFT JOIN user_col_comments cc ON tc.table_name = cc.table_name 
                    AND tc.column_name = cc.column_name
                WHERE tc.table_name = :table_name
                ORDER BY tc.column_id
                """
                cursor.execute(sql, {"table_name": table_name.upper()})
            
            columns = cursor.fetchall()
            if not columns:
                return f"未找到表 {table_name}"
            
            # 获取表注释
            if schema_name:
                table_comment_sql = """
                SELECT comments FROM all_tab_comments 
                WHERE table_name = :table_name AND owner = :schema
                """
                cursor.execute(table_comment_sql, {"table_name": table_name.upper(), "schema": schema_name.upper()})
            else:
                table_comment_sql = """
                SELECT comments FROM user_tab_comments 
                WHERE table_name = :table_name
                """
                cursor.execute(table_comment_sql, {"table_name": table_name.upper()})
            
            table_comment_result = cursor.fetchone()
            table_comment = table_comment_result[0] if table_comment_result and table_comment_result[0] else "无注释"
            
            result = f"表 {table_name} 的详细信息:\n"
            result += f"表注释: {table_comment}\n\n"
            result += "字段名 | 数据类型 | 长度 | 可空 | 默认值 | 字段注释\n"
            result += "-" * 80 + "\n"
            
            for col in columns:
                column_name, data_type, data_length, nullable, default_value, column_comment = col
                length_info = f"({data_length})" if data_length else ""
                nullable_info = "是" if nullable == "Y" else "否"
                default_info = str(default_value) if default_value else ""
                comment_info = column_comment if column_comment else "无注释"
                result += f"{column_name} | {data_type}{length_info} | {data_length or ''} | {nullable_info} | {default_info} | {comment_info}\n"
            
            return result
            
    finally:
        cursor.close()
        conn.close()


@tool
@handle_db_error
def execute_oracle_query(sql: str, fetch_size: int = 100) -> str:
    """
    执行Oracle SQL查询（自动添加中文别名）
    
    Args:
        sql: 要执行的SQL查询语句
        fetch_size: 最大返回行数，默认100行
    
    Returns:
        查询结果的字符串格式（包含中文别名）
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
        # 执行原始查询
        cursor.execute(sql)
        
        # 获取列名
        columns = []
        for desc in cursor.description:
            column_name = desc[0]
            columns.append(column_name)
        
        # 获取数据 - 先获取数据，避免后续查询影响结果集
        rows = cursor.fetchmany(fetch_size)
        
        # 检查是否有结果
        if not rows:
            return "查询无结果"
        
        # 使用新的连接获取中文别名，避免影响原始查询
        chinese_columns = []
        try:
            alias_conn = get_oracle_connection()
            alias_cursor = alias_conn.cursor()
            
            for column_name in columns:
                chinese_alias = get_column_chinese_alias(alias_cursor, column_name, sql)
                chinese_columns.append(chinese_alias if chinese_alias else column_name)
            
            alias_cursor.close()
            alias_conn.close()
        except Exception as e:
            logger.debug(f"获取中文别名失败，使用原始列名: {e}")
            chinese_columns = columns.copy()
        
        # 格式化输出（使用中文别名）
        result = "查询结果:\n"
        result += " | ".join(chinese_columns) + "\n"
        result += "-" * (len(" | ".join(chinese_columns)) + 10) + "\n"
        
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
        
        # 添加字段映射说明
        if any(chinese_columns[i] != columns[i] for i in range(len(columns))):
            result += "\n\n字段映射说明:\n"
            for i, (orig, chinese) in enumerate(zip(columns, chinese_columns)):
                if orig != chinese:
                    result += f"{chinese} -> {orig}\n"
        
        return result
        
    except Exception as e:
        logger.error(f"执行SQL查询失败: {str(e)}")
        return f"查询执行错误: {str(e)}"
        
    finally:
        cursor.close()
        conn.close()


def get_column_chinese_alias(cursor, column_name: str, original_sql: str) -> Optional[str]:
    """
    获取字段的中文别名（从注释中获取）
    
    Args:
        cursor: 数据库游标
        column_name: 字段名
        original_sql: 原始SQL语句
    
    Returns:
        中文别名或None
    """
    try:
        # 尝试从SQL中提取表名
        table_names = extract_table_names_from_sql(original_sql)
        
        for table_name in table_names:
            # 首先尝试user_col_comments
            try:
                comment_sql = """
                SELECT comments FROM user_col_comments 
                WHERE table_name = :table_name AND column_name = :column_name
                """
                cursor.execute(comment_sql, {
                    "table_name": table_name.upper(), 
                    "column_name": column_name.upper()
                })
                
                result = cursor.fetchone()
                if result and result[0]:
                    return result[0]
                    
            except Exception:
                pass
            
            # 如果user_col_comments没有结果，尝试all_col_comments
            try:
                comment_sql = """
                SELECT comments FROM all_col_comments 
                WHERE table_name = :table_name AND column_name = :column_name
                AND rownum = 1
                """
                cursor.execute(comment_sql, {
                    "table_name": table_name.upper(), 
                    "column_name": column_name.upper()
                })
                
                result = cursor.fetchone()
                if result and result[0]:
                    return result[0]
            except Exception:
                continue
                    
    except Exception as e:
        logger.debug(f"获取字段中文别名失败: {e}")
    
    return None


def extract_table_names_from_sql(sql: str) -> List[str]:
    """
    从SQL语句中提取表名
    
    Args:
        sql: SQL语句
    
    Returns:
        表名列表
    """
    # 简单的表名提取逻辑
    sql_upper = sql.upper()
    
    # 匹配FROM子句中的表名（支持schema.table格式）
    from_pattern = r'FROM\s+(?:[A-Z_][A-Z0-9_]*\.)?([A-Z_][A-Z0-9_]*)'
    from_matches = re.findall(from_pattern, sql_upper)
    
    # 匹配JOIN子句中的表名（支持schema.table格式）
    join_pattern = r'JOIN\s+(?:[A-Z_][A-Z0-9_]*\.)?([A-Z_][A-Z0-9_]*)'
    join_matches = re.findall(join_pattern, sql_upper)
    
    # 匹配UPDATE语句中的表名
    update_pattern = r'UPDATE\s+(?:[A-Z_][A-Z0-9_]*\.)?([A-Z_][A-Z0-9_]*)'
    update_matches = re.findall(update_pattern, sql_upper)
    
    # 合并所有表名并去重
    table_names = list(set(from_matches + join_matches + update_matches))
    
    return table_names


@tool
@handle_db_error
def get_table_relationships(table_name: str, schema_name: Optional[str] = None) -> str:
    """
    获取表的外键关系信息（包含字段注释）
    
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
                b.column_name r_column_name,
                cc1.comments local_comment,
                cc2.comments ref_comment
            FROM all_cons_columns a
            JOIN all_constraints c ON a.owner = c.owner AND a.constraint_name = c.constraint_name
            JOIN all_constraints c_pk ON c.r_owner = c_pk.owner AND c.r_constraint_name = c_pk.constraint_name
            JOIN all_cons_columns b ON c_pk.owner = b.owner AND c_pk.constraint_name = b.constraint_name
            LEFT JOIN all_col_comments cc1 ON a.owner = cc1.owner 
                AND a.table_name = cc1.table_name AND a.column_name = cc1.column_name
            LEFT JOIN all_col_comments cc2 ON c_pk.owner = cc2.owner 
                AND c_pk.table_name = cc2.table_name AND b.column_name = cc2.column_name
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
                b.column_name r_column_name,
                cc1.comments local_comment,
                cc2.comments ref_comment
            FROM user_cons_columns a
            JOIN user_constraints c ON a.constraint_name = c.constraint_name
            JOIN user_constraints c_pk ON c.r_constraint_name = c_pk.constraint_name
            JOIN user_cons_columns b ON c_pk.constraint_name = b.constraint_name
            LEFT JOIN user_col_comments cc1 ON a.table_name = cc1.table_name 
                AND a.column_name = cc1.column_name
            LEFT JOIN user_col_comments cc2 ON c_pk.table_name = cc2.table_name 
                AND b.column_name = cc2.column_name
            WHERE c.constraint_type = 'R'
            AND a.table_name = :table_name
            ORDER BY a.constraint_name, a.position
            """
            cursor.execute(sql, {"table_name": table_name.upper()})
        
        relationships = cursor.fetchall()
        
        if not relationships:
            return f"表 {table_name} 没有外键关系"
        
        result = f"表 {table_name} 的外键关系:\n"
        result += "约束名 | 本表字段(注释) | 引用表 | 引用字段(注释)\n"
        result += "-" * 80 + "\n"
        
        for rel in relationships:
            constraint_name, column_name, r_table_name, r_column_name, local_comment, ref_comment = rel
            
            # 格式化字段显示（包含注释）
            local_field = f"{column_name}"
            if local_comment:
                local_field += f"({local_comment})"
                
            ref_field = f"{r_column_name}"
            if ref_comment:
                ref_field += f"({ref_comment})"
            
            result += f"{constraint_name} | {local_field} | {r_table_name} | {ref_field}\n"
        
        return result
        
    finally:
        cursor.close()
        conn.close()


@tool
@handle_db_error
def get_table_indexes(table_name: str, schema_name: Optional[str] = None) -> str:
    """
    获取表的索引信息
    
    Args:
        table_name: 表名
        schema_name: 模式名
    
    Returns:
        索引信息的字符串描述
    """
    conn = get_oracle_connection()
    cursor = conn.cursor()
    
    try:
        if schema_name:
            sql = """
            SELECT 
                i.index_name,
                i.index_type,
                i.uniqueness,
                ic.column_name,
                ic.column_position,
                cc.comments
            FROM all_indexes i
            JOIN all_ind_columns ic ON i.owner = ic.index_owner AND i.index_name = ic.index_name
            LEFT JOIN all_col_comments cc ON ic.table_owner = cc.owner 
                AND ic.table_name = cc.table_name AND ic.column_name = cc.column_name
            WHERE i.table_name = :table_name AND i.owner = :schema
            ORDER BY i.index_name, ic.column_position
            """
            cursor.execute(sql, {"table_name": table_name.upper(), "schema": schema_name.upper()})
        else:
            sql = """
            SELECT 
                i.index_name,
                i.index_type,
                i.uniqueness,
                ic.column_name,
                ic.column_position,
                cc.comments
            FROM user_indexes i
            JOIN user_ind_columns ic ON i.index_name = ic.index_name
            LEFT JOIN user_col_comments cc ON ic.table_name = cc.table_name 
                AND ic.column_name = cc.column_name
            WHERE i.table_name = :table_name
            ORDER BY i.index_name, ic.column_position
            """
            cursor.execute(sql, {"table_name": table_name.upper()})
        
        indexes = cursor.fetchall()
        
        if not indexes:
            return f"表 {table_name} 没有索引"
        
        result = f"表 {table_name} 的索引信息:\n"
        result += "索引名 | 类型 | 唯一性 | 字段名(注释) | 位置\n"
        result += "-" * 70 + "\n"
        
        for idx in indexes:
            index_name, index_type, uniqueness, column_name, position, comment = idx
            
            # 格式化字段显示（包含注释）
            field_display = column_name
            if comment:
                field_display += f"({comment})"
            
            uniqueness_display = "唯一" if uniqueness == "UNIQUE" else "非唯一"
            
            result += f"{index_name} | {index_type} | {uniqueness_display} | {field_display} | {position}\n"
        
        return result
        
    finally:
        cursor.close()
        conn.close()


# 导出工具
oracle_table_info_tool = get_table_info
oracle_query_tool = execute_oracle_query
oracle_relationships_tool = get_table_relationships
oracle_indexes_tool = get_table_indexes 