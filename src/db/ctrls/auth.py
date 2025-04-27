import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
from datetime import datetime, timedelta

from src.core import settings
from src.db.services import get_data_from_table, insert_into_table, update_model
from src.db.models import Auth, EmailVerification, RefreshToken, User
from src.tasks import send_verification_email_task
from src.utils import (
    hash_refresh_token,
    hash_password,
    verify_password,
    create_token,
    decode_token,
)


# READY
async def get_refresh_token(
    token_id: uuid.UUID,
    db: AsyncSession,
):
    query = select(RefreshToken).where(RefreshToken.id == token_id)
    refresh_token = await get_data_from_table(
        query=query,
        session=db,
    )

    return refresh_token


# READY
async def update_refresh_token(
    data: dict,
    id: uuid.UUID,
    db: AsyncSession,
):
    refresh_token = await update_model(
        model_class=RefreshToken,
        id=id,
        session=db,
        schema=data,
    )

    return refresh_token


# READY
async def create_refresh_token(
    user: User,
    db: AsyncSession,
):
    exp = timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
    )

    refresh_token = create_token(
        data={
            "sub": user.username,
            "email": user.email,
            "id": str(user.id),
        },
        expires_delta=exp,
    )

    token_hash = hash_refresh_token(refresh_token)

    refresh_token_db = await insert_into_table(
        model_class=RefreshToken,
        session=db,
        schema={
            "user_id": user.id,
            "token_hash": token_hash,
            "expires_at": datetime.utcnow() + exp,
        },
    )

    if not refresh_token_db:
        return False

    return refresh_token, refresh_token_db.id


# READY
async def create_access_token(
    user: User,
    refresh_token_id: uuid.UUID,
):
    access_token = create_token(
        data={
            "sub": user.username,
            "email": user.email,
            "id": str(user.id),
            "refresh_token_id": refresh_token_id,
        },
        expires_delta=timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        ),
    )

    return access_token


# READY
async def insert_refresh_token(
    user_id: uuid.UUID,
    token_hash: str,
    expires_at: datetime,
    db: AsyncSession,
):
    result = await insert_into_table(
        model_class=RefreshToken,
        session=db,
        schema={
            "user_id": user_id,
            "token_hash": token_hash,
            "expires_at": expires_at,
        },
    )

    return result


# READY
async def verify_authorization(
    user: User,
    password: str,
    db: AsyncSession,
):
    query = select(Auth.hashed_password).where(Auth.user_id == user.id)
    hashed_password = await get_data_from_table(
        query=query,
        session=db,
    )

    is_verified = await verify_password(
        password,
        hashed_password,
    )

    return is_verified


# READY
async def save_password(
    user_id: uuid.UUID,
    password: str,
    db: AsyncSession,
):
    hashed_password = await hash_password(password)

    auth_data = {
        "user_id": user_id,
        "hashed_password": hashed_password,
    }

    auth = await insert_into_table(
        model_class=Auth,
        session=db,
        schema=auth_data,
    )

    return auth


async def create_email_verification_token(
    user_id: uuid.UUID,
):
    token = create_token(
        data={
            "sub": str(user_id),
            "type": "email_verification",
        },
        expires_delta=timedelta(
            hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRES_HOURS,
        ),
    )
    return token


# READY
async def create_email_verification(
    user_id: uuid.UUID,
    user_email: str,
    db: AsyncSession,
):
    token = await create_email_verification_token(
        user_id=user_id,
    )

    email_verification = await insert_into_table(
        model_class=EmailVerification,
        session=db,
        schema={
            "user_id": user_id,
            "token": token,
        },
    )

    send_verification_email_task.delay(
        email=user_email,
        token=token,
    )

    return email_verification


# READY
async def refresh_email_verification(
    ev_id: uuid.UUID,
    user_id: uuid.UUID,
    user_email: str,
    db: AsyncSession,
):
    token = await create_email_verification_token(
        user_id=user_id,
    )

    email_verification = await update_email_verification(
        ev_id=ev_id,
        data={
            "token": token,
            "expires_at": datetime.utcnow()
            + timedelta(
                hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRES_HOURS,
            ),
            "created_at": datetime.utcnow(),
        },
        db=db,
    )

    send_verification_email_task.delay(
        email=user_email,
        token=token,
    )

    return email_verification


# READY
async def get_id_from_email_token(token: str) -> str | None:
    data = decode_token(token)
    return data.get("sub")


# READY
async def verify_email_token(
    token: str,
    user_id: uuid.UUID,
    db: AsyncSession,
):
    query = (
        select(EmailVerification)
        .where(EmailVerification.user_id == user_id)
        .where(EmailVerification.token == token)
    )

    email_verification = await get_data_from_table(
        query=query,
        session=db,
    )

    if (
        not email_verification
        or email_verification.is_used
        or email_verification.expires_at < datetime.utcnow()
    ):
        return False

    return email_verification


# READY
async def get_ev_by_user_id(
    user_id: uuid.UUID,
    db: AsyncSession,
):
    query = select(EmailVerification).where(EmailVerification.user_id == user_id)

    verification = await get_data_from_table(
        query=query,
        session=db,
    )

    return verification


# READY
async def update_email_verification(
    ev_id: uuid.UUID,
    data: dict[str, Any],
    db: AsyncSession,
):
    res = await update_model(
        model_class=EmailVerification,
        id=ev_id,
        session=db,
        schema=data,
    )

    return res
