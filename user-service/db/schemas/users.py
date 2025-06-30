import uuid

from pydantic import BaseModel, EmailStr, Field, constr


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
    bio: constr(max_length=255) = Field(
        default="",
        description="Optional short bio about the user. Max 255 characters.",
    )

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: uuid.UUID = Field(..., description="Unique identifier for the user (UUID).")
    email: EmailStr = Field(
        ...,
        description="User's email address.",
    )
    username: str = Field(
        ...,
        description="Unique username of the user.",
    )
    full_name: str = Field(
        ...,
        description="Full name of the user.",
    )
    bio: str = Field(
        ...,
        description="Short biography or description of the user.",
    )
    is_active: bool = Field(
        ...,
        description="Indicates whether the user's account is active.",
    )

    class Config:
        from_attributes = True


class UserIdResponse(BaseModel):
    user_id: uuid.UUID = Field(
        ...,
        description="Unique identifier for the user (UUID).",
    )

    class Config:
        from_attributes = True
