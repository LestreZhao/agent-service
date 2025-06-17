# FusionAI 环境配置指南

## 概述

系统现在采用**按厂商配置**的方式管理LLM，每个厂商都有独立的配置参数。请按照以下指南配置您的`.env`文件。

## 配置文件创建

在项目根目录创建`.env`文件：

```bash
touch .env
```

## 完整配置模板

将以下内容复制到您的`.env`文件中，并替换为您的实际API密钥：

```env
# =============================================================================
# FusionAI 智能体系统 - 环境配置
# =============================================================================

# OpenAI 配置
OPENAI_MODEL=gpt-4o
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_API_KEY=sk-your-openai-api-key-here

# Anthropic Claude 配置
CLAUDE_MODEL=claude-3-5-sonnet-20241022
CLAUDE_BASE_URL=https://api.anthropic.com
CLAUDE_API_KEY=sk-ant-your-claude-api-key-here

# Google Gemini 配置
GOOGLE_MODEL=gemini-2.5-pro-preview-06-05
# GOOGLE_BASE_URL=  # Google不需要base_url
GOOGLE_API_KEY=your-google-api-key-here

# 阿里通义千问配置
QWEN_MODEL=qwen2-7b-instruct
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_API_KEY=sk-your-qwen-api-key-here

# DeepSeek 配置
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_API_KEY=sk-your-deepseek-api-key-here

# Ollama 本地模型配置
OLLAMA_MODEL=llama3.1:8b
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_API_KEY=ollama  # Ollama通常不需要API密钥

# =============================================================================
# 其他服务配置
# =============================================================================

# 爬虫服务配置
FIRECRAWL_API_KEY=fc-your-firecrawl-api-key-here

# 文件服务配置
AGENT_FILE_BASE_URL=https://agentfile.fusiontech.cn

# 系统配置
DISABLE_MD_FILE_GENERATION=false
```

## 智能体厂商分配

当前系统中各智能体使用的厂商配置（在`src/config/agents.py`中定义）：

- **OpenAI厂商**：
  - `coordinator` (任务协调员)
  - `planner` (任务规划员)
  - `supervisor` (任务监督员)
  - `researcher` (研究员)
  - `reporter` (报告员)
  - `document_parser` (文档解析员)
  - `chart_generator` (图表生成员)

- **DeepSeek厂商**：
  - `coder` (程序员)
  - `db_analyst` (数据库分析师)

## 配置说明

### 必要配置

根据智能体厂商分配，您至少需要配置：

1. **OpenAI** - 系统核心智能体使用
2. **DeepSeek** - 编程和数据分析任务使用

### 可选配置

其他厂商可以根据需要配置：

- **Claude** - 如果您想使用Anthropic的模型
- **Google Gemini** - 如果您想使用Google的模型
- **Qwen** - 如果您想使用阿里的通义千问
- **Ollama** - 如果您想使用本地部署的模型

### 配置参数说明

每个厂商有以下配置参数：

- `XXX_MODEL`: 模型名称
- `XXX_BASE_URL`: API基础URL（可选，有默认值）
- `XXX_API_KEY`: API密钥

## 快速开始

### 最小配置

如果您只想快速开始，只需配置OpenAI和DeepSeek：

```env
# 最小配置
OPENAI_MODEL=gpt-4o
OPENAI_API_KEY=sk-your-openai-api-key-here

DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_API_KEY=sk-your-deepseek-api-key-here
```

### 修改智能体厂商分配

如果您想修改智能体使用的厂商，可以编辑`src/config/agents.py`文件中的`AGENT_LLM_MAP`：

```python
AGENT_LLM_MAP: dict[str, LLMProvider] = {
    "coordinator": "openai",      # 可以改为其他厂商
    "planner": "claude",          # 例如改为claude
    "supervisor": "google",       # 例如改为google
    # ... 其他智能体配置
}
```

## 验证配置

启动系统时，会自动显示配置信息：

```bash
python server.py
```

您会看到类似以下的输出，显示各厂商的配置状态：

```
🔍 厂商配置测试:
  openai    : gpt-4o                     | ChatOpenAI               | API Key: ✅
  deepseek  : deepseek-chat              | ChatDeepSeek             | API Key: ✅
  google    : gemini-2.5-pro-preview-06-05 | ChatGoogleGenerativeAI | API Key: ❌
```

## 常见问题

### Q: 如何获取API密钥？

- **OpenAI**: https://platform.openai.com/api-keys
- **DeepSeek**: https://platform.deepseek.com/api_keys
- **Google**: https://ai.google.dev/
- **Anthropic**: https://console.anthropic.com/
- **阿里云**: https://dashscope.aliyuncs.com/

### Q: 可以只使用一个厂商吗？

可以，您可以将所有智能体都配置为使用同一个厂商。修改`src/config/agents.py`中的配置即可。

### Q: Base URL是必需的吗？

大部分厂商有默认的Base URL，您可以不设置。只有在使用代理或自定义端点时才需要设置。

### Q: 如何使用本地模型？

配置Ollama相关参数，确保Ollama服务正在运行，然后将需要的智能体配置为使用"ollama"厂商。 