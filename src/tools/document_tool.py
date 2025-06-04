from langchain.tools import Tool
from typing import Dict, Any
import json
import re
import requests
import tempfile
import os
from urllib.parse import urlparse, unquote

from .document_parser import document_parser


def extract_file_id_from_url(url: str) -> str:
    """从文档URL中提取文件ID，支持多种URL格式"""
    
    # 1. 匹配 /api/documents/{file_id} 格式的URL
    pattern = r'/api/documents/([a-f0-9-]+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    
    # 2. 如果URL中包含file_id参数
    pattern = r'file_id=([a-f0-9-]+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    
    # 3. 直接检查是否是UUID格式
    uuid_pattern = r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$'
    if re.match(uuid_pattern, url):
        return url
    
    # 4. 处理MinIO预签名URL - 从路径中提取文件名作为标识
    try:
        parsed_url = urlparse(url)
        if parsed_url.path:
            # 提取路径中的文件名部分
            path_parts = parsed_url.path.strip('/').split('/')
            if len(path_parts) >= 2:  # 至少包含bucket和文件名
                # 获取文件名部分并解码URL编码
                filename = unquote(path_parts[-1])
                # 移除URL参数部分
                filename = filename.split('?')[0]
                # 为MinIO URL生成一个标识符（使用完整URL的哈希或路径）
                import hashlib
                url_hash = hashlib.md5(url.encode()).hexdigest()
                return f"minio-{url_hash[:12]}"
    except Exception:
        pass
    
    return ""


def download_and_parse_minio_file(url: str) -> dict:
    """下载并解析MinIO文件"""
    try:
        # 下载文件
        response = requests.get(url, timeout=30)
        
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"下载失败，状态码: {response.status_code}"
            }
        
        # 获取文件信息
        parsed_url = urlparse(url)
        filename = unquote(parsed_url.path.split('/')[-1]).split('?')[0]
        file_type = os.path.splitext(filename)[1].lower()
        file_size = len(response.content)
        
        # 保存到临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_type) as tmp_file:
            tmp_file.write(response.content)
            temp_path = tmp_file.name
        
        try:
            # 根据文件类型解析内容
            content = ""
            
            if file_type == '.pdf':
                # 解析PDF
                import PyPDF2
                with open(temp_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        content += page.extract_text() + "\n\n"
            
            elif file_type in ['.docx', '.doc']:
                # 解析Word文档
                import docx
                doc = docx.Document(temp_path)
                for paragraph in doc.paragraphs:
                    content += paragraph.text + "\n"
            
            else:
                # 尝试作为文本文件读取
                with open(temp_path, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()
            
            return {
                "success": True,
                "filename": filename,
                "file_type": file_type,
                "file_size": file_size,
                "content": content.strip(),
                "source_url": url
            }
        
        except ImportError as e:
            return {
                "success": False,
                "error": f"缺少解析库: {e}. 请安装 PyPDF2 或 python-docx"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"文件解析失败: {e}"
            }
        
        finally:
            # 清理临时文件
            try:
                os.unlink(temp_path)
            except:
                pass
    
    except Exception as e:
        return {
            "success": False,
            "error": f"下载或处理失败: {e}"
        }


def analyze_document_content_tool(document_url_or_id: str, analysis_request: str = "") -> str:
    """
    分析文档内容 - 核心工具
    
    Args:
        document_url_or_id: 文档URL或文件ID
        analysis_request: 用户的分析要求
        
    Returns:
        文档分析结果的JSON字符串
    """
    try:
        # 检查是否是MinIO URL（包含预签名参数）
        if 'X-Amz-Algorithm' in document_url_or_id or 'fusion-agent' in document_url_or_id:
            # 这是一个MinIO预签名URL，下载并解析实际文件
            parse_result = download_and_parse_minio_file(document_url_or_id)
            
            if not parse_result["success"]:
                return json.dumps({
                    "error": parse_result["error"],
                    "success": False,
                    "input_received": document_url_or_id
                }, ensure_ascii=False)
            
            content = parse_result["content"]
            
            # 构建分析结果
            analysis = {
                "document_info": {
                    "filename": parse_result["filename"],
                    "file_type": parse_result["file_type"],
                    "file_size": parse_result["file_size"],
                    "uploaded_at": "从MinIO下载",
                    "parsed_at": "实时解析",
                    "source_url": document_url_or_id[:100] + "..." if len(document_url_or_id) > 100 else document_url_or_id
                },
                "content_statistics": {
                    "content_length": len(content),
                    "word_count": len(content.split()) if content else 0,
                    "line_count": content.count('\n') + 1 if content else 0,
                    "paragraph_count": len([p for p in content.split('\n\n') if p.strip()]) if content else 0
                },
                "analysis_request": analysis_request,
                "document_content": content,
                "content_preview": content[:1000] + "..." if len(content) > 1000 else content
            }
            
            return json.dumps({
                "success": True,
                "data": analysis,
                "source_type": "minio_url_parsed"
            }, ensure_ascii=False, indent=2)
        
        # 原有的文件ID处理逻辑
        file_id = extract_file_id_from_url(document_url_or_id)
        if not file_id:
            # 如果提取失败，假设输入本身就是文件ID
            file_id = document_url_or_id
        
        # 获取文档信息
        document_info = document_parser.get_file_info(file_id)
        
        if document_info is None:
            return json.dumps({
                "error": f"未找到文件ID为 {file_id} 的文档",
                "success": False,
                "input_received": document_url_or_id,
                "extracted_id": file_id
            }, ensure_ascii=False)
        
        content = document_info.get("content", "")
        
        # 综合分析结果
        analysis = {
            "document_info": {
                "filename": document_info.get("filename"),
                "file_type": document_info.get("file_type"),
                "file_size": document_info.get("file_size"),
                "uploaded_at": document_info.get("uploaded_at"),
                "parsed_at": document_info.get("parsed_at")
            },
            "content_statistics": {
                "content_length": len(content),
                "word_count": len(content.split()) if content else 0,
                "line_count": len(content.split('\n')) if content else 0,
                "paragraph_count": len([p for p in content.split('\n\n') if p.strip()]) if content else 0
            },
            "analysis_request": analysis_request,
            "document_content": content,
            "content_preview": content[:1000] + "..." if len(content) > 1000 else content
        }
        
        return json.dumps({
            "success": True,
            "data": analysis,
            "source_type": "file_storage"
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"分析文档失败: {str(e)}",
            "success": False,
            "input_received": document_url_or_id
        }, ensure_ascii=False)


# 创建唯一的 LangChain 工具
document_analysis_tool = Tool(
    name="analyze_document_content",
    description="""
    分析文档内容的核心工具。可以处理多种文档URL格式或文件ID，并根据用户要求进行文档分析。
    
    参数:
    - document_url_or_id (str): 支持多种格式：
      * /api/documents/{file_id} 格式的API URL
      * MinIO预签名URL (包含 X-Amz-* 参数) - 会自动下载和解析
      * 包含file_id参数的URL
      * 直接的UUID文件ID
    - analysis_request (str, 可选): 用户的具体分析要求，如"总结主要内容"、"提取关键信息"等
    
    返回包含以下信息的JSON:
    - document_info: 文档基本信息（文件名、类型、大小等）
    - content_statistics: 内容统计（字数、行数、段落数等）
    - analysis_request: 用户的分析要求
    - document_content: 完整文档内容
    - content_preview: 内容预览（前1000字符）
    - source_type: 数据源类型 (file_storage, minio_url_parsed)
    
    支持的文档格式: PDF (.pdf), Word (.docx, .doc)
    支持的URL格式: API URLs, MinIO预签名URLs (自动下载解析), 参数化URLs, 直接UUID
    
    注意: MinIO URLs 会被自动下载并解析，提取真实的文档内容
    
    重要提醒: 使用此工具的智能体必须用中文回答所有问题和分析结果
    """,
    func=analyze_document_content_tool
) 