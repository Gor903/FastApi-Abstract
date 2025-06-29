from pydantic import BaseModel

from .auth import LoginRequest, LoginResponse
from .users import UserIdResponse, UserRegister, UserResponse

__all__ = [
    "UserRegister",
    "UserResponse",
    "UserIdResponse",
    "LoginResponse",
    "LoginRequest",
]


class MessageResponse(BaseModel):
    message: str
