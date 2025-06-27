from pydantic_settings import BaseSettings

import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):

    USER_MANAGEMENT_HOST: str = os.getenv("USER_MANAGEMENT_HOST", "user_management")
    USER_MANAGEMENT_PORT: int = int(os.getenv("USER_MANAGEMENT_PORT", "8008"))

    SERVICE1_HOST: str = os.getenv("SERVICE1_HOST", "service1")
    SERVICE1_PORT: int = int(os.getenv("SERVICE1_PORT", "8001"))

    SERVICE2_HOST: str = os.getenv("SERVICE2_HOST", "service2")
    SERVICE2_PORT: int = int(os.getenv("SERVICE2_PORT", "8002"))

    class Config:
        env_file = "../.env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()
