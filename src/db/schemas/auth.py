from operator import xor
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, model_validator


class LoginRequest(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: str

    @model_validator(mode="after")
    def check_email_or_username(self):
        if not xor(self.email is not None, self.username is not None):
            raise ValueError("Provide either 'email' or 'username', but not both.")
        return self


class LoginResponse(BaseModel):
    access_token: str = Field(
        description="Access token",
    )
    refresh_token: str = Field(
        description="Refresh token",
    )
