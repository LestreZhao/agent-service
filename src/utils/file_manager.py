import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, TypedDict
# 延迟导入title_generator以避免循环导入

logger = logging.getLogger(__name__)

class ExecutionSummary(TypedDict):
    """执行总结信息"""
    agent_name: str
    file_path: str
    completed_at: str
    summary_content: str

class ExecutionFileManager:
    """执行文件管理器，负责.md总结文件的管理"""
    
    def __init__(self, base_output_dir: str = "docs/executions"):
        self.base_output_dir = Path(base_output_dir)
        self.base_output_dir.mkdir(parents=True, exist_ok=True)
    
    def create_task_directory(self, task_id: str) -> str:
        """为任务创建专用目录"""
        task_dir = self.base_output_dir / task_id
        task_dir.mkdir(parents=True, exist_ok=True)
        return str(task_dir)
    
    def save_plan(self, task_id: str, plan_content: str) -> str:
        """保存原始计划为.md文件"""
        task_dir = self.base_output_dir / task_id
        plan_file = task_dir / "plan.md"
        
        with open(plan_file, 'w', encoding='utf-8') as f:
            f.write(f"# 任务执行计划\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"## 详细计划\n\n")
            f.write(plan_content)
        
        return str(plan_file)
    
    def save_execution_summary(self, task_id: str, agent_name: str, 
                             result_content: str, original_messages: List[Any]) -> ExecutionSummary:
        """保存执行节点的总结为.md文件"""
        task_dir = self.base_output_dir / task_id
        # 确保任务目录存在
        task_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成总结内容
        summary_content = self._generate_summary_content(agent_name, result_content, original_messages)
        
        # 使用大模型生成中文标题作为文件名
        logger.info(f"正在为{agent_name}的执行结果生成中文标题...")
        try:
            # 延迟导入以避免循环导入
            from src.utils.title_generator import title_generator
            chinese_title = title_generator.generate_chinese_title(summary_content, agent_name)
            filename = f"{chinese_title}.md"
            logger.info(f"生成的文件名: {filename}")
        except Exception as e:
            logger.error(f"生成标题失败，使用默认文件名: {e}")
            filename = f"{agent_name}_summary.md"
        
        summary_file = task_dir / filename
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        # 创建执行总结信息
        execution_summary: ExecutionSummary = {
            "agent_name": agent_name,
            "file_path": str(summary_file),
            "completed_at": datetime.now().isoformat(),
            "summary_content": summary_content[:500] + "..." if len(summary_content) > 500 else summary_content
        }
        
        logger.info(f"执行总结已保存到: {summary_file}")
        return execution_summary
    
    def _generate_summary_content(self, agent_name: str, result_content: str, 
                                original_messages: List[Any]) -> str:
        """直接保存智能体的原始输出内容，不添加任何额外格式"""
        return result_content
    
    def read_all_summaries(self, task_id: str) -> List[Dict[str, Any]]:
        """读取任务目录下的所有总结文件"""
        task_dir = self.base_output_dir / task_id
        summaries = []
        
        if not task_dir.exists():
            return summaries
        
        # 读取所有.md文件（除了plan.md和final_integration.md）
        excluded_files = {'plan.md', 'final_integration.md'}
        
        for md_file in task_dir.glob("*.md"):
            if md_file.name in excluded_files:
                continue
                
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # 尝试从文件内容或文件名推断智能体名称
                    agent_name = self._infer_agent_name(md_file.name, content)
                    
                    summaries.append({
                        "agent_name": agent_name,
                        "file_path": str(md_file),
                        "content": content,
                        "title": md_file.stem  # 保存文件标题
                    })
            except Exception as e:
                logger.error(f"读取文件 {md_file} 失败: {e}")
        
        return summaries
    
    def _infer_agent_name(self, filename: str, content: str) -> str:
        """从文件名或内容推断智能体名称"""
        # 如果是旧格式的文件名，直接提取
        if '_summary.md' in filename:
            return filename.replace('_summary.md', '')
        
        # 否则根据内容或文件名特征推断
        agent_indicators = {
            'researcher': ['研究', '分析', '调研', '市场'],
            'coder': ['代码', '编程', '开发', '脚本', '函数'],

            'db_analyst': ['数据库', '查询', 'SQL', '数据分析'],
            'document_parser': ['文档', '解析', 'PDF', 'Word'],
            'reporter': ['报告', '总结', '整合', '综合'],
            'chart_generator': ['图表', '可视化', '图形']
        }
        
        content_lower = content.lower()
        filename_lower = filename.lower()
        
        for agent, keywords in agent_indicators.items():
            for keyword in keywords:
                if keyword in content_lower or keyword in filename_lower:
                    return agent
        
        # 默认返回文件名（不含扩展名）
        return filename.replace('.md', '')
    
    def save_final_integration(self, task_id: str, integration_content: str) -> str:
        """保存最终整合输出"""
        task_dir = self.base_output_dir / task_id
        final_file = task_dir / "final_integration.md"
        
        with open(final_file, 'w', encoding='utf-8') as f:
            f.write(integration_content)
        
        return str(final_file)
    
    def get_task_files_info(self, task_id: str) -> Dict[str, Any]:
        """获取任务目录下所有文件的信息"""
        task_dir = self.base_output_dir / task_id
        if not task_dir.exists():
            return {}
        
        files_info = {
            "task_directory": str(task_dir),
            "plan_file": None,
            "summary_files": [],
            "final_integration": None
        }
        
        # 检查计划文件
        plan_file = task_dir / "plan.md"
        if plan_file.exists():
            files_info["plan_file"] = str(plan_file)
        
        # 检查总结文件（所有.md文件，除了plan.md和final_integration.md）
        excluded_files = {'plan.md', 'final_integration.md'}
        for md_file in task_dir.glob("*.md"):
            if md_file.name not in excluded_files:
                files_info["summary_files"].append(str(md_file))
        
        # 检查最终整合文件
        final_file = task_dir / "final_integration.md"
        if final_file.exists():
            files_info["final_integration"] = str(final_file)
        
        return files_info 