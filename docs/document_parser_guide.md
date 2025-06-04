# FusionAI 文档解析员功能指南

## 概述

FusionAI 文档解析员是一个智能的文档处理智能体，能够处理 PDF 和 Word 文档，提供文档内容解析、分析和问答功能。该智能体完全集成到 FusionAI 的多智能体协作体系中，可由 coordinator、planner 和 supervisor 进行管理调度。

## 功能特性

### 🔍 文档处理能力
- **支持格式**: PDF (.pdf)、Word (.docx、.doc)
- **内容提取**: 智能文本提取和结构化处理
- **文件存储**: 基于 MinIO 的可靠文件存储
- **元数据管理**: 完整的文档信息追踪

### 🧠 智能分析能力
- **内容分析**: 文档结构、主题、关键词识别
- **统计信息**: 字数、行数、段落数等统计
- **内容搜索**: 文档内关键词搜索和上下文提取
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
                                       ┌─────────────────────────────┐
                                       │         MinIO              │
                                       │   文档存储和管理            │
                                       └─────────────────────────────┘
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

参数:
- file: 文档文件 (PDF/Word)

响应:
{
  "success": true,
  "message": "文档上传成功",
  "file_id": "uuid-string",
  "download_url": "/api/documents/{file_id}",
  "document_info": {
    "filename": "example.pdf",
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

发送包含文档相关请求的消息到 `/api/chat/stream`:

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
4. **Document Parser** 执行文档解析和分析
5. **Reporter** 整理最终报告

### 3. 工具使用

文档解析员使用以下工具：

- `get_document_info`: 获取文档完整信息
- `analyze_document_content`: 分析文档内容并提供统计

## 使用示例

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
            "content": f"请对文档 {file_id} 进行深度分析：1) 提取关键信息 2) 识别主要观点 3) 分析文档结构 4) 提供执行建议"
        }
    ]
}
```

## 最佳实践

### 1. 文档管理
- 使用有意义的文件名
- 定期清理不需要的文档
- 备份重要文档的 file_id

### 2. 分析优化
- 提供具体的分析要求
- 对大文档分段处理
- 结合其他智能体能力

### 3. 错误处理
- 检查文档格式支持
- 处理网络连接问题
- 监控存储空间使用

## 故障排除

### 常见问题

1. **MinIO 连接失败**
   - 检查 Docker 是否运行
   - 验证端口是否被占用
   - 确认环境变量配置

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
3. 添加新的 API 端点

---

**注意**: 文档解析员作为 FusionAI 智能体体系的一部分，完全受 coordinator、planner 和 supervisor 的管理调度，确保与其他智能体的协调工作。 