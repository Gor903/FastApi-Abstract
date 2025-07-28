from typing import Any, Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from user_service.api.dependencies import db_dependency, user_id_dependency
from user_service.ctrls import auth as auth_ctrls
from user_service.schemas import MessageResponse
from user_service.schemas import auth as auth_schemas
from user_service.schemas import users as users_schemas

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post(
    path="/register",
    response_model=users_schemas.UserShortResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: users_schemas.UserRegister,
    db: AsyncSession = db_dependency,
):
    data = data.model_dump()

    user = await auth_ctrls.register(
        data=data,
        db=db,
    )

    return user


@router.post(
    path="/verify_otp",
    response_model=users_schemas.UserShortResponse,
    status_code=status.HTTP_200_OK,
)
async def verify_otp(
    data: auth_schemas.OTPRequest,
    db: AsyncSession = db_dependency,
):
    data = data.model_dump()

    response = await auth_ctrls.verify_otp(
        data=data,
        db=db,
    )

    return response


@router.post(
    path="/send_otp",
    response_model=MessageResponse,
)
async def send_otp(
    data: auth_schemas.EmailOrUsernameRequest,
    db: AsyncSession = db_dependency,
):
    data = data.model_dump()

    await auth_ctrls.send_otp(
        data=data,
        db=db,
    )

    return {
        "message": "OTP sent",
    }


@router.post(
    path="/login",
    response_model=auth_schemas.LoginResponse,
)
async def login(
    data: auth_schemas.LoginRequest,
    db: AsyncSession = db_dependency,
):
    data = data.model_dump()

    response = await auth_ctrls.login(
        data=data,
        db=db,
    )

    return response


@router.post(
    path="/reset_password",
    response_model=MessageResponse,
)
async def reset_password(
    data: auth_schemas.PasswordResset,
    user_id: UUID = user_id_dependency,
    db: AsyncSession = db_dependency,
):
    data = data.model_dump()
    data["user_id"] = user_id

    response = await auth_ctrls.reset_password(
        data=data,
        db=db,
    )

    return response


@router.post(
    path="/reset_password/otp",
    response_model=MessageResponse,
)
async def reset_password_otp(
    data: auth_schemas.PasswordResetOTP,
    db: AsyncSession = db_dependency,
):
    data = data.model_dump()

    response = await auth_ctrls.reset_password_otp(
        data=data,
        db=db,
    )

    return response


@router.post(
    path="/refresh",
    response_model=auth_schemas.LoginResponse,
)
async def refresh(
    data: auth_schemas.RefreshTokenRequest,
    db: AsyncSession = db_dependency,
):
    data = data.model_dump()

    response = await auth_ctrls.refresh(
        data=data,
        db=db,
    )

    return response


@router.post(
    path="/logout",
    response_model=MessageResponse,
)
async def logout(
    data: auth_schemas.RefreshTokenRequest,
    db: AsyncSession = db_dependency,
):
    data = data.model_dump()

    response = await auth_ctrls.logout(
        data=data,
        db=db,
    )

    return response
