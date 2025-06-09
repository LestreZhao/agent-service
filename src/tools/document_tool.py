from langchain.tools import Tool
from typing import Dict, Any
import json
import requests
import tempfile
import os
from urllib.parse import urlparse, unquote
import time
import logging
import traceback

# 导入日志配置
from src.utils.logger_config import setup_logging
from .document_parser import document_parser

# 配置日志记录
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def download_and_parse_document(url: str) -> dict:
    """下载并解析文档文件"""
    max_retries = 3
    retry_delay = 2  # 秒
    
    for attempt in range(max_retries):
        try:
            # 下载文件，增加超时时间
            response = requests.get(url, timeout=60)  # 增加到60秒
            
            if response.status_code != 200:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                return {
                    "success": False,
                    "error": f"下载失败，状态码: {response.status_code}"
                }
            
            # 获取文件信息
            parsed_url = urlparse(url)
            filename = unquote(parsed_url.path.split('/')[-1]).split('?')[0]
            
            # 如果URL中没有文件名，使用默认名称
            if not filename or '.' not in filename:
                # 根据Content-Type猜测文件类型
                content_type = response.headers.get('content-type', '').lower()
                if 'pdf' in content_type:
                    filename = "document.pdf"
                elif 'word' in content_type or 'document' in content_type:
                    filename = "document.docx"
                else:
                    filename = "document.pdf"  # 默认假设为PDF
            
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
                    from docx import Document
                    doc = Document(temp_path)
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
                    "source_url": url,
                    "download_attempt": attempt + 1
                }
            
            except ImportError as e:
                return {
                    "success": False,
                    "error": f"缺少解析库: {e}. 请安装 PyPDF2 或 python-docx"
                }
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
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
        
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))  # 递增延迟
                continue
            return {
                "success": False,
                "error": f"下载超时，已重试 {max_retries} 次"
            }
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            return {
                "success": False,
                "error": f"下载或处理失败: {e}"
            }
    
    return {
        "success": False,
        "error": f"重试 {max_retries} 次后仍然失败"
    }


def analyze_document_content_tool(document_url, analysis_request: str = "") -> str:
    """
    文档解析分析工具 - 接收可访问的URL和用户需求，获取文件并解析分析
    
    Args:
        document_url: 可访问的文档URL或文件ID
        analysis_request: 用户的分析要求
        
    Returns:
        文档分析结果的JSON字符串
    """
    logger.info(f"开始分析文档，原始输入: {document_url}")
    logger.info(f"输入类型: {type(document_url)}")
    logger.info(f"分析要求: {analysis_request}")
    
    try:
        # 参数类型检查和转换
        if isinstance(document_url, dict):
            logger.warning(f"接收到字典类型的输入参数: {document_url}")
            
            # 检查是否是完整的参数字典 (包含document_url和analysis_request字段)
            if 'document_url' in document_url and 'analysis_request' in document_url:
                logger.info("检测到完整参数字典格式")
                analysis_request = document_url['analysis_request']
                document_url = document_url['document_url']
                logger.info(f"提取的文档URL: {document_url}")
                logger.info(f"提取的分析要求: {analysis_request}")
            
            # 检查是否是只包含URL/ID的字典
            elif 'url' in document_url:
                document_url = document_url['url']
                logger.info(f"从字典中提取URL: {document_url}")
            elif 'id' in document_url:
                document_url = document_url['id']
                logger.info(f"从字典中提取ID: {document_url}")
            elif 'file_id' in document_url:
                document_url = document_url['file_id']
                logger.info(f"从字典中提取file_id: {document_url}")
            elif 'document_url' in document_url:
                # 只有document_url字段的情况
                document_url = document_url['document_url']
                logger.info(f"从字典中提取document_url: {document_url}")
            else:
                logger.error(f"字典中未找到有效的URL或ID字段: {document_url}")
                return json.dumps({
                    "error": f"输入参数格式错误：字典中未找到有效的URL或ID字段。支持的字段：document_url, url, id, file_id",
                    "success": False,
                    "input_received": str(document_url),
                    "error_type": "invalid_input_format"
                }, ensure_ascii=False)
        
        # 确保document_url是字符串
        if not isinstance(document_url, str):
            document_url = str(document_url)
            logger.info(f"转换为字符串: {document_url}")
        
        logger.info(f"处理后的文档URL: {document_url}")
        
        # 检查是否是文件ID（UUID格式）
        import re
        uuid_pattern = r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$'
        
        logger.debug(f"检查输入格式: {document_url}")
        
        if re.match(uuid_pattern, document_url):
            logger.info(f"识别为文件ID格式: {document_url}")
            
            # 这是一个文件ID，从存储系统获取文档
            try:
                logger.debug("尝试从存储系统获取文件信息")
                document_info = document_parser.get_file_info(document_url)
                logger.debug(f"get_file_info返回结果: {document_info is not None}")
            except Exception as e:
                logger.error(f"调用document_parser.get_file_info失败: {str(e)}")
                logger.error(f"详细错误信息: {traceback.format_exc()}")
                return json.dumps({
                    "error": f"获取文件信息时发生内部错误: {str(e)}",
                    "success": False,
                    "input_received": document_url,
                    "error_type": "file_info_retrieval_error",
                    "detailed_error": traceback.format_exc()
                }, ensure_ascii=False)
            
            if document_info is None:
                logger.warning(f"未找到文件ID: {document_url}")
                return json.dumps({
                    "error": f"未找到文件ID为 {document_url} 的文档",
                    "success": False,
                    "input_received": document_url,
                    "error_type": "file_not_found"
                }, ensure_ascii=False)
            
            logger.info(f"成功获取文件信息: {document_info.get('filename', 'Unknown')}")
            content = document_info.get("content", "")
            logger.debug(f"文档内容长度: {len(content)}")
            
            # 构建分析结果
            try:
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
                
                logger.info("成功构建分析结果")
                return json.dumps({
                    "success": True,
                    "data": analysis,
                    "source_type": "file_storage"
                }, ensure_ascii=False, indent=2)
                
            except Exception as e:
                logger.error(f"构建分析结果失败: {str(e)}")
                logger.error(f"详细错误信息: {traceback.format_exc()}")
                return json.dumps({
                    "error": f"构建分析结果失败: {str(e)}",
                    "success": False,
                    "input_received": document_url,
                    "error_type": "analysis_construction_error",
                    "detailed_error": traceback.format_exc()
                }, ensure_ascii=False)
        
        # 检查是否是内部API URL格式
        elif "/api/documents/" in document_url and any(endpoint in document_url for endpoint in ["/content", "/info", "/analyze"]):
            # 从API URL中提取文件ID
            try:
                # 匹配 /api/documents/{file_id}/xxx 格式
                api_pattern = r'/api/documents/([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'
                match = re.search(api_pattern, document_url)
                
                if match:
                    file_id = match.group(1)
                    # 递归调用，使用提取的文件ID
                    return analyze_document_content_tool(file_id, analysis_request)
                else:
                    return json.dumps({
                        "error": f"无法从API URL中提取有效的文件ID: {document_url}",
                        "success": False,
                        "input_received": document_url
                    }, ensure_ascii=False)
                    
            except Exception as e:
                return json.dumps({
                    "error": f"解析API URL失败: {str(e)}",
                    "success": False,
                    "input_received": document_url
                }, ensure_ascii=False)
        
        else:
            # 这是一个外部URL，下载并解析文档
            parse_result = download_and_parse_document(document_url)
            
            if not parse_result["success"]:
                return json.dumps({
                    "error": parse_result["error"],
                    "success": False,
                    "input_received": document_url
                }, ensure_ascii=False)
            
            content = parse_result["content"]
            
            # 构建分析结果
            analysis = {
                "document_info": {
                    "filename": parse_result["filename"],
                    "file_type": parse_result["file_type"],
                    "file_size": parse_result["file_size"],
                    "uploaded_at": "从URL下载",
                    "parsed_at": "实时解析",
                    "source_url": document_url[:100] + "..." if len(document_url) > 100 else document_url
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
                "source_type": "url_download"
            }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"文档分析工具发生未捕获的异常: {str(e)}")
        logger.error(f"详细错误信息: {traceback.format_exc()}")
        return json.dumps({
            "error": f"分析文档失败: {str(e)}",
            "success": False,
            "input_received": document_url,
            "error_type": "unexpected_error",
            "detailed_error": traceback.format_exc()
        }, ensure_ascii=False)


# 创建 LangChain 工具
document_analysis_tool = Tool(
    name="analyze_document_content",
    description="""
    文档解析分析工具 - 根据可访问的URL和用户需求进行文档分析
    
    参数:
    - document_url (str): 可访问的文档URL或文件ID
      * 支持各种可访问的URL（http/https链接）
      * 支持文件ID（UUID格式）
    - analysis_request (str, 可选): 用户的具体分析要求，如"总结主要内容"、"提取关键信息"等
    
    功能:
    - 自动下载指定URL的文档文件
    - 解析文档内容（支持PDF和Word格式）
    - 根据用户需求进行内容分析
    - 提供文档统计信息和内容预览
    
    返回包含以下信息的JSON:
    - document_info: 文档基本信息（文件名、类型、大小等）
    - content_statistics: 内容统计（字数、行数、段落数等）
    - analysis_request: 用户的分析要求
    - document_content: 完整文档内容
    - content_preview: 内容预览（前1000字符）
    - source_type: 数据源类型 (url_download, file_storage)
    
    支持的文档格式: PDF (.pdf), Word (.docx, .doc)
    
    重要提醒: 使用此工具的智能体必须用中文回答所有问题和分析结果
    """,
    func=analyze_document_content_tool
) 