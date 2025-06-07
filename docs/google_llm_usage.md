# Google LLM 支持文档

FusionAI框架现在支持Google的Gemini模型。系统会根据模型名称自动选择合适的LLM提供商。

## 支持的模型

### Google Gemini 模型
- `gemini-2.5-pro-preview-06-05`
- `gemini-pro`
- `gemini-pro-vision`
- `models/gemini-pro`
- `models/gemini-pro-vision`

### 其他支持的模型
- **DeepSeek**: `deepseek-chat`, `deepseek-coder`
- **OpenAI兼容**: `gpt-4o`, `gpt-4o-mini`, `claude-3-5-sonnet-20241022`等

## 环境配置

在环境变量中设置Google API Key：

```bash
# Google API配置
GOOGLE_API_KEY=your_google_api_key

# 示例：使用Google模型
REASONING_MODEL=gemini-2.5-pro-preview-06-05
BASIC_MODEL=gemini-pro
VL_MODEL=gemini-pro-vision
```

## 使用方法

### 1. 通过环境变量配置

```python
# 在.env文件中设置
REASONING_MODEL=gemini-2.5-pro-preview-06-05
GOOGLE_API_KEY=your_api_key

# 代码中使用
from src.agents.llm import get_llm_by_type

reasoning_llm = get_llm_by_type("reasoning")  # 自动使用Google LLM
response = reasoning_llm.invoke("你好，请介绍一下自己")
```

### 2. 直接创建Google LLM

```python
from src.agents.llm import create_google_llm

# 直接创建Google LLM实例
google_llm = create_google_llm(
    model="gemini-2.5-pro-preview-06-05",
    api_key="your_api_key",
    temperature=0.7
)

response = google_llm.invoke("请用中文回答问题")
```

### 3. 自动模型选择

```python
from src.agents.llm import _create_llm_by_model_name

# 系统会根据模型名称自动选择提供商
llm = _create_llm_by_model_name(
    model="gemini-2.5-pro-preview-06-05",  # 自动选择Google
    api_key="your_api_key"
)

# 或者
llm = _create_llm_by_model_name(
    model="gpt-4o",  # 自动选择OpenAI兼容
    api_key="your_openai_key"
)
```

## 模型选择规则

系统使用以下规则自动选择LLM提供商：

1. **Google模型**: 模型名以`gemini`或`models/gemini`开头
2. **DeepSeek模型**: 模型名以`deepseek`开头  
3. **OpenAI兼容**: 其他所有模型（包括GPT、Claude等）

## 配置示例

### 全Google配置
```bash
REASONING_MODEL=gemini-2.5-pro-preview-06-05
BASIC_MODEL=gemini-pro
VL_MODEL=gemini-pro-vision
GOOGLE_API_KEY=your_google_api_key
```

### 混合配置
```bash
REASONING_MODEL=gemini-2.5-pro-preview-06-05
REASONING_API_KEY=  # 留空，使用GOOGLE_API_KEY

BASIC_MODEL=gpt-4o-mini
BASIC_BASE_URL=https://api.openai.com/v1
BASIC_API_KEY=your_openai_key

VL_MODEL=claude-3-5-sonnet-20241022
VL_BASE_URL=https://api.anthropic.com
VL_API_KEY=your_anthropic_key

GOOGLE_API_KEY=your_google_api_key
```

## 注意事项

1. **API Key优先级**: 
   - 如果指定了特定的API Key（如`REASONING_API_KEY`），优先使用
   - 否则对于Google模型，使用`GOOGLE_API_KEY`

2. **模型名称**: 
   - Google模型名称必须准确，建议使用官方模型名称
   - 支持带`models/`前缀的格式

3. **错误处理**: 
   - 如果API Key未配置，创建LLM时会失败
   - 建议在生产环境中设置所有必要的API Key

4. **性能考虑**:
   - LLM实例会被缓存，避免重复创建
   - 不同类型的LLM（reasoning、basic、vision）分别缓存

## 测试

运行测试脚本验证Google LLM支持：

```bash
python3 test_google_llm.py
```

这将测试：
- Google LLM创建
- 自动模型选择
- 环境配置检查 