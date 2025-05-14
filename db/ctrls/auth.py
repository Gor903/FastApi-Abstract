import random
import string
import uuid
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core import settings
from db.models import Auth, RefreshToken, User
from db.models.auth import OTPVerification
from db.services import (
    delete_record,
    get_data_from_table,
    insert_into_table,
    update_model,
)
from src.tasks import send_email_task
from src.utils import (
    create_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)


async def get_refresh_token_by_id(
    token_id: uuid.UUID,
    db: AsyncSession,
):
    query = select(RefreshToken).where(RefreshToken.id == token_id)
    refresh_token = await get_data_from_table(
        query=query,
        session=db,
    )

    return refresh_token


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
            "anchor": str(uuid.uuid4()),
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
            hours=settings.ACCESS_TOKEN_EXPIRE_HOURS,
        ),
    )

    return access_token


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

    is_verified = await verify_password(
        password,
        hashed_password,
    )

    return is_verified


async def verify_otp(
    user_id: uuid.UUID,
    otp: str,
    db: AsyncSession,
):
    otp_db = await get_otp(
        user_id=user_id,
        db=db,
    )

    is_verified = await verify_password(
        plain_password=otp,
        hashed_password=otp_db.hashed_otp,
    )

    await update_model(
        model_class=OTPVerification,
        id=otp_db.id,
        schema={
            "is_used": True,
        },
        session=db,
    )

    return is_verified


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


async def update_password(
    user_id: uuid.UUID,
    password: str,
    db: AsyncSession,
):
    query = select(Auth).where(Auth.user_id == user_id)
    auth = await get_data_from_table(
        query=query,
        session=db,
    )

    hashed_password = await hash_password(password)

    res = await update_model(
        model_class=Auth,
        id=auth.id,
        schema={
            "hashed_password": hashed_password,
        },
        session=db,
    )

    return res


async def logout_everywhere(
    user_id: uuid.UUID,
    db: AsyncSession,
):
    query = select(RefreshToken).where(RefreshToken.user_id == user_id)
    logins = await get_data_from_table(
        query=query,
        session=db,
        __get_all__=True,
    )

    for login in logins:
        await delete_record(
            model_class=RefreshToken,
            id=login.id,
            session=db,
        )


def generate_otp(length=settings.OTP_LENGTH):
    """Generate a numeric OTP of specified length"""
    return "".join(random.choices(string.digits, k=length))


async def get_otp(
    user_id: uuid.UUID,
    db: AsyncSession,
    exist: bool = False,
):
    query = (
        select(OTPVerification)
        .where(OTPVerification.user_id == user_id)
        .where(OTPVerification.is_used == False)
        .where(OTPVerification.expires_at > datetime.utcnow())
    )

    otp_db = await get_data_from_table(
        query=query,
        session=db,
    )

    if exist == bool(otp_db):
        message = f"User has an OTP" if exist else f"User does not have an OTP token"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )

    return otp_db


async def create_and_send_otp(
    user_id: uuid.UUID,
    email: str,
    db: AsyncSession,
):
    await get_otp(
        user_id=user_id,
        db=db,
        exist=True,
    )

    otp = generate_otp()

    hashed_otp = await hash_password(otp)

    await insert_into_table(
        model_class=OTPVerification,
        session=db,
        schema={
            "user_id": user_id,
            "hashed_otp": hashed_otp,
        },
    )

    send_email_task.delay(
        email=email,
        subject="Verify your OTP",
        body=f"Your OTP: \n\n {otp}",
    )

    return True


async def get_refresh_token_by_token(
    refresh_token: str,
    db: AsyncSession,
):
    hashed_token = hash_refresh_token(refresh_token)

    query = select(RefreshToken).where(RefreshToken.token_hash == hashed_token)

    refresh_token = await get_data_from_table(
        query=query,
        session=db,
    )

    return refresh_token
