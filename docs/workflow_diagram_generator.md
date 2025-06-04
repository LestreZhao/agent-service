# FusionAI 智能体工作流图生成器使用指南

## 📖 概述

FusionAI 智能体工作流图生成器是一个专门为 FusionAI 项目设计的工具，用于自动分析和可视化智能体工作流程。该工具可以：

- 🔍 自动分析当前工作流结构
- 🎨 生成多种格式的流程图
- 🔄 支持自动刷新功能
- 📊 提供详细的工作流分析报告
- 🌐 生成交互式可视化图表

## 🚀 快速开始

### 1. 安装依赖

首先运行依赖安装脚本：

```bash
python scripts/setup_diagram_dependencies.py
```

或者手动安装：

```bash
# 安装Python包
pip install graphviz matplotlib networkx plotly watchdog

# 安装系统级Graphviz
# macOS
brew install graphviz

# Ubuntu/Debian
sudo apt-get install graphviz

# CentOS/RHEL
sudo yum install graphviz
```

### 2. 生成流程图

```bash
# 生成所有格式的流程图
python scripts/generate_workflow_diagram.py

# 只生成特定格式
python scripts/generate_workflow_diagram.py --format png

# 生成后自动打开
python scripts/generate_workflow_diagram.py --open

# 启动自动刷新模式
python scripts/generate_workflow_diagram.py --auto-refresh
```

## 🛠️ 功能特性

### 支持的输出格式

| 格式 | 文件类型 | 特点 | 用途 |
|------|----------|------|------|
| **PNG** | `.png` | 高质量静态图片 | 文档嵌入、演示 |
| **SVG** | `.svg` | 矢量图形，可缩放 | 网页展示、印刷 |
| **HTML** | `.html` | 交互式图表 | 在线浏览、详细查看 |
| **Mermaid** | `.mmd` | 图表代码 | 代码文档、集成 |

### 工作流分析功能

脚本会自动分析以下内容：

1. **节点分析** - 自动识别所有智能体节点
2. **边分析** - 分析节点间的连接关系
3. **智能体配置** - 提取智能体工具绑定信息
4. **工具映射** - 分析可用工具列表
5. **配置信息** - 读取团队成员和LLM映射

### 自动刷新功能

启动自动刷新模式后，脚本会：

- 🔍 监控 `src/graph/`、`src/agents/`、`src/config/` 目录
- 📁 检测文件变化
- 🔄 自动重新生成流程图
- ⚡ 实时更新可视化

## 📋 命令行选项

```bash
python scripts/generate_workflow_diagram.py [选项]
```

### 可用选项

| 选项 | 描述 | 默认值 |
|------|------|--------|
| `--format` | 输出格式：png, svg, html, mermaid, all | all |
| `--auto-refresh` | 启动自动刷新模式 | False |
| `--interval` | 自动刷新间隔(秒) | 5 |
| `--open` | 生成后自动打开 | False |
| `--summary` | 生成工作流摘要报告 | False |
| `--verbose` | 显示详细日志 | False |

### 使用示例

```bash
# 基础用法 - 生成所有格式
python scripts/generate_workflow_diagram.py

# 只生成PNG格式
python scripts/generate_workflow_diagram.py --format png

# 生成HTML交互式图表并自动打开
python scripts/generate_workflow_diagram.py --format html --open

# 启动自动刷新模式，每3秒检查一次
python scripts/generate_workflow_diagram.py --auto-refresh --interval 3

# 生成摘要报告
python scripts/generate_workflow_diagram.py --summary

# 详细模式，显示所有日志
python scripts/generate_workflow_diagram.py --verbose
```

## 📁 输出文件说明

### 文件结构

```
docs/
├── diagrams/                          # 流程图输出目录
│   ├── fusionai_workflow.png         # PNG格式流程图
│   ├── fusionai_workflow.svg         # SVG格式流程图
│   ├── fusionai_workflow_matplotlib.png  # Matplotlib版本
│   ├── fusionai_workflow_interactive.html # 交互式HTML图表
│   └── fusionai_workflow.mmd         # Mermaid图表代码
└── workflow_summary.md               # 工作流分析摘要
```

### 文件说明

#### 1. PNG/SVG 流程图
- 使用 Graphviz 生成的专业流程图
- 不同类型节点使用不同颜色标识
- 支持条件边和直接边的区分

#### 2. Matplotlib 图表
- 基于网络图布局的可视化
- 适合展示节点间的拓扑关系
- 自动计算最优布局

#### 3. 交互式 HTML 图表
- 使用 Plotly 生成的交互式图表
- 支持鼠标悬停查看详细信息
- 可以缩放和平移
- 适合在线浏览和演示

#### 4. Mermaid 图表代码
```mermaid
graph TD
    coordinator["coordinator<br/>与用户交互，接收任务需求"]
    planner["planner<br/>制定详细执行计划，分解任务步骤"]
    supervisor{"supervisor<br/>协调各个智能体，决定下一步行动"}
    
    start([开始])
    end([结束])
    
    start --> coordinator
    coordinator --> planner
    planner --> supervisor
    supervisor -->|路由到researcher| researcher
    supervisor -->|任务完成| end
```

## 🔧 高级功能

### 1. 自定义配置

可以通过修改脚本中的配置来自定义输出：

```python
# 节点颜色配置
node_colors = {
    "入口节点": "#E3F2FD",
    "规划节点": "#F3E5F5", 
    "监督节点": "#FFF3E0",
    "执行节点": "#E8F5E8",
    "输出节点": "#FFEBEE"
}

# 图表尺寸配置
fig_size = (14, 10)  # Matplotlib图表大小
plotly_size = (1200, 800)  # Plotly图表大小
```

### 2. 扩展分析功能

脚本支持扩展新的分析功能：

```python
class WorkflowAnalyzer:
    def _analyze_custom_feature(self, workflow_info):
        """自定义分析功能"""
        # 添加你的分析逻辑
        pass
```

### 3. 自定义输出格式

可以添加新的输出格式生成器：

```python
class DiagramGenerator:
    def generate_custom_format(self):
        """自定义格式生成器"""
        # 实现你的生成逻辑
        pass
```

## 🔍 工作流分析详情

### 节点类型识别

脚本会自动识别以下节点类型：

- **入口节点** (coordinator) - 用户交互入口
- **规划节点** (planner) - 任务规划和分解
- **监督节点** (supervisor) - 流程控制和调度
- **执行节点** (researcher, coder, browser等) - 具体任务执行
- **输出节点** (reporter) - 结果整理和输出

### 边类型分析

- **直接边** - 固定的节点连接
- **条件边** - 基于状态的动态路由

### 智能体工具映射

自动分析每个智能体绑定的工具：

```
researcher:
  - tavily_search_tool
  - web_search_tool

coder:
  - python_repl_tool
  - code_execution_tool

browser:
  - browser_automation_tool
```

## 🐛 故障排除

### 常见问题

1. **Graphviz 未安装**
   ```
   ❌ 错误: dot: command not found
   💡 解决: 安装系统级Graphviz
   ```

2. **依赖包缺失**
   ```
   ❌ 错误: ModuleNotFoundError: No module named 'networkx'
   💡 解决: pip install networkx
   ```

3. **权限问题**
   ```
   ❌ 错误: Permission denied
   💡 解决: 检查输出目录权限
   ```

4. **导入错误**
   ```
   ❌ 错误: 无法导入智能体
   💡 解决: 检查项目路径和虚拟环境
   ```

### 调试技巧

1. **启用详细日志**
   ```bash
   python scripts/generate_workflow_diagram.py --verbose
   ```

2. **测试单个格式**
   ```bash
   python scripts/generate_workflow_diagram.py --format png
   ```

3. **检查依赖安装**
   ```bash
   python scripts/setup_diagram_dependencies.py
   ```

## 📊 性能建议

### 大型项目优化

对于大型工作流项目：

1. **使用特定格式** - 只生成需要的格式
2. **调整刷新间隔** - 增加自动刷新间隔
3. **限制监控范围** - 只监控关键文件

### 资源使用

- **内存使用**: 约50-100MB
- **CPU使用**: 生成时短暂高使用率
- **磁盘空间**: 输出文件约1-5MB

## 🔄 集成建议

### CI/CD 集成

```yaml
# GitHub Actions 示例
- name: Generate Workflow Diagrams
  run: |
    python scripts/setup_diagram_dependencies.py
    python scripts/generate_workflow_diagram.py --format all
    
- name: Upload Diagrams
  uses: actions/upload-artifact@v3
  with:
    name: workflow-diagrams
    path: docs/diagrams/
```

### 文档集成

在项目README中嵌入生成的图表：

```markdown
## 工作流程图

![FusionAI工作流](docs/diagrams/fusionai_workflow.png)

[查看交互式图表](docs/diagrams/fusionai_workflow_interactive.html)
```

## 🎯 最佳实践

1. **定期更新** - 在修改工作流后及时更新图表
2. **版本控制** - 将生成的图表纳入版本控制
3. **格式选择** - 根据用途选择合适的输出格式
4. **自动化** - 使用自动刷新模式进行开发
5. **文档同步** - 确保图表与代码保持同步

---

**📝 注意**: 这个工具是专门为FusionAI项目设计的，如需在其他项目中使用，可能需要相应的调整和配置。 