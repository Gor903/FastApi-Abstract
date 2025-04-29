import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db import Base
from src.db.models.auth import OTPVerification

if TYPE_CHECKING:
    from src.db.models import EmailVerification


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        info={"description": "UUID primary key, auto-generated and unique."},
    )
    email: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
        nullable=False,
        info={"description": "User email. Unique"},
    )
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
        info={"description": "User name. Unique"},
    )
    full_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        info={"description": "User's full name."},
    )
    bio: Mapped[str] = mapped_column(
        String(255),
        default="",
        nullable=True,
        info={"description": "Information about user"},
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        info={"description": "Account active state"},
    )

    auth: Mapped["Auth"] = relationship(
        back_populates="user",
        uselist=False,
    )
    email_verification: Mapped["EmailVerification"] = relationship(
        back_populates="user",
        uselist=False,
    )
    login_history: Mapped[list["LoginHistory"]] = relationship(
        back_populates="user",
    )
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        back_populates="user",
    )
    otp_verification: Mapped[list["OTPVerification"]] = relationship(
        back_populates="user",
    )

    def __repr__(self):
        return f"<User id={self.id} email={self.email} verified={self.is_verified}>"
