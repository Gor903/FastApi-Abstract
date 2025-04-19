import uuid
from sqlalchemy import String, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from typing import TYPE_CHECKING

from src.db import Base

if TYPE_CHECKING:
    from src.db.models import EmailVerification


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    email: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
        nullable=False,
    )
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )
    full_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    bio: Mapped[str] = mapped_column(
        String(255),
        default="",
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
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

    def __repr__(self):
        return f"<User id={self.id} email={self.email} verified={self.is_verified}>"
