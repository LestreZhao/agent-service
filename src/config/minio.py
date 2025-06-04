import os
from minio import Minio
from minio.error import S3Error

# MinIO 配置
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME", "fusionai-documents")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"

def get_minio_client():
    """获取MinIO客户端实例"""
    return Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=MINIO_SECURE
    )

def ensure_bucket_exists():
    """确保存储桶存在"""
    client = get_minio_client()
    try:
        if not client.bucket_exists(MINIO_BUCKET_NAME):
            client.make_bucket(MINIO_BUCKET_NAME)
            print(f"Created bucket: {MINIO_BUCKET_NAME}")
    except S3Error as e:
        print(f"Error creating bucket: {e}")
        raise 