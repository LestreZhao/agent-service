# Oracle数据库工具改进功能说明

## 🎯 改进概述

本次改进主要针对Oracle数据库查询工具，实现了以下核心功能：

1. **中文别名支持** - 查询结果自动显示字段的中文注释作为别名
2. **注释信息获取** - 获取表列表和字段信息时包含完整的注释信息
3. **增强的关系查询** - 外键关系查询包含字段注释
4. **索引信息查询** - 新增表索引信息查询功能

## 🔧 功能详解

### 1. 获取表信息（包含注释）

#### 功能描述
- 获取数据库中所有表的列表，包含表注释
- 获取指定表的详细字段信息，包含字段注释

#### 使用示例
```python
from src.tools.oracle_db import get_table_info

# 获取所有表列表（包含表注释）
tables_info = get_table_info()
print(tables_info)

# 获取指定表的详细信息（包含字段注释）
table_details = get_table_info("USERS")
print(table_details)

# 指定schema获取表信息
schema_tables = get_table_info("USERS", "HR")
print(schema_tables)
```

#### 输出示例
```
数据库中的表列表:
表名 | 表注释
--------------------------------------------------
USERS | 用户信息表
ORDERS | 订单信息表
PRODUCTS | 产品信息表

表 USERS 的详细信息:
表注释: 用户信息表

字段名 | 数据类型 | 长度 | 可空 | 默认值 | 字段注释
--------------------------------------------------------------------------------
ID | NUMBER | | 否 | | 用户ID
NAME | VARCHAR2(100) | 100 | 否 | | 用户姓名
EMAIL | VARCHAR2(255) | 255 | 是 | | 电子邮箱
CREATE_TIME | DATE | | 否 | SYSDATE | 创建时间
```

### 2. 查询结果中文别名

#### 功能描述
- 执行SQL查询时，自动获取字段的中文注释作为列标题
- 提供字段映射说明，显示中文别名与原字段名的对应关系

#### 使用示例
```python
from src.tools.oracle_db import execute_oracle_query

# 执行查询，自动显示中文别名
sql = "SELECT id, name, email FROM users WHERE rownum <= 5"
result = execute_oracle_query(sql, fetch_size=5)
print(result)
```

#### 输出示例
```
查询结果:
用户ID | 用户姓名 | 电子邮箱
----------------------------------------
1 | 张三 | zhangsan@example.com
2 | 李四 | lisi@example.com
3 | 王五 | wangwu@example.com

字段映射说明:
用户ID -> ID
用户姓名 -> NAME
电子邮箱 -> EMAIL
```

### 3. 表关系查询（包含注释）

#### 功能描述
- 获取表的外键关系信息
- 显示本表字段和引用字段的中文注释

#### 使用示例
```python
from src.tools.oracle_db import get_table_relationships

# 获取表的外键关系（包含字段注释）
relationships = get_table_relationships("ORDERS")
print(relationships)

# 指定schema获取关系信息
schema_relationships = get_table_relationships("ORDERS", "SALES")
print(schema_relationships)
```

#### 输出示例
```
表 ORDERS 的外键关系:
约束名 | 本表字段(注释) | 引用表 | 引用字段(注释)
--------------------------------------------------------------------------------
FK_ORDERS_USER | USER_ID(用户ID) | USERS | ID(用户ID)
FK_ORDERS_PRODUCT | PRODUCT_ID(产品ID) | PRODUCTS | ID(产品ID)
```

### 4. 表索引信息查询

#### 功能描述
- 获取表的所有索引信息
- 显示索引类型、唯一性和包含的字段（含注释）

#### 使用示例
```python
from src.tools.oracle_db import get_table_indexes

# 获取表的索引信息
indexes = get_table_indexes("USERS")
print(indexes)

# 指定schema获取索引信息
schema_indexes = get_table_indexes("USERS", "HR")
print(schema_indexes)
```

#### 输出示例
```
表 USERS 的索引信息:
索引名 | 类型 | 唯一性 | 字段名(注释) | 位置
----------------------------------------------------------------------
PK_USERS | NORMAL | 唯一 | ID(用户ID) | 1
IDX_USERS_EMAIL | NORMAL | 唯一 | EMAIL(电子邮箱) | 1
IDX_USERS_NAME | NORMAL | 非唯一 | NAME(用户姓名) | 1
```

## 🛠️ 技术实现

### 中文别名获取机制

1. **SQL解析** - 从SQL语句中提取涉及的表名
2. **注释查询** - 查询`USER_COL_COMMENTS`或`ALL_COL_COMMENTS`视图获取字段注释
3. **别名映射** - 将字段注释作为中文别名显示在查询结果中

### 注释信息集成

- **表注释** - 通过`USER_TAB_COMMENTS`/`ALL_TAB_COMMENTS`视图获取
- **字段注释** - 通过`USER_COL_COMMENTS`/`ALL_COL_COMMENTS`视图获取
- **LEFT JOIN** - 使用左连接确保即使没有注释也能正常显示

### 安全性保障

- **SQL过滤** - 只允许执行SELECT查询语句
- **关键字检查** - 禁止包含危险操作的关键字
- **结果限制** - 默认限制查询结果行数，防止大量数据输出

## 📝 配置要求

### 环境变量
```bash
# Oracle数据库连接配置
ORACLE_HOST=your_oracle_host
ORACLE_PORT=1521
ORACLE_SERVICE_NAME=your_service_name
ORACLE_USERNAME=your_username
ORACLE_PASSWORD=your_password
```

### 数据库权限
确保数据库用户具有以下权限：
- 对目标表的SELECT权限
- 对`USER_TABLES`、`USER_TAB_COLUMNS`等系统视图的SELECT权限
- 对`USER_COL_COMMENTS`、`USER_TAB_COMMENTS`等注释视图的SELECT权限

## 🧪 测试验证

### 运行测试脚本
```bash
# 运行改进功能测试
python test_oracle_improvements.py
```

### 测试内容
1. **表名提取测试** - 验证从SQL语句中正确提取表名
2. **表信息测试** - 验证获取表列表和字段信息（含注释）
3. **中文别名测试** - 验证查询结果显示中文别名
4. **关系查询测试** - 验证外键关系查询（含注释）
5. **索引信息测试** - 验证索引信息查询功能

## 🔍 故障排除

### 常见问题

1. **连接失败**
   - 检查环境变量配置是否正确
   - 确认数据库服务是否正常运行
   - 验证网络连接是否畅通

2. **权限不足**
   - 确认用户是否有足够的查询权限
   - 检查是否能访问系统视图

3. **中文显示异常**
   - 确认数据库字符集配置
   - 检查客户端编码设置

4. **注释获取失败**
   - 确认表和字段是否有注释
   - 检查注释视图的访问权限

### 调试建议

1. **启用调试日志**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **单独测试功能**
   - 先测试基本连接功能
   - 逐步测试各个改进功能

3. **检查SQL语句**
   - 在数据库客户端直接执行生成的SQL
   - 验证查询结果是否符合预期

## 📚 相关文档

- [Oracle数据库工具原始文档](src/tools/oracle_db.py)
- [数据库配置文档](src/config/database.py)
- [FusionAI项目文档](README.md)

---

*此文档描述了Oracle数据库工具的改进功能，包括中文别名支持和注释信息获取。如有问题请参考故障排除部分或联系开发团队。* 