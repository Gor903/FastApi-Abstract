import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from db import Base
from sqlalchemy import Boolean, CheckConstraint, DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from db.models import Auth, OTPVerification, RefreshToken


class User(Base):
    __tablename__ = "users"
    __table_args__ = (CheckConstraint("age BETWEEN 0 AND 100", name="check_age_range"),)

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
        nullable=True,
        info={"description": "Information about user"},
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        info={"description": "Account active state"},
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        info={"description": "Account verification state"},
    )

    age: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
    )

    profession: Mapped[str] = mapped_column(
        String(100),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    auth: Mapped["Auth"] = relationship(
        back_populates="user",
        uselist=False,
    )
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        back_populates="user",
    )
    otp_verification: Mapped[list["OTPVerification"]] = relationship(
        back_populates="user",
    )

    def __repr__(self):
        return f"<User id={self.id} email={self.email} verified={self.is_verified}>"
