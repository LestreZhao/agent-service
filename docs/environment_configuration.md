# 环境变量配置指南

## 概述
本文档说明FusionAI项目中的所有环境变量配置。

## 配置文件
1. 复制环境变量模板：`cp .env.example .env`
2. 编辑 `.env` 文件，填入实际配置值

## 环境变量说明

### LLM API 配置

#### 推理模型配置 (复杂推理任务)
```bash
REASONING_MODEL=gpt-4o                    # 推理模型名称
REASONING_BASE_URL=                       # API基础URL (可选)
REASONING_API_KEY=your_reasoning_api_key  # API密钥
```

#### 基础模型配置 (简单任务)
```bash
BASIC_MODEL=gpt-4o-mini                   # 基础模型名称
BASIC_BASE_URL=                           # API基础URL (可选)
BASIC_API_KEY=your_basic_api_key         # API密钥
```

#### 视觉语言模型配置
```bash
VL_MODEL=gpt-4o                          # 视觉模型名称
VL_BASE_URL=                             # API基础URL (可选)
VL_API_KEY=your_vision_api_key           # API密钥
```

#### Google API 配置
```bash
GOOGLE_API_KEY=your_google_api_key       # Google API密钥
```

### 工具和服务配置



#### 爬虫服务配置
```bash
FIRECRAWL_API_KEY=your_firecrawl_api_key # FireCrawl API密钥
```

#### 文件服务器配置 (重要)
```bash
AGENT_FILE_BASE_URL=https://agentfile.fusiontech.cn  # Linux系统文件访问域名
```

**说明**：
- 在Linux系统中，生成的文件链接会使用此域名
- 在macOS/Windows系统中，使用本地文件路径
- 默认值：`https://agentfile.fusiontech.cn`

### 数据库配置 (可选)

#### Oracle 数据库
```bash
ORACLE_HOST=localhost                    # 数据库主机
ORACLE_PORT=1521                        # 数据库端口
ORACLE_SERVICE_NAME=XEPDB1              # 服务名
ORACLE_USERNAME=your_username           # 用户名
ORACLE_PASSWORD=your_password           # 密码
```

#### MinIO 对象存储 (可选)
```bash
MINIO_ENDPOINT=localhost:9000            # MinIO服务地址
MINIO_ACCESS_KEY=your_access_key        # 访问密钥
MINIO_SECRET_KEY=your_secret_key        # 秘密密钥
MINIO_BUCKET_NAME=fusion-agent          # 存储桶名称
```

## 配置示例

### 开发环境示例
```bash
# 基础LLM配置
REASONING_API_KEY=sk-xxxxxxxxxxxxxxxx
BASIC_API_KEY=sk-xxxxxxxxxxxxxxxx
VL_API_KEY=sk-xxxxxxxxxxxxxxxx
GOOGLE_API_KEY=AIxxxxxxxxxxxxxxxx

# 文件服务器配置
AGENT_FILE_BASE_URL=https://agentfile.fusiontech.cn

# 浏览器配置

```

### 生产环境示例
```bash
# 生产环境LLM配置
REASONING_MODEL=gpt-4o
REASONING_API_KEY=prod-sk-xxxxxxxxxxxxxxxx

# 生产文件服务器
AGENT_FILE_BASE_URL=https://files.production.fusiontech.cn
```

## 最新变更 (v1.1)

### 新增配置项
- **AGENT_FILE_BASE_URL**: 文件服务器域名配置
  - 影响范围：Linux系统下的文件链接生成
  - 默认值：`https://agentfile.fusiontech.cn`
  - 用途：在Linux环境中，所有生成的文件链接都会使用此域名前缀

### 配置优化
- 文件链接生成现在根据操作系统自动选择格式
- Linux: 使用HTTP URL格式 (`{AGENT_FILE_BASE_URL}/path/to/file`)  
- macOS/Windows: 使用本地文件路径格式

## 故障排除

### 文件链接访问问题
1. 检查 `AGENT_FILE_BASE_URL` 配置是否正确
2. 确认文件服务器是否可访问
3. 验证文件路径是否存在

### API密钥问题
1. 确认所有必需的API密钥已正确配置
2. 检查API密钥格式和权限
3. 验证网络连接和API服务状态 