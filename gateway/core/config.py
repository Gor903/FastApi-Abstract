import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = os.getenv("PROJECT_NAME")

    USER_SERVICE_HOST: str = os.getenv("USER_SERVICE_HOST")
    USER_SERVICE_PORT: str = os.getenv("USER_SERVICE_PORT")

    class Config:
        env_file = "../.env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()
