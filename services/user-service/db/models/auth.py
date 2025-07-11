import uuid
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from core import settings
from db import Base
from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from db.models import User


class Auth(Base):
    __tablename__ = "auth"

    id: Mapped[int] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        info={"description": "UUID primary key, auto-generated and unique."},
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        info={"description": "User's UUID"},
    )
    hashed_password: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        back_populates="auth",
    )

    def __repr__(self):
        return f"<Auth user_id={self.user_id}>"


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )

    token_hash: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    issued_at: Mapped[datetime] = mapped_column(
        default=datetime.now,
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        nullable=False,
    )
    revoked: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        back_populates="refresh_tokens",
    )

    def __repr__(self):
        return f"<RefreshToken id={self.id} user_id={self.user_id}>"


class OTPVerification(Base):
    __tablename__ = "otp_verification"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    hashed_otp: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    is_used: Mapped[bool] = mapped_column(
        default=False,
        nullable=True,
    )
    expires_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now()
        + timedelta(minutes=settings.OTP_EXPIRES_MINUTES),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        back_populates="otp_verification",
    )

    def __repr__(self):
        return f"<OTPVerification id={self.id} user_id={self.user_id} is_used={self.is_used}>"
