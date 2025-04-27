from typing import List, Union
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI-Abstract"

    DOMAIN_NAME: str = os.getenv("DOMAIN_NAME")

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "SuperSecretKey")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    SERVER_SECRET_SALT: str = os.getenv("SERVER_SECRET_SALT")
    EMAIL_VERIFICATION_TOKEN_EXPIRES_HOURS: int = int(
        os.getenv("EMAIL_VERIFICATION_TOKEN_EXPIRES_HOURS", 15)
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

    # CORS
    CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    # Service: Database
    DATABASE_URL: str = (
        "postgresql+asyncpg://"
        + f"{os.getenv('POSTGRES_USER')}:"
        + f"{os.getenv('POSTGRES_PASSWORD')}@"
        + f"{os.getenv('POSTGRES_HOST')}:"
        + f"{os.getenv('POSTGRES_PORT')}/"
        + f"{os.getenv('POSTGRES_DB')}"
    )

    # Service: Celery
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv(
        "CELERY_RESULT_BACKEND", "redis://redis:6379/1"
    )

    # Service: Mailing
    SMTP_HOST: str = os.getenv("SMTP_HOST")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT"))
    SMTP_USER: str = os.getenv("SMTP_USER")
    SMTP_PASS: str = os.getenv("SMTP_PASS")

    # Service: MinIO
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT")
    MINIO_ROOT_USER: str = os.getenv("MINIO_ROOT_USER")
    MINIO_ROOT_PASSWORD: str = os.getenv("MINIO_ROOT_PASSWORD")

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()
