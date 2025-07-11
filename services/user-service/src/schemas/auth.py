from operator import xor
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, model_validator
from src.utils import password_validator


class EmailOrUsernameRequest(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None

    @model_validator(mode="after")
    def check_email_or_username(self):
        if not xor(self.email is not None, self.username is not None):
            raise ValueError("Provide either 'email' or 'username', but not both.")
        return self


class LoginRequest(EmailOrUsernameRequest):
    password: str

    @model_validator(mode="after")
    def check_password(self):
        password_validator(self.password)
        return self


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(
        description="Refresh token",
    )


class LoginResponse(BaseModel):
    access_token: str = Field(
        description="Access token",
    )
    refresh_token: str = Field(
        description="Refresh token",
    )


class OTPRequest(EmailOrUsernameRequest):
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
