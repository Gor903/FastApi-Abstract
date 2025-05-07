import io
import uuid

from core import minio, settings


def upload_image(
    user_id: int,
    file_bytes: bytes,
    filename: str,
    content_type: str,
    file_type: str = "profile",
) -> str:
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    object_path = f"user_{user_id}/{file_type}/{unique_name}"

    file_stream = io.BytesIO(file_bytes)

    minio.put_object(
        bucket_name="media",
        object_name=object_path,
        data=file_stream,
        length=len(file_bytes),
        content_type=content_type,
    )

    return f"http://{settings.MINIO_ENDPOINT}/{object_path}"
