import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, TypedDict

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
        summary_file = task_dir / f"{agent_name}_summary.md"
        
        # 生成总结内容
        summary_content = self._generate_summary_content(agent_name, result_content, original_messages)
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        # 创建执行总结信息
        execution_summary: ExecutionSummary = {
            "agent_name": agent_name,
            "file_path": str(summary_file),
            "completed_at": datetime.now().isoformat(),
            "summary_content": summary_content[:500] + "..." if len(summary_content) > 500 else summary_content
        }
        
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
        for md_file in task_dir.glob("*_summary.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    summaries.append({
                        "agent_name": md_file.stem.replace('_summary', ''),
                        "file_path": str(md_file),
                        "content": content
                    })
            except Exception as e:
                print(f"读取文件 {md_file} 失败: {e}")
        
        return summaries
    
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
        
        # 检查总结文件
        for summary_file in task_dir.glob("*_summary.md"):
            files_info["summary_files"].append(str(summary_file))
        
        # 检查最终整合文件
        final_file = task_dir / "final_integration.md"
        if final_file.exists():
            files_info["final_integration"] = str(final_file)
        
        return files_info 