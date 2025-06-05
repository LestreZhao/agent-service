# FusionAI 文档解析员功能指南

## 概述

FusionAI 文档解析员是一个智能的文档处理智能体，能够处理 PDF 和 Word 文档，提供文档内容解析、分析和问答功能。该智能体完全集成到 FusionAI 的多智能体协作体系中，可由 coordinator、planner 和 supervisor 进行管理调度。

## 功能特性

### 🔍 文档处理能力
- **支持格式**: PDF (.pdf)、Word (.docx、.doc)
- **智能URL处理**: 自动从任何可访问的URL下载并解析文档
- **内容提取**: 智能文本提取和结构化处理
- **文件存储**: 基于 MinIO 的可靠文件存储
- **元数据管理**: 完整的文档信息追踪

### 🧠 智能分析能力
- **内容分析**: 文档结构、主题、关键词识别
- **统计信息**: 字数、行数、段落数等统计
- **需求导向分析**: 根据用户具体需求进行针对性分析
- **问答功能**: 基于文档内容的智能问答

### 🤝 智能体协作
- **协调管理**: 由 coordinator 统一调度
- **计划集成**: 可纳入 planner 的任务规划
- **监督控制**: 受 supervisor 监督和路由
- **结果反馈**: 向其他智能体提供分析结果

## 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Coordinator   │───▶│    Planner      │───▶│   Supervisor    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│   Researcher    │     Coder       │   DB Analyst    │Document Parser  │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┘
                                                       │
                                                       ▼
                                            ┌─────────────────────┐
                                            │  智能文档解析器     │
                                            │  • URL自动下载      │
                                            │  • 内容智能提取     │
                                            │  • 需求导向分析     │
                                            └─────────────────────┘
```

## 环境设置

### 1. 安装依赖
```bash
# 已包含在项目依赖中
uv add minio PyPDF2 python-docx python-multipart aiofiles
```

### 2. 启动 MinIO 服务
```bash
# 使用提供的脚本
./scripts/setup_minio.sh

# 或手动启动 Docker 容器
docker run -d \
  --name fusionai-minio \
  -p 9000:9000 \
  -p 9001:9001 \
  -v ./data/minio:/data \
  -e "MINIO_ROOT_USER=minioadmin" \
  -e "MINIO_ROOT_PASSWORD=minioadmin" \
  minio/minio server /data --console-address ":9001"
```

### 3. 环境变量配置
在 `.env` 文件中添加：
```env
# MinIO 配置
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=fusionai-documents
MINIO_SECURE=false
```

## API 接口

### 文档上传
```http
POST /api/documents/upload
Content-Type: multipart/form-data

文件：document.pdf

响应:
{
  "success": true,
  "message": "文档上传成功",
  "file_id": "uuid-string",
  "download_url": "/api/documents/uuid-string",
  "document_info": {
    "filename": "document.pdf",
    "file_type": ".pdf",
    "file_size": 1024,
    "content_length": 2048,
    "uploaded_at": "2024-01-01T00:00:00"
  }
}
```

### 获取文档信息
```http
GET /api/documents/{file_id}?include_content=true

响应:
{
  "success": true,
  "data": {
    "file_id": "uuid-string",
    "filename": "example.pdf",
    "file_type": ".pdf",
    "content": "文档完整内容...",
    "content_length": 2048,
    "file_size": 1024,
    "uploaded_at": "2024-01-01T00:00:00",
    "parsed_at": "2024-01-01T00:00:01"
  }
}
```

### 文档分析
```http
POST /api/documents/{file_id}/analyze
Content-Type: application/json

{
  "analysis_request": "请分析文档的主要内容和结构"
}

响应:
{
  "success": true,
  "data": {
    "file_id": "uuid-string",
    "filename": "example.pdf",
    "content_length": 2048,
    "word_count": 300,
    "line_count": 50,
    "paragraph_count": 10,
    "content_preview": "文档内容预览...",
    "analyzed_at": "2024-01-01T00:00:02"
  }
}
```

### 下载原始文档
```http
GET /api/documents/{file_id}/download

响应: 文件流下载
```

### 删除文档
```http
DELETE /api/documents/{file_id}

响应:
{
  "success": true,
  "message": "文档删除成功",
  "file_id": "uuid-string"
}
```

## 智能体使用

### 1. 通过聊天接口使用

#### URL文档分析
发送包含文档URL和分析需求的消息到 `/api/chat/stream`:

```json
{
  "messages": [
    {
      "role": "user",
      "content": "请分析这个文档 https://example.com/document.pdf，总结主要内容和关键观点"
    }
  ]
}
```

#### 已上传文档分析
```json
{
  "messages": [
    {
      "role": "user",
      "content": "请分析文档ID为 {file_id} 的内容，提取主要观点"
    }
  ]
}
```

### 2. 智能体工作流

1. **Coordinator** 接收用户请求，识别文档处理需求
2. **Planner** 制定包含文档分析的执行计划
3. **Supervisor** 将任务路由给 Document Parser
4. **Document Parser** 执行文档解析和分析：
   - 如果是URL：自动下载文档
   - 如果是文件ID：从存储系统获取
   - 根据用户需求进行内容分析
5. **Reporter** 整理最终报告

### 3. 工具使用

文档解析员使用核心工具：

- `analyze_document_content`: 智能文档分析工具
  - 支持URL自动下载和解析
  - 支持文件ID访问存储文档
  - 根据用户需求进行分析

## 使用示例

### URL文档分析
```python
# 通过聊天接口分析在线文档
chat_request = {
    "messages": [
        {
            "role": "user",
            "content": "请分析这个PDF文档 https://example.com/report.pdf，重点关注其中的数据分析部分"
        }
    ]
}
```

### 基本文档分析
```python
# 通过API上传文档
response = requests.post(
    "http://localhost:8000/api/documents/upload",
    files={"file": open("document.pdf", "rb")}
)
file_id = response.json()["file_id"]

# 通过聊天接口分析
chat_request = {
    "messages": [
        {
            "role": "user", 
            "content": f"请分析文档 {file_id}，总结主要内容"
        }
    ]
}
```

### 高级分析请求
```python
chat_request = {
    "messages": [
        {
            "role": "user",
            "content": "请对这个文档 https://example.com/contract.pdf 进行深度分析：1) 提取关键条款 2) 识别风险点 3) 分析合同结构 4) 提供执行建议"
        }
    ]
}
```

## 核心优势

### 1. 智能URL处理
- **自动下载**: 支持任何可访问的HTTP/HTTPS URL
- **格式识别**: 自动检测PDF、Word等文档格式
- **内容解析**: 智能提取文档文本内容

### 2. 需求导向分析
- **用户需求理解**: 根据用户具体要求进行分析
- **定制化处理**: 针对不同分析需求提供相应洞察
- **智能总结**: 生成符合用户期望的分析报告

### 3. 灵活输入支持
- **URL输入**: 直接处理文档链接
- **文件ID**: 访问已上传的文档
- **混合使用**: 在同一会话中处理多种输入类型

## 最佳实践

### 1. URL使用建议
- 确保URL可公开访问
- 使用直接的文档链接
- 避免需要认证的私有链接

### 2. 分析需求表达
- 明确具体的分析要求
- 提供分析的重点和方向
- 结合业务场景说明需求

### 3. 性能优化
- 对大文档进行分段分析
- 结合其他智能体能力
- 合理利用缓存机制

## 故障排除

### 常见问题

1. **URL访问失败**
   - 检查URL是否可公开访问
   - 验证网络连接状态
   - 确认文档格式支持

2. **文档解析失败**
   - 验证文件格式支持
   - 检查文件是否损坏
   - 确认文件大小限制

3. **智能体无响应**
   - 检查 LLM 配置
   - 验证 API 密钥
   - 查看日志错误信息

### 日志查看
```bash
# 查看应用日志
uv run python -m src.api.app

# 查看 MinIO 日志
docker logs fusionai-minio
```

## 开发扩展

### 添加新文档格式
1. 在 `DocumentParser` 类中添加解析方法
2. 更新 `parse_document` 方法
3. 添加相应的内容类型映射

### 集成新分析功能
1. 扩展分析工具函数
2. 更新智能体提示词
3. 优化分析算法

---

**注意**: 文档解析员作为 FusionAI 智能体体系的一部分，完全受 coordinator、planner 和 supervisor 的管理调度，确保与其他智能体的协调工作。新的URL处理能力使得文档分析更加灵活和强大。 