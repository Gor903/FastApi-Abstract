import io
from minio import Minio
import uuid
from src.core import settings

_minio = Minio(
    endpoint=settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ROOT_USER,
    secret_key=settings.MINIO_ROOT_PASSWORD,
    secure=False,
)

if not _minio.bucket_exists("media"):
    _minio.make_bucket("media")


def upload_user_file(
    user_id: int,
    file_bytes: bytes,
    filename: str,
    content_type: str,
    file_type: str = "profile",
) -> str:

    unique_name = f"{uuid.uuid4().hex}_{filename}"
    object_path = f"user_{user_id}/{file_type}/{unique_name}"

    file_stream = io.BytesIO(file_bytes)  # Convert to file-like object

    _minio.put_object(
        bucket_name="media",
        object_name=object_path,
        data=file_stream,
        length=len(file_bytes),
        content_type=content_type,
    )

    return f"http://{settings.MINIO_ENDPOINT}/{object_path}"
