#!/usr/bin/env python3
"""
FusionAI 智能体工作流图生成器（精简版）

这个脚本专门用于生成FusionAI项目的智能体工作流程图。
支持PNG和Mermaid输出格式。

使用方法：
python scripts/generate_workflow_diagram.py [选项]

作者：FusionAI团队
版本：2.0.0
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# 添加项目根目录到系统路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    import graphviz
except ImportError as e:
    print(f"❌ 缺少依赖包: {e}")
    print("请安装依赖: pip install graphviz 或 uv add graphviz")
    print("同时需要安装系统级Graphviz: brew install graphviz (macOS)")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WorkflowAnalyzer:
    """工作流分析器 - 解析FusionAI项目的工作流结构"""
    
    def __init__(self):
        self.project_root = project_root
        self.graph_dir = self.project_root / "src" / "graph"
        self.config_dir = self.project_root / "src" / "config"
        
    def analyze_workflow(self) -> Dict[str, Any]:
        """分析当前工作流结构"""
        logger.info("🔍 开始分析工作流结构...")
        
        workflow_info = {
            "nodes": {},
            "edges": [],
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "project_name": "FusionAI",
                "version": "2.0.0"
            }
        }
        
        # 分析节点和边
        self._analyze_graph_structure(workflow_info)
        
        logger.info(f"✅ 工作流分析完成，发现 {len(workflow_info['nodes'])} 个节点")
        return workflow_info
    
    def _analyze_graph_structure(self, workflow_info: Dict[str, Any]):
        """分析图结构"""
        # 预定义的标准工作流结构
        standard_nodes = {
            "coordinator": {
                "name": "coordinator",
                "type": "入口节点",
                "description": "与用户交互，接收任务需求"
            },
            "planner": {
                "name": "planner", 
                "type": "规划节点",
                "description": "制定详细执行计划，分解任务步骤"
            },
            "supervisor": {
                "name": "supervisor",
                "type": "监督节点", 
                "description": "协调各个智能体，决定下一步行动"
            },
            "researcher": {
                "name": "researcher",
                "type": "执行节点",
                "description": "进行网络搜索和信息收集"
            },
            "coder": {
                "name": "coder",
                "type": "执行节点", 
                "description": "执行Python代码和数据处理"
            },
            "browser": {
                "name": "browser",
                "type": "执行节点",
                "description": "浏览器自动化操作"
            },
            "reporter": {
                "name": "reporter",
                "type": "整合输出节点",
                "description": "整合所有执行结果，生成最终报告"
            },
            "db_analyst": {
                "name": "db_analyst", 
                "type": "执行节点",
                "description": "数据库查询和分析"
            },
            "document_parser": {
                "name": "document_parser",
                "type": "执行节点", 
                "description": "文档解析和内容分析"
            }
        }
        
        workflow_info["nodes"] = standard_nodes
        
        # 标准的工作流连接
        standard_edges = [
            {"from": "start", "to": "coordinator", "type": "direct"},
            {"from": "coordinator", "to": "planner", "type": "direct"}, 
            {"from": "planner", "to": "supervisor", "type": "direct"},
            {"from": "supervisor", "to": "researcher", "type": "conditional", "condition": "路由到researcher"},
            {"from": "supervisor", "to": "coder", "type": "conditional", "condition": "路由到coder"},
            {"from": "supervisor", "to": "browser", "type": "conditional", "condition": "路由到browser"},
            {"from": "supervisor", "to": "reporter", "type": "conditional", "condition": "路由到reporter"},
            {"from": "supervisor", "to": "db_analyst", "type": "conditional", "condition": "路由到db_analyst"},
            {"from": "supervisor", "to": "document_parser", "type": "conditional", "condition": "路由到document_parser"},
            # 添加返回连接
            {"from": "researcher", "to": "supervisor", "type": "direct", "condition": "任务完成"},
            {"from": "coder", "to": "supervisor", "type": "direct", "condition": "任务完成"},
            {"from": "browser", "to": "supervisor", "type": "direct", "condition": "任务完成"},
            {"from": "db_analyst", "to": "supervisor", "type": "direct", "condition": "任务完成"},
            {"from": "document_parser", "to": "supervisor", "type": "direct", "condition": "任务完成"},
            # reporter直接到结束
            {"from": "reporter", "to": "end", "type": "direct"},
            # supervisor到结束
            {"from": "supervisor", "to": "end", "type": "conditional", "condition": "任务完成"}
        ]
        
        workflow_info["edges"] = standard_edges

class DiagramGenerator:
    """流程图生成器（精简版）"""
    
    def __init__(self, workflow_info: Dict[str, Any]):
        self.workflow_info = workflow_info
        self.output_dir = project_root / "docs" / "diagrams"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_png_and_mermaid(self) -> Dict[str, str]:
        """生成PNG和Mermaid格式的流程图"""
        results = {}
        
        logger.info("🎨 开始生成流程图...")
        
        # 生成PNG图
        try:
            results["png"] = self.generate_graphviz_diagram()
            logger.info("✅ PNG流程图生成完成")
        except Exception as e:
            logger.error(f"❌ PNG图生成失败: {e}")
        
        # 生成Mermaid代码
        try:
            results["mermaid"] = self.generate_mermaid_code()
            logger.info("✅ Mermaid代码生成完成")
        except Exception as e:
            logger.error(f"❌ Mermaid代码生成失败: {e}")
        
        return results
    
    def generate_graphviz_diagram(self) -> str:
        """生成Graphviz PNG流程图"""
        dot = graphviz.Digraph(comment='FusionAI工作流', format='png')
        dot.attr(rankdir='LR')  # 左右布局
        dot.attr('node', shape='box', style='rounded,filled', fontname='Arial')
        dot.attr('graph', bgcolor='white', fontname='Arial')
        
        # 定义节点颜色
        node_colors = {
            "入口节点": "#E3F2FD",    # 浅蓝色
            "规划节点": "#F3E5F5",    # 浅紫色
            "监督节点": "#FFF3E0",    # 浅橙色
            "执行节点": "#E8F5E8",    # 浅绿色
            "整合输出节点": "#FFEBEE",  # 浅红色
        }
        
        # 添加开始和结束节点
        dot.node("start", "开始", shape="ellipse", fillcolor="#4CAF50", fontcolor="white", fontsize="12")
        dot.node("end", "结束", shape="ellipse", fillcolor="#F44336", fontcolor="white", fontsize="12")
        
        # 添加工作流节点
        for node_name, node_info in self.workflow_info["nodes"].items():
            color = node_colors.get(node_info["type"], "#F5F5F5")
            # 节点标签使用中英文对照
            label = f"{node_name}\\n{node_info['description']}"
            dot.node(node_name, label, fillcolor=color, fontsize="10")
        
        # 添加边
        for edge in self.workflow_info["edges"]:
            edge_style = "dashed" if edge["type"] == "conditional" else "solid"
            edge_color = "#2196F3" if edge["type"] == "conditional" else "#333333"
            
            label = edge.get("condition", "")
            dot.edge(edge["from"], edge["to"], label=label, style=edge_style, 
                    color=edge_color, fontsize="8")
        
        # 生成文件
        output_file = self.output_dir / "fusionai_workflow.png"
        dot.render(output_file.with_suffix(""), format='png', cleanup=True)
        
        return str(output_file)
    
    def generate_mermaid_code(self) -> str:
        """生成Mermaid图表代码"""
        mermaid_code = "graph LR\n"
        
        # 添加节点定义
        node_definitions = []
        for node_name, node_info in self.workflow_info["nodes"].items():
            node_type = node_info["type"]
            description = node_info["description"]
            
            if node_type == "入口节点":
                shape = f'{node_name}["{node_name}<br/>{description}"]'
            elif node_type == "监督节点":
                shape = f'{node_name}{{{node_name}<br/>{description}}}'
            else:
                shape = f'{node_name}["{node_name}<br/>{description}"]'
            node_definitions.append(f"    {shape}")
        
        # 添加特殊节点
        node_definitions.append('    start([开始])')
        node_definitions.append('    end([结束])')
        
        mermaid_code += "\n".join(node_definitions) + "\n\n"
        
        # 添加边
        edge_definitions = []
        for edge in self.workflow_info["edges"]:
            if edge["type"] == "conditional":
                condition = edge.get("condition", "")
                edge_def = f'    {edge["from"]} -->|{condition}| {edge["to"]}'
            else:
                edge_def = f'    {edge["from"]} --> {edge["to"]}'
            edge_definitions.append(edge_def)
        
        mermaid_code += "\n".join(edge_definitions) + "\n\n"
        
        # 添加样式
        mermaid_code += """    classDef startEnd fill:#4CAF50,stroke:#333,stroke-width:2px,color:#fff
    classDef coordinator fill:#E3F2FD,stroke:#333,stroke-width:2px
    classDef planner fill:#F3E5F5,stroke:#333,stroke-width:2px  
    classDef supervisor fill:#FFF3E0,stroke:#333,stroke-width:2px
    classDef executor fill:#E8F5E8,stroke:#333,stroke-width:2px
    classDef reporter fill:#FFEBEE,stroke:#333,stroke-width:2px
    
    class start,end startEnd
    class coordinator coordinator
    class planner planner
    class supervisor supervisor
    class researcher,coder,browser,db_analyst,document_parser executor
    class reporter reporter
"""
        
        # 保存文件
        output_file = self.output_dir / "fusionai_workflow.mmd"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(mermaid_code)
        
        return str(output_file)

def generate_workflow_summary(workflow_info: Dict[str, Any]) -> str:
    """生成工作流摘要报告"""
    summary = f"""
# FusionAI 工作流分析报告

**生成时间**: {workflow_info['metadata']['generated_at']}
**项目版本**: {workflow_info['metadata']['version']}

## 📊 统计信息

- **节点总数**: {len(workflow_info['nodes'])}
- **边总数**: {len(workflow_info['edges'])}

## 🤖 智能体列表

"""
    
    for node_name, node_info in workflow_info['nodes'].items():
        summary += f"### {node_name}\n"
        summary += f"- **类型**: {node_info['type']}\n"
        summary += f"- **描述**: {node_info['description']}\n\n"
    
    summary += """## 🔄 工作流程

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

"""
    
    for edge in workflow_info['edges']:
        edge_type = "条件路由" if edge["type"] == "conditional" else "直接连接"
        condition = f" ({edge.get('condition', '')})" if edge.get('condition') else ""
        summary += f"- **{edge['from']}** → **{edge['to']}** - {edge_type}{condition}\n"
    
    # 保存摘要
    summary_file = project_root / "docs" / "workflow_summary.md"
    summary_file.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    return str(summary_file)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="FusionAI智能体工作流图生成器（精简版）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python scripts/generate_workflow_diagram.py           # 生成PNG和Mermaid格式
  python scripts/generate_workflow_diagram.py --summary # 同时生成摘要报告
  python scripts/generate_workflow_diagram.py --verbose # 显示详细日志
        """
    )
    
    parser.add_argument(
        '--summary',
        action='store_true', 
        help='生成工作流摘要报告'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='显示详细日志'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 打印欢迎信息
    print("🚀 FusionAI 智能体工作流图生成器（精简版）")
    print("=" * 55)
    
    try:
        # 分析工作流
        analyzer = WorkflowAnalyzer()
        workflow_info = analyzer.analyze_workflow()
        
        # 生成摘要
        if args.summary:
            summary_file = generate_workflow_summary(workflow_info)
            print(f"📋 工作流摘要已生成: {summary_file}")
        
        # 生成流程图
        generator = DiagramGenerator(workflow_info)
        results = generator.generate_png_and_mermaid()
        
        # 显示结果
        print("\n✅ 流程图生成完成!")
        print("📁 输出文件:")
        for format_name, file_path in results.items():
            if file_path:
                print(f"  📄 {format_name}: {file_path}")
        
        print(f"\n📊 工作流统计:")
        print(f"  🤖 智能体数量: {len(workflow_info['nodes'])}")
        print(f"  🔗 连接数量: {len(workflow_info['edges'])}")
        
        print(f"\n💡 使用提示:")
        print(f"  📖 查看PNG图片: open {results.get('png', '')}")
        print(f"  📝 查看Mermaid代码: cat {results.get('mermaid', '')}")
        
    except Exception as e:
        logger.error(f"❌ 程序执行失败: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 