import uuid
from operator import xor
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, model_validator

from src.utils import password_validator


class LoginRequest(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: str

    @model_validator(mode="after")
    def check_email_or_username(self):
        if not xor(self.email is not None, self.username is not None):
            raise ValueError("Provide either 'email' or 'username', but not both.")
        return self

    @model_validator(mode="after")
    def check_password(self):
        password_validator(self.password)
        return self


class LoginResponse(BaseModel):
    access_token: str = Field(
        description="Access token",
    )
    refresh_token: str = Field(
        description="Refresh token",
    )


class OTPRequest(BaseModel):
    user_id: uuid.UUID = Field(
        description="User ID",
    )
    otp: str = Field(
        description="OTP",
    )


class PasswordResset(BaseModel):
    old_password: str
    new_password: str

    @model_validator(mode="after")
    def check_password(self):
        password_validator(self.new_password)
        return self


class PasswordResetOTP(LoginRequest):
    otp: str = Field(
        description="OTP",
    )
