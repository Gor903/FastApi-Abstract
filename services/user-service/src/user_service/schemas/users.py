import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, constr, model_validator
from user_service.utils import password_validator


class UserRegister(BaseModel):
    email: EmailStr = Field(
        ...,
        description="User's email address. Must be unique and valid.",
    )
    username: constr(min_length=3, max_length=50) = Field(
        ...,
        description="Unique username for the user. 3-50 characters.",
    )
    full_name: constr(min_length=1, max_length=50) = Field(
        ...,
        description="User's full name. 1-50 characters.",
    )
    password: constr(min_length=8, max_length=128) = Field(
        ...,
        description="Password for the account. 8-128 characters.",
    )

    @model_validator(mode="after")
    def check_password(self):
        password_validator(self.password)
        return self

    class Config:
        from_attributes = True


class UserShortResponse(BaseModel):
    id: uuid.UUID = Field(..., description="Unique identifier for the user (UUID).")
    username: str = Field(
        ...,
        description="Unique username of the user.",
    )
    full_name: str = Field(
        ...,
        description="Full name of the user.",
    )
    is_active: bool = Field(
        ...,
        description="Indicates whether the user's account is active.",
    )

    class Config:
        from_attributes = True


class UserResponse(UserShortResponse):
    email: EmailStr
    bio: str | None
    age: int | None
    profession: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    age: Optional[int] = Field(None, ge=0, le=100)
    profession: Optional[str] = Field(None, max_length=100)
    full_name: Optional[str] = Field(None, max_length=50)
    bio: Optional[str] = Field(None, max_length=255)


class UserIdResponse(BaseModel):
    user_id: uuid.UUID = Field(
        ...,
        description="Unique identifier for the user (UUID).",
    )

    class Config:
        from_attributes = True
