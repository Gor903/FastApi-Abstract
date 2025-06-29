import random
import string
import uuid
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from src.utils import hash_password, verify_password, create_token, hash_token
from core import settings
from db.models import Auth, RefreshToken, User
from db.models.auth import OTPVerification
from db.services import (
    delete_record,
    get_data_from_table,
    insert_into_table,
    update_model,
)
from .users import get_user

from typing import Dict, Any



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

    authorization = await verify_authorization(
        user=user,
        password=data.get("password"),
        db=db,
    )

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid users",
        )
    
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


async def logout(
    data: Dict[str, Any],
    db: AsyncSession,
):
    refresh_token = data.get("refresh_token")

    query = (
        select(RefreshToken)
        .where(RefreshToken.token_hash == hash_token(refresh_token))
    )

    token_db = await get_data_from_table(
        query=query,
        session=db,
    )

    if token_db.revoked or token_db.expires_at < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token already revoked",
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
    

async def refresh(
    data: Dict[str, Any],
    db: AsyncSession,
):
    refresh_token = data.get("refresh_token")

    query = (
        select(RefreshToken)
        .where(RefreshToken.token_hash == hash_token(refresh_token))
    )

    token_db = await get_data_from_table(
        query=query,
        session=db,
    )

    if token_db.revoked or token_db.expires_at < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token already revoked",
        )

    await update_model(
        model_class=RefreshToken,
        id=token_db.id,
        schema={
            "revoked": True,
        },
        session=db,
    )

    refresh_token_expire = timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
    )

    user = await get_user(
        id=token_db.user_id,
        db=db,
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


async def reset_password(
    data: Dict[str, Any],
    db: AsyncSession,
):      
    old_password = data.get("old_password")
    new_password = data.get("new_password")
    user = data.get("user")

    authorization = await verify_authorization(
        user=user,
        password=old_password,
        db=db,
    )

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid users",
        )
    
    query = select(Auth).where(Auth.user_id == user.id)
    
    auth = await get_data_from_table(
        query=query,
        session=db,
    )

    await update_model(
        model_class=Auth,
        id=auth.id,
        schema={
            "hashed_password": await hash_password(new_password),
        },
        session=db,
    )

    return {
        "message": "Password updated successfully",
    }


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

    print(otp_cunt)

    if otp_cunt > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has an OTP",
        )
    
    otp = "".join(random.choices(string.digits, k=settings.OTP_LENGTH))
    print(otp)
    hashed_otp = await hash_password(otp)

    await insert_into_table(
        model_class=OTPVerification,
        session=db,
        schema={
            "user_id": str(user.id),
            "hashed_otp": hashed_otp,
        },
    )

    print("inserted")

    
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

    authorization = await verify_password(
        plain_password=data.get("otp"),
        hashed_password=otp_db.hashed_otp,
    )

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid users otp",
        )

    await update_model(
        model_class=OTPVerification,
        id=otp_db.id,
        schema={
            "is_used": True,
        },
        session=db,
    )

    return user


async def reset_password_otp(
    data: Dict[str, Any],
    db: AsyncSession,
):
    user = await verify_otp(
        data=data,
        db=db,
    )

    query = select(Auth).where(Auth.user_id == user.id)
    
    auth = await get_data_from_table(
        query=query,
        session=db,
    )

    await update_model(
        model_class=Auth,
        id=auth.id,
        schema={
            "hashed_password": await hash_password(data.get("password")),
        },
        session=db,
    )

    return {
        "message": "Password updated successfully",
    }



# Tobechanged


async def verify_authorization(
    user: User,
    password: str,
    db: AsyncSession,
):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid users",
        )

    query = select(Auth).where(Auth.user_id == user.id)

    auth = await get_data_from_table(
        query=query,
        session=db,
    )

    if not auth:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid users",
        )

    return await verify_password(
        plain_password=password,
        hashed_password=auth.hashed_password,
    )