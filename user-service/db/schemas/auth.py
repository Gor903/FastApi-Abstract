import uuid
from operator import xor
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, model_validator



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
        if not 7 < len(self.password) < 16:
            raise ValueError("Password must be between 8 and 15 characters")
        if not any(char.isdigit() for char in self.password):
            raise ValueError("Password must contain at least 1 number")
        if not any(char.isalpha() for char in self.password):
            raise ValueError("Password must contain at least 1 letter")
        if not any(char.isupper() for char in self.password):
            raise ValueError("Password must contain at least 1 uppercase letter")
        if all(char.isalnum() for char in self.password):
            raise ValueError("Password must contain at least 1 symbol")
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
        if not 7 < len(self.new_password) < 16:
            raise ValueError("Password must be between 8 and 15 characters")
        if not any(char.isdigit() for char in self.new_password):
            raise ValueError("Password must contain at least 1 number")
        if not any(char.isalpha() for char in self.new_password):
            raise ValueError("Password must contain at least 1 letter")
        if not any(char.isupper() for char in self.new_password):
            raise ValueError("Password must contain at least 1 uppercase letter")
        if all(char.isalnum() for char in self.new_password):
            raise ValueError("Password must contain at least 1 symbol")
        return self


class PasswordResetOTP(LoginRequest):
    otp: str = Field(
        description="OTP",
    )
