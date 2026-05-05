import os
import uuid
import shutil
import boto3
from pathlib import Path
from config.settings import get_settings
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)
settings = get_settings()
BASE = Path(settings.STORAGE_LOCAL_PATH)

# ── Initialize S3 client if configured ──
s3_client = None
if settings.STORAGE_BACKEND == "s3":
    try:
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
    except Exception as e:
        logger.error(f"Failed to initialize S3 client: {e}")

def _ensure(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def _generate_key(user_id: str, folder: str, filename: str) -> str:
    """Generate S3 key path."""
    ext = Path(filename).suffix.lower()
    unique_name = f"{uuid.uuid4()}{ext}"
    return f"{folder}/{user_id}/{unique_name}"

def upload_to_s3(file_bytes: bytes, key: str) -> bool:
    """Upload file to S3."""
    try:
        s3_client.put_object(
            Bucket=settings.AWS_S3_BUCKET,
            Key=key,
            Body=file_bytes,
            ServerSideEncryption='AES256'
        )
        return True
    except ClientError as e:
        logger.error(f"S3 upload error: {e}")
        return False

def download_from_s3(key: str) -> bytes:
    """Download file from S3."""
    try:
        response = s3_client.get_object(Bucket=settings.AWS_S3_BUCKET, Key=key)
        return response['Body'].read()
    except ClientError as e:
        logger.error(f"S3 download error: {e}")
        return None

def delete_from_s3(key: str) -> bool:
    """Delete file from S3."""
    try:
        s3_client.delete_object(Bucket=settings.AWS_S3_BUCKET, Key=key)
        return True
    except ClientError as e:
        logger.error(f"S3 delete error: {e}")
        return False

def generate_s3_url(key: str, expires_in: int = 3600) -> str:
    """Generate presigned URL for S3 file."""
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': settings.AWS_S3_BUCKET, 'Key': key},
            ExpiresIn=expires_in
        )
        return url
    except ClientError as e:
        logger.error(f"S3 URL generation error: {e}")
        return None

def upload_path(user_id: str, filename: str) -> Path:
    p = BASE / "uploads" / user_id
    _ensure(p)
    return p / filename

def output_path(user_id: str, filename: str) -> Path:
    p = BASE / "outputs" / user_id
    _ensure(p)
    return p / filename

def temp_path(filename: str) -> Path:
    p = BASE / "temp"
    _ensure(p)
    return p / filename

def save_upload(user_id: str, file_bytes: bytes, original_name: str) -> str:
    """Save upload file to local storage or S3."""
    ext = Path(original_name).suffix.lower()
    unique_name = f"{uuid.uuid4()}{ext}"
    
    if settings.STORAGE_BACKEND == "s3":
        key = _generate_key(user_id, "uploads", original_name)
        if upload_to_s3(file_bytes, key):
            return f"s3://{settings.AWS_S3_BUCKET}/{key}"
        else:
            raise Exception("Failed to upload to S3")
    else:
        dest = upload_path(user_id, unique_name)
        dest.write_bytes(file_bytes)
        return str(dest)

def save_output(user_id: str, file_bytes: bytes, filename: str) -> str:
    """Save output file to local storage or S3."""
    ext = Path(filename).suffix.lower()
    unique_name = f"{uuid.uuid4()}{ext}"
    
    if settings.STORAGE_BACKEND == "s3":
        key = _generate_key(user_id, "outputs", filename)
        if upload_to_s3(file_bytes, key):
            return f"s3://{settings.AWS_S3_BUCKET}/{key}"
        else:
            raise Exception("Failed to upload to S3")
    else:
        dest = output_path(user_id, unique_name)
        dest.write_bytes(file_bytes)
        return str(dest)

def delete_file(path: str):
    """Delete file from local storage or S3."""
    try:
        if path.startswith("s3://"):
            key = path.replace(f"s3://{settings.AWS_S3_BUCKET}/", "")
            delete_from_s3(key)
        else:
            os.remove(path)
    except FileNotFoundError:
        pass

def cleanup_user_temp(user_id: str):
    """Delete all temp files for a user after export."""
    if settings.STORAGE_BACKEND == "s3":
        # For S3, you would need to list and delete all objects with prefix
        # This is a simplified version
        try:
            response = s3_client.list_objects_v2(
                Bucket=settings.AWS_S3_BUCKET,
                Prefix=f"uploads/{user_id}"
            )
            if 'Contents' in response:
                for obj in response['Contents']:
                    delete_from_s3(obj['Key'])
        except ClientError as e:
            logger.error(f"S3 cleanup error: {e}")
    else:
        for folder in ["uploads", "temp"]:
            p = BASE / folder / user_id
            if p.exists():
                shutil.rmtree(p, ignore_errors=True)
