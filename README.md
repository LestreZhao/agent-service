# FusionAI - 智能工作流系统

## 📋 目录
- [项目简介](#项目简介)
- [主要功能](#主要功能) 
- [环境配置](#环境配置)
- [安装指南](#安装指南)
- [使用说明](#使用说明)
- [架构设计](#架构设计)
- [API接口](#api接口)
- [开发指南](#开发指南)

## 🚀 项目简介

FusionAI是由湖北福鑫科创信息技术有限公司开发的智能工作流系统，专注于通过多智能体协作来解决复杂的业务问题。

### 🎯 核心特性
- **多智能体协作**：研究员、程序员、数据分析师、文档解析器、图表生成器等专业智能体
- **智能任务规划**：自动分解复杂任务并分配给最适合的智能体
- **实时协作**：WebSocket支持的实时通信和状态更新
- **专业报告生成**：基于多源信息的综合分析报告

## 🏗️ 主要功能

### 智能体团队
- **🔍 研究员 (Researcher)**: 网络搜索和信息收集
- **💻 程序员 (Coder)**: Python编程和数据处理  
- **🗄️ 数据分析师 (DB Analyst)**: Oracle数据库查询和分析
- **📄 文档解析器 (Document Parser)**: 文档内容提取和分析
- **📊 图表生成器 (Chart Generator)**: ECharts数据可视化
- **🌐 浏览器 (Browser)**: 网页浏览和内容提取
- **📝 报告员 (Reporter)**: 综合报告生成

### 🔧 系统配置

#### 环境变量配置
```bash
# 禁用MD文件生成 (可选)
DISABLE_MD_FILE_GENERATION=true  # 或 false/1/0/yes/no
```

### 📊 提示词系统优化 (2024年最新)

本系统采用了全面优化的提示词架构，具有以下特点：

#### 🌍 国际化标准
- **英文指令描述**：所有提示词使用专业英文描述智能体能力和执行规则
- **中文输出要求**：强制要求所有智能体输出内容必须使用中文
- **统一语言规范**：确保用户体验的一致性和专业性

#### 🚫 执行静默原则
- **绝对静默执行**：智能体在工具调用过程中完全静默，零解释文本
- **仅最终输出**：只允许在任务完成后输出最终分析报告
- **零中间消息**：禁止任何执行过程描述或状态更新消息

#### 🧠 智能增强能力
- **深度分析能力**：每个智能体都具备深度挖掘和多维分析能力
- **自我纠错机制**：智能体具备自动错误检测和修正能力
- **质量保证体系**：内置质量检查和验证机制

#### 📋 提示词优化详情

##### 研究员 (Researcher)
- 战略搜索智能：多关键词组合和渐进搜索策略
- 深度内容分析：跨源信息验证和可信度评估
- 综合覆盖：多角度、多维度的研究方法
- 分析综合：将多源信息整合为连贯洞察

##### 程序员 (Coder)  
- 代码架构卓越：模块化、可重用的代码结构设计
- 技术问题解决：复杂需求分析和最优算法设计
- 数据分析精通：使用pandas、numpy等进行高级数据处理
- 质量保证：全面测试和性能优化

##### 数据分析师 (DB Analyst)
- 模式智能：数据库结构和关系的智能分析
- 自适应SQL生成：基于实际表结构的动态查询构建
- 自我纠错机制：动态模式验证和智能查询修改
- 5阶段工作流：发现→构建→纠错→挖掘→报告

##### 文档解析器 (Document Parser)
- 文档智能：多格式支持和最优解析策略
- 内容分析卓越：结构化和语义分析
- 多维洞察：业务、技术和战略见解提取
- 信息综合：复杂信息的清晰组织和呈现

##### 图表生成器 (Chart Generator)
- 智能图表类型选择：基于数据特征的最优可视化方法
- 专业ECharts精通：完整配置和交互功能实现
- 数据分析卓越：模式识别和业务洞察提取
- 视觉传达卓越：清晰、美观、功能优越的可视化

##### 浏览器 (Browser)
- 战略网页导航：智能站点交互和高价值信息源识别
- 高级内容分析：深度内容挖掘和模式识别
- 数字情报处理：实时数据捕获和多源集成
- 防循环系统：严格URL跟踪和强制完成机制

##### 报告员 (Reporter)
- 战略报告分析：综合信息合成和执行级摘要
- 多源分析集成：整合各智能体的分析结果
- 专业中文报告：高质量的中文商业报告生成
- 去工具依赖：直接基于工作流消息生成报告

#### 🎯 质量保证体系
- **完成标准**：每个智能体都有明确的任务完成标准
- **质量检查**：内置多级质量验证和检查机制  
- **性能优化**：针对效率和准确性的持续优化
- **用户体验**：专注于专业、高效的用户体验

## 🛠️ 环境配置

### 必需环境变量

```bash
# OpenAI API配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=your_openai_base_url

# Tavily搜索API
TAVILY_API_KEY=your_tavily_api_key

# Oracle数据库配置
ORACLE_HOST=your_oracle_host
ORACLE_PORT=1521
ORACLE_SERVICE_NAME=your_service_name
ORACLE_USERNAME=your_username
ORACLE_PASSWORD=your_password

# 可选配置
DISABLE_MD_FILE_GENERATION=false  # 禁用MD文件生成
```

## 📦 安装指南

### 1. 克隆项目
```bash
git clone <repository_url>
cd langmanus
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，添加必要的API密钥和数据库配置
```

### 4. 启动系统
```bash
python -m src.main
```

## 🔧 使用说明

### 基本使用流程

1. **任务提交**：通过API或Web界面提交任务
2. **智能规划**：系统自动分析任务并制定执行计划
3. **多智能体协作**：各专业智能体按计划执行任务
4. **结果整合**：生成综合分析报告
5. **结果交付**：通过API或Web界面获取结果

### API使用示例

```python
import requests

# 提交任务
response = requests.post('http://localhost:8000/api/tasks', 
    json={'query': '分析苹果公司2023年财务表现'})
    
task_id = response.json()['task_id']

# 获取结果
result = requests.get(f'http://localhost:8000/api/tasks/{task_id}')
```

## 🏗️ 架构设计

### 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Frontend  │    │   API Gateway   │    │  Task Manager   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Planner       │    │   Supervisor    │    │   Coordinator   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
    ┌────────────────────────────┼────────────────────────────┐
    │            智能体团队       │                             │
┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐
│研究员 │ │程序员 │ │数据库 │ │文档   │ │图表   │ │报告员 │
│       │ │       │ │分析师 │ │解析器 │ │生成器 │ │       │
└───────┘ └───────┘ └───────┘ └───────┘ └───────┘ └───────┘
```

### 工作流程

1. **任务接收**：用户通过API或Web界面提交任务
2. **智能规划**：Planner分析任务并制定执行计划
3. **任务调度**：Supervisor根据计划调度相应的智能体
4. **并行执行**：多个智能体并行处理不同的子任务
5. **结果汇总**：Reporter整合所有结果生成最终报告
6. **质量检查**：系统验证结果质量和完整性
7. **结果交付**：通过API返回最终结果

## 📊 API接口

### 任务管理

#### 创建任务
```http
POST /api/tasks
Content-Type: application/json

{
    "query": "任务描述",
    "priority": "high|medium|low",
    "timeout": 3600
}
```

#### 获取任务状态
```http
GET /api/tasks/{task_id}
```

#### 获取任务结果
```http
GET /api/tasks/{task_id}/result
```

### WebSocket实时通信

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/{task_id}');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('任务状态更新:', data);
};
```

## 🔧 开发指南

### 添加新智能体

1. **创建智能体类**
```python
# src/agents/new_agent.py
class NewAgent:
    def __init__(self):
        self.name = "new_agent"
        
    async def execute(self, task):
        # 实现智能体逻辑
        return result
```

2. **添加提示词**
```markdown
# src/prompts/new_agent.md
# 智能体提示词内容
```

3. **注册智能体**
```python
# src/agents/__init__.py
from .new_agent import NewAgent
```

### 自定义工具

```python
# src/tools/custom_tool.py
from langchain.tools import BaseTool

class CustomTool(BaseTool):
    name = "custom_tool"
    description = "工具描述"
    
    def _run(self, query: str) -> str:
        # 实现工具逻辑
        return result
```

### 配置管理

```python
# src/config/custom.py
import os

CUSTOM_SETTING = os.getenv('CUSTOM_SETTING', 'default_value')
```

## 🤝 贡献指南

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系我们

- **公司**: 湖北福鑫科创信息技术有限公司
- **项目**: FusionAI智能工作流系统
- **文档**: [项目文档](docs/)
- **问题反馈**: [GitHub Issues](../../issues)

---

> 💡 **提示**: 更多详细信息请参考 [项目文档](docs/) 或联系开发团队。


