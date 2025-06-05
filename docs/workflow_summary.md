
# FusionAI 工作流分析报告

**生成时间**: 2025-06-04T15:15:32.735575
**项目版本**: 2.0.0

## 📊 统计信息

- **节点总数**: 9
- **边总数**: 16

## 🤖 智能体列表

### coordinator
- **类型**: 入口节点
- **描述**: 与用户交互，接收任务需求

### planner
- **类型**: 规划节点
- **描述**: 制定详细执行计划，分解任务步骤

### supervisor
- **类型**: 监督节点
- **描述**: 协调各个智能体，决定下一步行动

### researcher
- **类型**: 执行节点
- **描述**: 进行网络搜索和信息收集

### coder
- **类型**: 执行节点
- **描述**: 执行Python代码和数据处理

### browser
- **类型**: 执行节点
- **描述**: 浏览器自动化操作

### output_integrator
- **类型**: 整合输出节点
- **描述**: 整合所有执行结果，生成最终报告

### db_analyst
- **类型**: 执行节点
- **描述**: 数据库查询和分析

### document_parser
- **类型**: 执行节点
- **描述**: 文档解析和内容分析

## 🔄 工作流程

1. **开始** → **coordinator** - 用户输入接收
2. **coordinator** → **planner** - 任务规划
3. **planner** → **supervisor** - 执行协调
4. **supervisor** → **执行节点** - 分发到具体智能体
   - researcher (网络搜索)
   - coder (代码执行) 
   - browser (浏览器操作)
   - db_analyst (数据分析)
   - document_parser (文档处理)
   - reporter (报告生成)
5. **supervisor** → **结束** - 任务完成

## 📋 连接关系

- **start** → **coordinator** - 直接连接
- **coordinator** → **planner** - 直接连接
- **planner** → **supervisor** - 直接连接
- **supervisor** → **researcher** - 条件路由 (路由到researcher)
- **supervisor** → **coder** - 条件路由 (路由到coder)
- **supervisor** → **browser** - 条件路由 (路由到browser)
- **supervisor** → **output_integrator** - 条件路由 (路由到output_integrator)
- **supervisor** → **db_analyst** - 条件路由 (路由到db_analyst)
- **supervisor** → **document_parser** - 条件路由 (路由到document_parser)
- **researcher** → **supervisor** - 直接连接 (任务完成)
- **coder** → **supervisor** - 直接连接 (任务完成)
- **browser** → **supervisor** - 直接连接 (任务完成)
- **db_analyst** → **supervisor** - 直接连接 (任务完成)
- **document_parser** → **supervisor** - 直接连接 (任务完成)
- **output_integrator** → **end** - 直接连接
- **supervisor** → **end** - 条件路由 (任务完成)
