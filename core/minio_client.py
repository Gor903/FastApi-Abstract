from minio import Minio

from core import settings

_minio = Minio(
    endpoint=settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ROOT_USER,
    secret_key=settings.MINIO_ROOT_PASSWORD,
    secure=False,
)

if not _minio.bucket_exists("media"):
    _minio.make_bucket("media")
