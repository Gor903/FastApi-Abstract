import uuid
import bcrypt
import asyncio
import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, Union
from datetime import datetime, timedelta

from src.core import settings
from src.db import models
from src.db.services import get_data_from_table, insert_into_table, update_model
from src.db.models import Auth, EmailVerification, RefreshToken, User
from src.tasks import send_verification_email_task


async def create_auth_tokens(
    user: User,
    db: AsyncSession,
):
    data = {
        "sub": user.username,
        "email": user.email,
        "id": str(user.id),
    }
    exp = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    refresh_token = create_token(
        data=data,
        expires_delta=exp,
    )

    token_hash = await hash_string(refresh_token)

    _refresh_token = await insert_refresh_token(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.utcnow() + exp,
        db=db,
    )

    if not _refresh_token[0]:
        return _refresh_token[1]

    data["refresh_token_id"] = str(_refresh_token[1].id)

    exp = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_token(
        data=data,
        expires_delta=exp,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


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

    is_verified = await verify_hashed_string(
        password,
        hashed_password,
    )

    return is_verified


async def save_password(
    user_id: uuid.UUID,
    password: str,
    db: AsyncSession,
):
    hashed_password = await hash_string(password)

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


async def create_email_verification(
    user_id: uuid.UUID,
    user_email: str,
    db: AsyncSession,
):
    data = {
        "sub": str(user_id),
        "type": "email_verification",
    }
    expires = timedelta(hours=24)
    token = create_token(
        data,
        expires,
    )

    model_data = {
        "user_id": user_id,
        "token": token,
    }

    await insert_into_table(
        model_class=EmailVerification,
        session=db,
        schema=model_data,
    )

    send_verification_email_task.delay(
        email=user_email,
        token=token,
    )

    return {"message": "Email verification sent!"}


async def hash_string(value: str) -> str:
    hashed = await asyncio.to_thread(
        bcrypt.hashpw,
        value.encode(),
        bcrypt.gensalt(),
    )

    return hashed.decode()


async def verify_hashed_string(plain_value: str, hashed_value: str) -> bool:
    is_valid = await asyncio.to_thread(
        bcrypt.checkpw,
        plain_value.encode(),
        hashed_value.encode(),
    )

    return is_valid


async def get_id_from_email_token(token: str) -> str | None:
    data = decode_token(token)
    return data.get("sub")


async def verify_email_token(
    token: str, user_id: uuid.UUID, db: AsyncSession
) -> tuple[bool | object, str]:
    query = (
        select(EmailVerification)
        .where(EmailVerification.user_id == user_id)
        .where(EmailVerification.token == token)
    )

    email_verification = await get_data_from_table(
        query=query,
        session=db,
    )

    if not email_verification:
        return False, "Verification failed"

    if email_verification.is_used:
        return False, "Email already verified!"

    if email_verification.expires_at < datetime.utcnow():
        return False, "Token expired!"

    return email_verification, "Verified successfully!"


async def get_ev_by_user_id(
    user_id: uuid.UUID,
    db: AsyncSession,
) -> tuple[bool | object, str]:
    query = select(EmailVerification).where(EmailVerification.user_id == user_id)

    verification = await get_data_from_table(
        query=query,
        session=db,
    )

    if not verification:
        return False, "Verification not found!"

    if verification.is_used:
        return False, "Email already verified!"

    return verification, "Verified found successfully!"


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


def create_token(data: dict, expires_delta: Union[timedelta, None]) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    return encoded_jwt


def decode_token(token: str) -> Union[dict[str, Any], None]:
    try:
        payload = jwt.decode(
            token,
            key=settings.SECRET_KEY,
            algorithms=[
                settings.ALGORITHM,
            ],
        )
        return payload
    except jwt.ExpiredSignatureError:
        print("Token has expired.")
        return None
    except jwt.InvalidTokenError:
        print("Invalid token.")
        return None
