import os
import platform
import json
import glob
from typing import Dict, List, Any
from langchain.tools import Tool
from src.config.env import AGENT_FILE_BASE_URL

def get_files_by_task_id(task_id: str) -> str:
    """
    根据任务ID查找所有相关的md文件，返回JSON数组
    
    Args:
        task_id: 任务ID
    
    Returns:
        包含文件信息的JSON数组字符串
    """
    try:
        system = platform.system().lower()
        
        # 构建文件搜索路径 - 根据file_manager的结构
        # 实际文件保存在 docs/executions/{task_id}/ 目录下
        base_dir = "docs/executions"
        task_dir = os.path.join(base_dir, task_id)
        
        files_info = []
        
        # 检查任务目录是否存在
        if not os.path.exists(task_dir):
            return json.dumps({
                "error": f"任务目录不存在: {task_id}",
                "task_id": task_id,
                "searched_path": task_dir,
                "files": []
            }, ensure_ascii=False, indent=2)
        
        # 查找所有.md文件
        md_pattern = os.path.join(task_dir, "*.md")
        md_files = glob.glob(md_pattern)
        
        for file_path in md_files:
            file_name = os.path.basename(file_path)
            
            # 根据操作系统生成正确的URL
            if system == 'linux':
                # Linux系统：使用配置的文件服务器域名
                relative_path = os.path.relpath(file_path, start='.')
                file_url = f"{AGENT_FILE_BASE_URL}/{relative_path}"
            elif system == 'darwin':  # macOS
                # macOS：生成完整的文件系统路径
                file_url = os.path.abspath(file_path)
            elif system == 'windows':
                # Windows：生成完整的文件系统路径
                file_url = os.path.abspath(file_path)
            else:
                # 未知系统：使用绝对路径
                file_url = os.path.abspath(file_path)
            
            # 获取文件大小
            file_size = 0
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
            
            # 构建文件信息
            file_info = {
                "name": file_name,
                "url": file_url,
                "size": file_size,
                "exists": True
            }
            
            files_info.append(file_info)
        
        # 构建响应数据
        response_data = {
            "task_id": task_id,
            "system": system,
            "task_directory": os.path.abspath(task_dir),
            "total_files": len(files_info),
            "files": files_info
        }
        
        return json.dumps(response_data, ensure_ascii=False, indent=2)
        
    except Exception as e:
        error_response = {
            "error": f"查找文件失败: {str(e)}",
            "task_id": task_id,
            "system": platform.system().lower(),
            "files": []
        }
        return json.dumps(error_response, ensure_ascii=False, indent=2)


def get_task_files_tool(task_id: str) -> str:
    """
    根据任务ID获取所有相关md文件的JSON信息
    
    Args:
        task_id: 任务ID
    
    Returns:
        包含文件信息的JSON字符串
    """
    try:
        return get_files_by_task_id(task_id)
        
    except Exception as e:
        error_response = {
            "error": f"工具执行失败: {str(e)}",
            "task_id": task_id,
            "files": []
        }
        return json.dumps(error_response, ensure_ascii=False, indent=2)


# 创建LangChain工具
task_files_json_tool = Tool(
    name="get_task_files_json",
    description="""
    根据任务ID获取所有相关md文件的JSON信息
    
    参数:
    - task_id (str): 任务ID，用于查找对应的文件目录
    
    功能:
    - 根据任务ID查找 docs/executions/{task_id}/ 目录下的所有.md文件
    - 根据操作系统生成正确的文件访问路径
    - Linux系统：使用环境变量配置的文件服务器域名 (AGENT_FILE_BASE_URL)
    - macOS/Windows：生成完整的文件系统路径
    - 返回包含name和url的JSON数组
    
    返回:
    JSON格式的文件列表，每个文件包含：
    - name: 文件名
    - url: 根据操作系统优化的访问路径
    - size: 文件大小
    - exists: 文件是否存在
    
    返回格式:
    {
        "task_id": "任务ID",
        "system": "操作系统",
        "task_directory": "任务目录路径", 
        "total_files": 文件数量,
        "files": [
            {
                "name": "文件名.md",
                "url": "文件访问路径",
                "size": 文件大小,
                "exists": true
            }
        ]
    }
    """,
    func=get_task_files_tool
) 