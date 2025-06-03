# 计划步骤追踪功能

## 概述

在 `/api/chat/stream` 接口中，现在可以实时追踪智能体正在执行 planning 中的哪一步。这个功能通过 SSE (Server-Sent Events) 流式传输两个新的事件类型来实现。

## 新增的事件类型

### 1. `plan_generated` 事件

当 planner 生成完整计划后触发此事件。

**事件格式：**
```json
{
  "event": "plan_generated",
  "data": {
    "plan_steps": [
      {
        "agent_name": "researcher",
        "title": "收集苹果公司股价信息",
        "description": "使用搜索引擎查找苹果公司最近的股价走势、相关新闻和分析报告",
        "note": "重点关注最近30天的数据"
      },
      {
        "agent_name": "coder",
        "title": "分析股价数据",
        "description": "使用 yfinance 获取详细的股价数据，计算技术指标",
        "note": "计算移动平均线、RSI等指标"
      },
      {
        "agent_name": "reporter",
        "title": "生成分析报告",
        "description": "基于收集的信息和分析结果，撰写一份专业的股价分析报告"
      }
    ],
    "total_steps": 3
  }
}
```

### 2. `step_started` 事件

当开始执行某个计划步骤时触发此事件。

**事件格式：**
```json
{
  "event": "step_started",
  "data": {
    "step_index": 1,
    "total_steps": 3,
    "step_info": {
      "agent_name": "researcher",
      "title": "收集苹果公司股价信息",
      "description": "使用搜索引擎查找苹果公司最近的股价走势、相关新闻和分析报告",
      "note": "重点关注最近30天的数据"
    }
  }
}
```

### 3. `step_end` 事件

当某个计划步骤执行完成时触发此事件。

**事件格式：**
```json
{
  "event": "step_end",
  "data": {
    "step_index": 1,
    "total_steps": 3,
    "step_info": {
      "agent_name": "researcher",
      "title": "收集苹果公司股价信息",
      "description": "使用搜索引擎查找苹果公司最近的股价走势、相关新闻和分析报告",
      "note": "重点关注最近30天的数据"
    }
  }
}
```

## 前端集成示例

### JavaScript/TypeScript 示例

```typescript
const eventSource = new EventSource('/api/chat/stream');

// 存储计划信息
let planSteps = [];
let currentStepIndex = 0;

eventSource.addEventListener('plan_generated', (event) => {
  const data = JSON.parse(event.data);
  planSteps = data.plan_steps;
  
  // 更新 UI 显示计划步骤
  updatePlanDisplay(planSteps);
  console.log(`计划已生成，共 ${data.total_steps} 个步骤`);
});

eventSource.addEventListener('step_started', (event) => {
  const data = JSON.parse(event.data);
  currentStepIndex = data.step_index;
  
  // 更新 UI 显示当前步骤
  updateCurrentStep(data.step_info);
  updateProgress(data.step_index, data.total_steps);
  
  console.log(`正在执行步骤 ${data.step_index}/${data.total_steps}: ${data.step_info.title}`);
});

// UI 更新函数示例
function updatePlanDisplay(steps) {
  const planContainer = document.getElementById('plan-steps');
  planContainer.innerHTML = steps.map((step, index) => `
    <div class="step" id="step-${index + 1}">
      <h4>${index + 1}. ${step.title}</h4>
      <p>执行者: ${step.agent_name}</p>
      <p>${step.description}</p>
      ${step.note ? `<p class="note">注意: ${step.note}</p>` : ''}
    </div>
  `).join('');
}

function updateCurrentStep(stepInfo) {
  // 高亮当前步骤
  document.querySelectorAll('.step').forEach(el => el.classList.remove('active'));
  document.getElementById(`step-${currentStepIndex}`).classList.add('active');
}

function updateProgress(current, total) {
  const progress = (current / total) * 100;
  document.getElementById('progress-bar').style.width = `${progress}%`;
  document.getElementById('progress-text').textContent = `步骤 ${current}/${total}`;
}
```
### Python 客户端示例

```python
import json
import sseclient
import requests

def track_plan_execution(messages):
    """追踪计划执行进度"""
    
    response = requests.post(
        'http://localhost:8000/api/chat/stream',
        json={'messages': messages},
        stream=True
    )
    
    client = sseclient.SSEClient(response)
    plan_steps = []
    
    for event in client.events():
        data = json.loads(event.data)
        
        if event.event == 'plan_generated':
            plan_steps = data['plan_steps']
            print(f"✅ 计划已生成，共 {data['total_steps']} 个步骤:")
            for i, step in enumerate(plan_steps):
                print(f"   {i+1}. {step['title']} ({step['agent_name']})")
        
        elif event.event == 'step_started':
            step_info = data['step_info']
            print(f"\n🚀 步骤 {data['step_index']}/{data['total_steps']}: {step_info['title']}")
            print(f"   执行者: {step_info['agent_name']}")
            print(f"   描述: {step_info['description']}")
```

## 实现细节

### 1. 事件流监听

在 `src/service/workflow_service.py` 中，通过监听 LangGraph 的事件流来追踪计划步骤：

- **计划生成追踪**：通过监听 `on_chat_model_stream` 事件累积 planner 的输出，在 `on_chain_end` 事件时解析完整的计划
- **步骤执行追踪**：通过监听 `on_chain_start` 事件，当特定的 agent 开始执行时，匹配对应的计划步骤

### 2. 计划解析

系统会：
1. 累积 planner 节点的流式输出
2. 在 planner 完成时解析 JSON 格式的计划
3. 提取 `steps` 数组中的步骤信息
4. 发送 `plan_generated` 事件

### 3. 步骤匹配

当某个 agent 开始执行时：
1. 检查该 agent 是否在 TEAM_MEMBERS 中
2. 在计划步骤中查找匹配的 `agent_name`
3. 发送 `step_started` 事件，包含当前步骤信息

## 注意事项

1. **步骤匹配**：系统通过 `agent_name` 来匹配计划中的步骤和实际执行的 agent。
2. **步骤索引**：步骤索引从 1 开始，便于用户理解。
3. **错误处理**：如果计划解析失败，系统仍会继续执行，但不会发送步骤追踪事件。
4. **流式处理**：计划内容通过流式方式累积，确保完整接收后再解析。

## 测试

可以运行 `test_plan_tracking.py` 来测试这个功能：

```bash
python test_plan_tracking.py
```

这将模拟一个完整的工作流程，并打印出所有的计划步骤追踪事件。 
