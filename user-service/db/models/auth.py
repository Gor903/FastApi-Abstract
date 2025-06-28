import uuid
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import Base

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

    user: Mapped["User"] = relationship(
        back_populates="auth",
    )

    def __repr__(self):
        return f"<Auth user_id={self.user_id}>"


# For next versions
class LoginHistory(Base):
    __tablename__ = "login_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        info={"description": "UUID primary key, auto-generated and unique."},
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        info={"description": "User's UUID"},
    )

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        nullable=False,
        info={"description": "Login datetime"},
    )
    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
        info={"description": "Login active state"},
    )
    device: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        info={"description": "Login device"},
    )
    ip: Mapped[str] = mapped_column(
        String(45),
        nullable=False,
        info={"description": "Login IP"},
    )
    location: Mapped[str] = mapped_column(
        String(100),
        nullable=True,
        info={"description": "Login location"},
    )

    user: Mapped["User"] = relationship(
        back_populates="login_history",
    )

    def __repr__(self):
        return f"<LoginHistory id={self.id} user_id={self.user_id} ip={self.ip}>"


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
        default=datetime.utcnow,
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
        default=lambda: datetime.utcnow() + timedelta(minutes=10),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        back_populates="otp_verification",
    )
