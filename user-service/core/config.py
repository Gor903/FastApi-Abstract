import os
from typing import List, Union

from dotenv import load_dotenv
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI-Abstract"

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "SuperSecretKey")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    SERVER_SECRET_SALT: str = os.getenv("SERVER_SECRET_SALT")
    OTP_LENGTH: int = int(os.getenv("OTP_LENGTH", 8))
    OTP_EXPIRES_MINUTES: int = int(os.getenv("OTP_EXPIRES_MINUTES", 10))
    ACCESS_TOKEN_EXPIRE_HOURS: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", 24))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

    # Service: DB PostgreSQL
    DATABASE_URL: str = (
        "postgresql+asyncpg://"
        + f"{os.getenv('USER_SERVICE_POSTGRES_USER')}:"
        + f"{os.getenv('USER_SERVICE_POSTGRES_PASSWORD')}@"
        + f"{os.getenv('USER_SERVICE_POSTGRES_HOST')}:"
        + f"{os.getenv('USER_SERVICE_POSTGRES_PORT')}/"
        + f"{os.getenv('USER_SERVICE_POSTGRES_DB')}"
    )

    USER_SERVICE_POSTGRES_HOST: str = os.getenv("USER_SERVICE_POSTGRES_HOST")

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()
