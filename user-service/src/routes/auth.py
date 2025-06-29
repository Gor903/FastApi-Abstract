from uuid import UUID
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.ctrls import auth as ctrls_auth
from db.schemas import users as schema_users
from db.schemas import auth as schema_auth
from db.schemas import MessageResponse
from src.dependencies import db_dependency, user_id_dependency


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post(
    path="/register",
    response_model=schema_users.UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: schema_users.UserRegister,
    db: AsyncSession = db_dependency,
):
    data = data.model_dump()

    user = await ctrls_auth.register(
        data=data,
        db=db,
    )

    return user


@router.post(
    path="/verify_otp",
    response_model=schema_users.UserResponse,
    status_code=status.HTTP_200_OK,
)
async def verify_otp(
    data: schema_auth.OTPRequest,
    db: AsyncSession = db_dependency,
):
    data = data.model_dump()

    response = await ctrls_auth.verify_otp(
        data=data,
        db=db,
    )

    return response


@router.post(
    path="/send_otp",
    response_model=MessageResponse,
)
async def send_otp(
    data: schema_auth.EmailOrUsernameRequest,
    db: AsyncSession = db_dependency,
):
    data = data.model_dump()

    await ctrls_auth.send_otp(
        data=data,
        db=db,
    )

    return {"message": "OTP sent",}


@router.post(
    path="/login",
    response_model=schema_auth.LoginResponse,
)
async def login(
    data: schema_auth.LoginRequest,
    db: AsyncSession = db_dependency,
):
    data = data.model_dump()

    response = await ctrls_auth.login(
        data=data,
        db=db,
    )

    return response


@router.post(
    path="/login/swagger",
    response_model=schema_auth.LoginResponse,
)
async def login_swagger(
    data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = db_dependency,
):
    data = {
        "username": data.username,
        "password": data.password,
    }    

    response = await ctrls_auth.login(
        data=data,
        db=db,
    )

    return response


@router.post(
    path="/reset_password",
    response_model=MessageResponse,
)
async def reset_password(
    data: schema_auth.PasswordResset,
    user_id: UUID = user_id_dependency,
    db: AsyncSession = db_dependency,
):
    data = data.model_dump()
    data["user_id"] = user_id

    response = await ctrls_auth.reset_password(
        data=data,
        db=db,
    )

    return response


@router.post(
    path="/reset_password/otp",
    response_model=MessageResponse,
)
async def reset_password_otp(
    data: schema_auth.PasswordResetOTP,
    db: AsyncSession = db_dependency,
):
    data = data.model_dump()

    response = await ctrls_auth.reset_password_otp(
        data=data,
        db=db,
    )

    return response


@router.post(
    path="/refresh",
    response_model=schema_auth.LoginResponse,
)
async def refresh(
    data: schema_auth.RefreshTokenRequest,
    db: AsyncSession = db_dependency,
):
    data = data.model_dump()

    response = await ctrls_auth.refresh(
        data=data,
        db=db,
    )

    return response


@router.post(
    path="/logout",
    response_model=MessageResponse,
)
async def logout(
    data: schema_auth.RefreshTokenRequest,
    db: AsyncSession = db_dependency,
):
    data = data.model_dump()

    response = await ctrls_auth.logout(
        data=data,
        db=db,
    )

    return response
