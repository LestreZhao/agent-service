from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Optional
import io

from src.tools.document_parser import document_parser

router = APIRouter(prefix="/documents", tags=["文档管理"])


@router.post("/upload", summary="上传文档")
async def upload_document(file: UploadFile = File(...)):
    """
    上传文档文件到MinIO并解析内容
    
    支持的文件格式：
    - PDF (.pdf)
    - Word (.docx, .doc)
    
    返回：
    - file_id: 文件唯一标识符
    - download_url: 获取文档信息的API地址
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
        
        # 构造下载URL
        file_id = document_info['file_id']
        download_url = f"/api/documents/{file_id}"
        
        return {
            "success": True,
            "message": "文档上传成功",
            "file_id": file_id,
            "download_url": download_url,
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


@router.get("/{file_id}", summary="获取文档信息")
async def get_document_info(
    file_id: str,
    include_content: bool = Query(True, description="是否包含完整文档内容")
):
    """
    根据文件ID获取文档信息
    
    参数：
    - file_id: 文件唯一标识符
    - include_content: 是否包含完整文档内容（默认为True）
    
    返回：
    - 文档详细信息和内容
    """
    try:
        document_info = document_parser.get_file_info(file_id)
        
        if document_info is None:
            raise HTTPException(status_code=404, detail="文档未找到")
        
        # 如果不需要完整内容，只返回预览
        if not include_content:
            content = document_info.get('content', '')
            document_info['content'] = content[:500] + "..." if len(content) > 500 else content
            document_info['content_preview'] = True
        
        return {
            "success": True,
            "data": document_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文档信息失败: {str(e)}")


@router.get("/{file_id}/download", summary="下载原始文档")
async def download_document(file_id: str):
    """
    下载原始文档文件
    
    参数：
    - file_id: 文件唯一标识符
    
    返回：
    - 原始文档文件流
    """
    try:
        # 先获取文档信息以获得原始文件名
        document_info = document_parser.get_file_info(file_id)
        
        if document_info is None:
            raise HTTPException(status_code=404, detail="文档未找到")
        
        # 下载文件内容
        file_content = document_parser.download_file(file_id)
        
        if file_content is None:
            raise HTTPException(status_code=404, detail="文件内容未找到")
        
        # 根据文件类型设置响应头
        filename = document_info['filename']
        file_ext = document_info['file_type']
        
        content_types = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword'
        }
        
        content_type = content_types.get(file_ext, 'application/octet-stream')
        
        return StreamingResponse(
            io.BytesIO(file_content),
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载文件失败: {str(e)}")


@router.delete("/{file_id}", summary="删除文档")
async def delete_document(file_id: str):
    """
    删除指定的文档
    
    参数：
    - file_id: 文件唯一标识符
    
    返回：
    - 删除结果
    """
    try:
        success = document_parser.delete_file(file_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="文档未找到")
        
        return {
            "success": True,
            "message": "文档删除成功",
            "file_id": file_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除文档失败: {str(e)}")


@router.post("/{file_id}/analyze", summary="分析文档内容")
async def analyze_document(
    file_id: str,
    analysis_request: Optional[str] = None
):
    """
    分析文档内容
    
    参数：
    - file_id: 文件唯一标识符
    - analysis_request: 特定的分析要求（可选）
    
    返回：
    - 文档分析结果
    """
    try:
        document_info = document_parser.get_file_info(file_id)
        
        if document_info is None:
            raise HTTPException(status_code=404, detail="文档未找到")
        
        content = document_info.get("content", "")
        
        # 基础文档分析
        analysis = {
            "file_id": file_id,
            "filename": document_info.get("filename"),
            "file_type": document_info.get("file_type"),
            "file_size": document_info.get("file_size"),
            "content_length": len(content),
            "word_count": len(content.split()) if content else 0,
            "line_count": len(content.split('\n')) if content else 0,
            "paragraph_count": len([p for p in content.split('\n\n') if p.strip()]) if content else 0,
            "analysis_request": analysis_request,
            "content_preview": content[:500] + "..." if len(content) > 500 else content,
            "analyzed_at": document_info.get("parsed_at")
        }
        
        # 如果有特定分析要求，可以在这里扩展分析逻辑
        if analysis_request:
            analysis["custom_analysis"] = f"根据要求'{analysis_request}'的分析正在进行中..."
        
        return {
            "success": True,
            "data": analysis
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析文档失败: {str(e)}") 