from pydantic import BaseModel

from .auth import LoginRequest, LoginResponse
from .users import UserRegister, UserResponse

__all__ = [
    "UserRegister",
    "UserResponse",
    "LoginResponse",
    "LoginRequest",
]


class MessageResponse(BaseModel):
    message: str
