import random
import string
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from user_service.core import settings
from user_service.db.models import Auth, OTPVerification, RefreshToken, User
from user_service.db.services import (
    get_data_from_table,
    insert_into_table,
    update_model,
)
from user_service.exceptions.http_exceptions import CTRLException
from user_service.notific_ocean import async_request
from user_service.utils import create_token, hash_password, hash_token, verify_password

from .users import get_user


async def register(
    data: Dict[str, Any],
    db: AsyncSession,
):
    password = data.pop("password")

    user = await insert_into_table(
        model_class=User,
        session=db,
        schema=data,
        auto_flush=True,
    )

    hashed_password = await hash_password(password)

    await insert_into_table(
        model_class=Auth,
        session=db,
        schema={
            "user_id": user.id,
            "hashed_password": hashed_password,
        },
        auto_commit=True,
    )

    otp = "".join(random.choices(string.digits, k=settings.OTP_LENGTH))

    hashed_otp = await hash_password(otp)

    await insert_into_table(
        model_class=OTPVerification,
        session=db,
        schema={
            "user_id": str(user.id),
            "hashed_otp": hashed_otp,
        },
    )

    await async_request(
        method="POST",
        base_url=f"http://{settings.BACKGROUND_HOST}:{settings.BACKGROUND_PORT}",
        endpoint="/notification/mail",
        body={
            "to": data.get("email"),
            "subject": "Verify your email",
            "body": f"One time password: {otp}",
        },
    )

    return user


async def send_otp(
    data: Dict[str, Any],
    db: AsyncSession,
):
    user = await get_user(
        username=data.get("username"),
        email=data.get("email"),
        db=db,
    )

    query = (
        select(func.count())
        .select_from(OTPVerification)
        .where(OTPVerification.user_id == user.id)
        .where(OTPVerification.is_used == False)
        .where(OTPVerification.expires_at > datetime.now())
    )

    otp_cunt = await get_data_from_table(
        query=query,
        session=db,
    )

    if otp_cunt is None:
        raise CTRLException(
            detail="OTP not found",
        )

    if otp_cunt > 0:
        raise CTRLException(
            detail="User has OTP!!",
        )

    otp = "".join(random.choices(string.digits, k=settings.OTP_LENGTH))

    hashed_otp = await hash_password(otp)

    await insert_into_table(
        model_class=OTPVerification,
        session=db,
        schema={
            "user_id": str(user.id),
            "hashed_otp": hashed_otp,
        },
    )

    await async_request(
        method="POST",
        base_url=f"http://{settings.NOTIFICATION_HOST}:{settings.NOTIFICATION_PORT}",
        endpoint="/notification/mail",
        body={
            "to": user.email,
            "subject": "Verify your email",
            "body": f"One time password: {otp}",
        },
    )


async def verify_otp(
    data: Dict[str, Any],
    db: AsyncSession,
):
    user = await get_user(
        username=data.get("username"),
        email=data.get("email"),
        db=db,
    )

    otp_db = await get_otp(
        user_id=user.id,
        db=db,
    )

    await update_model(
        model_class=OTPVerification,
        id=otp_db.id,
        schema={
            "is_used": True,
        },
        session=db,
    )

    authorization = await verify_password(
        plain_password=data.get("otp"),
        hashed_password=otp_db.hashed_otp,
    )

    if not authorization:
        raise CTRLException(
            detail="OTP is invalid",
        )

    await update_model(
        model_class=User,
        id=user.id,
        schema={
            "is_verified": True,
        },
        session=db,
    )

    return user


async def login(
    data: Dict[str, Any],
    db: AsyncSession,
):
    user = await get_user(
        username=data.get("username"),
        email=data.get("email"),
        db=db,
    )

    if not user.is_verified:
        raise CTRLException(
            detail="Email is not verified",
        )

    authorization = await verify_authorization(
        user_id=user.id,
        password=data.get("password"),
        db=db,
    )

    if not authorization:
        raise CTRLException(detail="Invalid username or password")

    data = {
        "user": user,
    }

    tokens = await create_tokens(
        data=data,
        db=db,
    )

    return tokens


async def reset_password(
    data: Dict[str, Any],
    db: AsyncSession,
):
    old_password = data.get("old_password")
    new_password = data.get("new_password")
    user_id = data.get("user_id")

    authorization = await verify_authorization(
        user_id=user_id,
        password=old_password,
        db=db,
    )

    if not authorization:
        raise CTRLException(
            detail="Invalid username or password",
        )

    data = {
        "user_id": user_id,
        "password": new_password,
    }

    await update_password(
        data=data,
        db=db,
    )

    return {
        "message": "Password updated successfully",
    }


async def reset_password_otp(
    data: Dict[str, Any],
    db: AsyncSession,
):
    user = await verify_otp(
        data=data,
        db=db,
    )

    data["user_id"] = user.id

    await update_password(
        data=data,
        db=db,
    )

    return {
        "message": "Password updated successfully",
    }


async def refresh(
    data: Dict[str, Any],
    db: AsyncSession,
):
    token_db = await get_refresh_token(
        data=data,
        db=db,
    )

    await update_model(
        model_class=RefreshToken,
        id=token_db.id,
        schema={
            "revoked": True,
        },
        session=db,
    )

    user = await get_user(
        id=token_db.user_id,
        db=db,
    )

    data = {
        "user": user,
    }

    tokens = await create_tokens(
        data=data,
        db=db,
    )

    return tokens


async def logout(
    data: Dict[str, Any],
    db: AsyncSession,
):
    token_db = await get_refresh_token(
        data=data,
        db=db,
    )

    await update_model(
        model_class=RefreshToken,
        id=token_db.id,
        schema={
            "revoked": True,
        },
        session=db,
    )

    return {"message": "Successfully logged out"}


# --------------------


async def verify_authorization(
    user_id: uuid.UUID,
    password: str,
    db: AsyncSession,
):
    user = await get_user(
        id=user_id,
        db=db,
    )

    query = select(Auth).where(Auth.user_id == user.id)

    auth = await get_data_from_table(
        query=query,
        session=db,
    )

    if not auth:
        raise CTRLException(detail="User credentials not found")

    return await verify_password(
        plain_password=password,
        hashed_password=auth.hashed_password,
    )


async def create_tokens(
    data: Dict[str, Any],
    db: AsyncSession,
):
    user = data.get("user")

    refresh_token_expire = timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
    )

    refresh_token = create_token(
        data={
            "sub": user.username,
            "email": user.email,
            "id": str(user.id),
            "anchor": str(uuid.uuid4()),
        },
        expires_delta=refresh_token_expire,
    )

    refresh_token_db = await insert_into_table(
        model_class=RefreshToken,
        session=db,
        schema={
            "user_id": str(user.id),
            "token_hash": hash_token(refresh_token),
            "expires_at": datetime.now() + refresh_token_expire,
        },
        auto_commit=True,
    )

    access_token = create_token(
        data={
            "sub": user.username,
            "email": user.email,
            "user_id": str(user.id),
            "refresh_token_id": str(refresh_token_db.id),
        },
        expires_delta=timedelta(
            hours=settings.ACCESS_TOKEN_EXPIRE_HOURS,
        ),
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


async def get_otp(
    user_id: str,
    db: AsyncSession,
):
    query = (
        select(OTPVerification)
        .where(OTPVerification.user_id == user_id)
        .where(OTPVerification.is_used == False)
        .where(OTPVerification.expires_at > datetime.now())
    )

    otp_db = await get_data_from_table(
        query=query,
        session=db,
    )

    if not otp_db:
        raise CTRLException(
            detail="No valid OTP found",
        )

    return otp_db


async def update_password(
    data: Dict[str, Any],
    db: AsyncSession,
):
    user_id = data.get("user_id")

    query = select(Auth).where(Auth.user_id == user_id)

    auth = await get_data_from_table(
        query=query,
        session=db,
    )

    if not auth:
        raise CTRLException(
            detail="User credentials not found",
        )

    hashed_password = await hash_password(data.get("password"))

    await update_model(
        model_class=Auth,
        id=auth.id,
        schema={
            "hashed_password": hashed_password,
        },
        session=db,
    )


async def get_refresh_token(
    data: Dict[str, Any],
    db: AsyncSession,
):
    refresh_token = data.get("refresh_token")

    query = select(RefreshToken).where(
        RefreshToken.token_hash == hash_token(refresh_token)
    )

    token_db = await get_data_from_table(
        query=query,
        session=db,
    )

    if not token_db:
        raise CTRLException(
            detail="Valid refresh token not found",
        )

    if token_db.revoked or token_db.expires_at < datetime.now():
        raise CTRLException(
            detail="Token revoked",
        )

    return token_db
