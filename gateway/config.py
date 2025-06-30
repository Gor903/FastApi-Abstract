import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):

    USER_SERVICE_HOST: str = os.getenv("USER_SERVICE_HOST")
    USER_SERVICE_PORT: int = int(os.getenv("USER_SERVICE_PORT"))

    class Config:
        env_file = "../.env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()
