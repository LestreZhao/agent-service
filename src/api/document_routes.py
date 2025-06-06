from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from typing import Optional
import io
import urllib.parse

from src.tools.document_parser import document_parser

router = APIRouter(prefix="/documents", tags=["文档管理"])


@router.post("/upload", summary="上传文档")
async def upload_document(file: UploadFile = File(...), request: Request = None):
    """
    上传文档文件到MinIO并解析内容
    
    支持的文件格式：
    - PDF (.pdf)
    - Word (.docx, .doc)
    
    返回：
    - file_id: 文件唯一标识符
    - download_url: 可在浏览器直接打开的文件下载地址
    - 文档基本信息
    """
    # 检查文件类型
    allowed_extensions = {'.pdf', '.docx', '.doc'}
    file_ext = '.' + file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型。支持的格式: {', '.join(allowed_extensions)}"
        )
    
    try:
        # 读取文件内容
        file_content = await file.read()
        
        # 上传并解析文档
        document_info = document_parser.upload_file(file_content, file.filename)
        
        # 获取文件ID
        file_id = document_info['file_id']
        
        # 构建可在浏览器直接打开的下载URL
        if request:
            base_url = f"{request.url.scheme}://{request.url.netloc}"
            download_url = f"{base_url}/api/documents/{file_id}/download"
        else:
            download_url = f"/api/documents/{file_id}/download"
        
        return {
            "success": True,
            "message": "文档上传成功",
            "file_id": file_id,
            "download_url": download_url,  # 🎯 唯一的URL，可直接在浏览器打开
            "document_info": {
                "filename": document_info['filename'],
                "file_type": document_info['file_type'],
                "file_size": document_info['file_size'],
                "content_length": document_info['content_length'],
                "uploaded_at": document_info['uploaded_at']
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文档上传失败: {str(e)}")


@router.get("/{file_id}/info", summary="获取文档信息")
async def get_document_info(file_id: str):
    """
    获取文档的基本信息（不包含内容）
    
    Args:
        file_id: 文件ID
    
    Returns:
        文档基本信息
    """
    try:
        document_info = document_parser.get_file_info(file_id)
        
        if document_info is None:
            raise HTTPException(status_code=404, detail=f"未找到文件ID为 {file_id} 的文档")
        
        # 移除content字段，只返回基本信息
        info_data = {k: v for k, v in document_info.items() if k != 'content'}
        
        return {
            "success": True,
            "data": info_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文档信息失败: {str(e)}")


@router.get("/{file_id}/content", summary="获取文档内容")
async def get_document_content(
    file_id: str,
    include_metadata: bool = Query(True, description="是否包含元数据")
):
    """
    获取文档的完整内容和分析信息
    
    Args:
        file_id: 文件ID
        include_metadata: 是否包含元数据信息
    
    Returns:
        文档完整信息包括内容
    """
    try:
        document_info = document_parser.get_file_info(file_id)
        
        if document_info is None:
            raise HTTPException(status_code=404, detail=f"未找到文件ID为 {file_id} 的文档")
        
        if include_metadata:
            return {
                "success": True,
                "data": document_info
            }
        else:
            return {
                "success": True,
                "data": {
                    "file_id": file_id,
                    "content": document_info.get("content", "")
                }
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文档内容失败: {str(e)}")


@router.get("/{file_id}/download", summary="下载原始文档")
async def download_document(file_id: str):
    """
    下载原始文档文件
    
    Args:
        file_id: 文件ID
    
    Returns:
        文件流下载
    """
    try:
        # 获取文档信息
        document_info = document_parser.get_file_info(file_id)
        if document_info is None:
            raise HTTPException(status_code=404, detail=f"未找到文件ID为 {file_id} 的文档")
        
        # 下载文件内容
        file_content = document_parser.download_file(file_id)
        if file_content is None:
            raise HTTPException(status_code=404, detail=f"无法下载文件ID为 {file_id} 的文档")
        
        # 获取文件信息
        filename = document_info.get('filename', 'document')
        file_type = document_info.get('file_type', '.pdf')
        
        # 设置正确的媒体类型
        media_type_map = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword'
        }
        media_type = media_type_map.get(file_type, 'application/octet-stream')
        
        # 处理中文文件名编码问题
        # 对文件名进行URL编码，支持中文
        encoded_filename = urllib.parse.quote(filename, safe='')
        
        # 使用RFC 5987标准的文件名编码格式
        # 同时提供fallback和UTF-8编码的文件名
        content_disposition = f"attachment; filename*=UTF-8''{encoded_filename}"
        
        # 如果文件名只包含ASCII字符，也提供标准的filename参数作为兼容
        try:
            filename.encode('ascii')
            content_disposition = f"attachment; filename=\"{filename}\"; filename*=UTF-8''{encoded_filename}"
        except UnicodeEncodeError:
            # 文件名包含非ASCII字符，只使用UTF-8编码格式
            pass
        
        # 创建文件流
        def iter_file():
            yield file_content
        
        return StreamingResponse(
            iter_file(),
            media_type=media_type,
            headers={
                "Content-Disposition": content_disposition,
                "Content-Length": str(len(file_content)),
                "Cache-Control": "no-cache",
                "Content-Transfer-Encoding": "binary"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载文档失败: {str(e)}")


@router.post("/{file_id}/analyze", summary="文档分析")
async def analyze_document(
    file_id: str,
    analysis_request: Optional[str] = Query(None, description="分析要求")
):
    """
    对指定文档进行分析
    
    Args:
        file_id: 文件ID
        analysis_request: 具体的分析要求
    
    Returns:
        文档分析结果
    """
    try:
        document_info = document_parser.get_file_info(file_id)
        
        if document_info is None:
            raise HTTPException(status_code=404, detail=f"未找到文件ID为 {file_id} 的文档")
        
        content = document_info.get("content", "")
        
        # 构建分析结果
        analysis = {
            "file_id": file_id,
            "document_info": {
                "filename": document_info.get("filename"),
                "file_type": document_info.get("file_type"),
                "file_size": document_info.get("file_size"),
                "uploaded_at": document_info.get("uploaded_at")
            },
            "content_statistics": {
                "content_length": len(content),
                "word_count": len(content.split()) if content else 0,
                "line_count": len(content.split('\n')) if content else 0,
                "paragraph_count": len([p for p in content.split('\n\n') if p.strip()]) if content else 0
            },
            "analysis_request": analysis_request or "基础文档分析",
            "content_preview": content[:500] + "..." if len(content) > 500 else content,
            "analyzed_at": document_info.get("parsed_at")
        }
        
        return {
            "success": True,
            "data": analysis
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文档分析失败: {str(e)}")


@router.delete("/{file_id}", summary="删除文档")
async def delete_document(file_id: str):
    """
    删除指定的文档
    
    Args:
        file_id: 文件ID
    
    Returns:
        删除结果
    """
    try:
        success = document_parser.delete_file(file_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"未找到文件ID为 {file_id} 的文档")
        
        return {
            "success": True,
            "message": "文档删除成功",
            "file_id": file_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除文档失败: {str(e)}") 