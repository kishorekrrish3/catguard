import boto3
from botocore.exceptions import ClientError
from typing import Optional
from app.config import settings


def get_storage_client():
    return boto3.client(
        "s3",
        endpoint_url=f"{'https' if settings.MINIO_SECURE else 'http'}://{settings.MINIO_ENDPOINT}",
        aws_access_key_id=settings.MINIO_ACCESS_KEY,
        aws_secret_access_key=settings.MINIO_SECRET_KEY,
        region_name="us-east-1",
    )


def ensure_bucket_exists() -> None:
    client = get_storage_client()
    try:
        client.head_bucket(Bucket=settings.MINIO_BUCKET)
    except ClientError:
        try:
            client.create_bucket(Bucket=settings.MINIO_BUCKET)
            client.put_bucket_policy(
                Bucket=settings.MINIO_BUCKET,
                Policy=f'{{"Version":"2012-10-17","Statement":[{{"Effect":"Allow","Principal":"*","Action":"s3:GetObject","Resource":"arn:aws:s3:::{settings.MINIO_BUCKET}/*"}}]}}',
            )
        except Exception:
            pass  # Bucket may already exist in race condition


def upload_file(file_bytes: bytes, key: str, content_type: str = "application/octet-stream") -> str:
    client = get_storage_client()
    client.put_object(
        Bucket=settings.MINIO_BUCKET,
        Key=key,
        Body=file_bytes,
        ContentType=content_type,
    )
    proto = "https" if settings.MINIO_SECURE else "http"
    return f"{proto}://{settings.MINIO_ENDPOINT}/{settings.MINIO_BUCKET}/{key}"


def delete_file(key: str) -> None:
    client = get_storage_client()
    client.delete_object(Bucket=settings.MINIO_BUCKET, Key=key)


def generate_presigned_url(key: str, expires: int = 3600) -> str:
    client = get_storage_client()
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.MINIO_BUCKET, "Key": key},
        ExpiresIn=expires,
    )
