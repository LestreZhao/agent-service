import io
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from pathlib import Path

import PyPDF2
from docx import Document
from minio.error import S3Error

from src.config.minio import get_minio_client, MINIO_BUCKET_NAME, ensure_bucket_exists


class DocumentParser:
    """文档解析器类"""
    
    def __init__(self):
        self.minio_client = get_minio_client()
        ensure_bucket_exists()
    
    def extract_pdf_content(self, file_content: bytes) -> str:
        """提取PDF文档内容"""
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            raise ValueError(f"PDF解析错误: {str(e)}")
    
    def extract_docx_content(self, file_content: bytes) -> str:
        """提取Word文档内容"""
        try:
            docx_file = io.BytesIO(file_content)
            doc = Document(docx_file)
            
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text.strip()
        except Exception as e:
            raise ValueError(f"Word文档解析错误: {str(e)}")
    
    def parse_document(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """解析文档并提取内容"""
        file_ext = Path(filename).suffix.lower()
        
        if file_ext == '.pdf':
            content = self.extract_pdf_content(file_content)
        elif file_ext in ['.docx', '.doc']:
            content = self.extract_docx_content(file_content)
        else:
            raise ValueError(f"不支持的文件类型: {file_ext}")
        
        return {
            "filename": filename,
            "file_type": file_ext,
            "content": content,
            "content_length": len(content),
            "parsed_at": datetime.now().isoformat()
        }
    
    def upload_file(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """上传文件到MinIO并解析"""
        try:
            # 生成唯一的文件ID
            file_id = str(uuid.uuid4())
            object_name = f"{file_id}_{filename}"
            
            # 上传到MinIO
            file_stream = io.BytesIO(file_content)
            self.minio_client.put_object(
                MINIO_BUCKET_NAME,
                object_name,
                file_stream,
                length=len(file_content),
                content_type=self._get_content_type(filename)
            )
            
            # 解析文档内容
            document_info = self.parse_document(file_content, filename)
            document_info.update({
                "file_id": file_id,
                "object_name": object_name,
                "file_size": len(file_content),
                "uploaded_at": datetime.now().isoformat()
            })
            
            return document_info
            
        except S3Error as e:
            raise ValueError(f"文件上传失败: {str(e)}")
        except Exception as e:
            raise ValueError(f"文档处理失败: {str(e)}")
    
    def get_file_info(self, file_id: str) -> Optional[Dict[str, Any]]:
        """根据文件ID获取文件信息"""
        try:
            # 查找以file_id开头的对象
            objects = self.minio_client.list_objects(MINIO_BUCKET_NAME, prefix=file_id)
            
            for obj in objects:
                if obj.object_name.startswith(file_id):
                    # 获取文件内容
                    response = self.minio_client.get_object(MINIO_BUCKET_NAME, obj.object_name)
                    file_content = response.read()
                    response.close()
                    
                    # 解析原始文件名
                    original_filename = obj.object_name[len(file_id) + 1:]  # 去掉file_id和下划线
                    
                    # 解析文档内容
                    document_info = self.parse_document(file_content, original_filename)
                    document_info.update({
                        "file_id": file_id,
                        "object_name": obj.object_name,
                        "file_size": obj.size,
                        "last_modified": obj.last_modified.isoformat() if obj.last_modified else None
                    })
                    
                    return document_info
            
            return None
            
        except S3Error as e:
            raise ValueError(f"获取文件信息失败: {str(e)}")
        except Exception as e:
            raise ValueError(f"文档处理失败: {str(e)}")
    
    def download_file(self, file_id: str) -> Optional[bytes]:
        """下载文件内容"""
        try:
            objects = self.minio_client.list_objects(MINIO_BUCKET_NAME, prefix=file_id)
            
            for obj in objects:
                if obj.object_name.startswith(file_id):
                    response = self.minio_client.get_object(MINIO_BUCKET_NAME, obj.object_name)
                    file_content = response.read()
                    response.close()
                    return file_content
            
            return None
            
        except S3Error as e:
            raise ValueError(f"下载文件失败: {str(e)}")
    
    def delete_file(self, file_id: str) -> bool:
        """删除文件"""
        try:
            objects = self.minio_client.list_objects(MINIO_BUCKET_NAME, prefix=file_id)
            
            for obj in objects:
                if obj.object_name.startswith(file_id):
                    self.minio_client.remove_object(MINIO_BUCKET_NAME, obj.object_name)
                    return True
            
            return False
            
        except S3Error as e:
            raise ValueError(f"删除文件失败: {str(e)}")
    
    def _get_content_type(self, filename: str) -> str:
        """根据文件名获取内容类型"""
        ext = Path(filename).suffix.lower()
        content_types = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword'
        }
        return content_types.get(ext, 'application/octet-stream')


# 创建全局实例
document_parser = DocumentParser() 