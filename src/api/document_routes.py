from fastapi import APIRouter, UploadFile, File, HTTPException
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