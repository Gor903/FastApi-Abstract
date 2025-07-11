__all__ = [
    "auth",
    "users",
    "MessageResponse",
]

from pydantic import BaseModel

from . import auth, users


class MessageResponse(BaseModel):
    message: str
