import uuid
from datetime import datetime

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from db.ctrls import users as ctrls_users
from db.ctrls import auth as ctrls_auth
from db.schemas import LoginRequest, LoginResponse, UserRegister, UserResponse
from src.dependencies import db_dependency, token_dependency, user_dependency

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post(
    path="/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user: UserRegister,
    db: AsyncSession = db_dependency,
):
    user_data = user.model_dump()
    password = user_data.pop("password")

    user = await ctrls_users.register_user(
        user_data=user_data,
        password=password,
        db=db,
    )

    return user


@router.post(
    path="/verify_otp",
    response_model=bool,
    status_code=status.HTTP_200_OK,
)
async def verify_otp(
    user_id: uuid.UUID = Body(..., embed=True),
    otp: str = Body(..., embed=True),
    db: AsyncSession = db_dependency,
):
    verified = await ctrls_auth.verify_otp(
        user_id=user_id,
        otp=otp,
        db=db,
    )

    if not verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect otp",
        )

    await ctrls_users.update_user(
        user_id=user_id,
        data={
            "is_verified": True,
        },
        db=db,
    )

    return True


@router.post(
    path="/send_otp",
    response_model=bool,
)
async def send_otp(
    email: str = Body(..., embed=True),
    db: AsyncSession = db_dependency,
):
    user = await ctrls_users.get_user_by_email(
        email=email,
        db=db,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not found",
        )

    res = await ctrls_auth.create_and_send_otp(
        user_id=user.id,
        email=email,
        db=db,
    )

    return res


@router.post(
    path="/login",
    response_model=LoginResponse,
)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = db_dependency,
):
    login_data = login_data.model_dump()

    if email := login_data.get("email"):
        user = await ctrls_users.get_user_by_email(
            email=email,
            db=db,
        )
    elif username := login_data.get("username"):
        user = await ctrls_users.get_user_by_username(
            username=username,
            db=db,
        )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found",
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your email is not verified",
        )

    authorized = await ctrls_auth.verify_authorization(
        user=user,
        password=login_data.get("password"),
        db=db,
    )

    if not authorized:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password",
        )

    refresh_token = await ctrls_auth.create_refresh_token(
        user=user,
        db=db,
    )

    access_token = await ctrls_auth.create_access_token(
        user=user,
        refresh_token_id=str(refresh_token[1]),
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token[0],
    }


@router.post(
    path="/login/swagger",
    response_model=LoginResponse,
)
async def login_user(
    login_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = db_dependency,
):
    user = await ctrls_users.get_user_by_username(
        username=login_data.username,
        db=db,
    )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your email is not verified",
        )

    authorized = await ctrls_auth.verify_authorization(
        user=user,
        password=login_data.password,
        db=db,
    )

    if not authorized:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password",
        )

    refresh_token = await ctrls_auth.create_refresh_token(
        user=user,
        db=db,
    )

    access_token = await ctrls_auth.create_access_token(
        user=user,
        refresh_token_id=str(refresh_token[1]),
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token[0],
    }


@router.post(
    path="/reset_password",
    response_model=bool,
)
async def reset_password(
    user: user_dependency,
    db: AsyncSession = db_dependency,
    old_password: str = Body(..., embed=True),
    new_password: str = Body(..., embed=True),
):
    authorized = await ctrls_auth.verify_authorization(
        user=user,
        password=old_password,
        db=db,
    )

    if not authorized:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password",
        )

    update = await ctrls_auth.update_password(
        user_id=user.id,
        password=new_password,
        db=db,
    )

    if update:
        await ctrls_auth.logout_everywhere(
            user_id=user.id,
            db=db,
        )

    return update


@router.post(
    path="/reset_password/otp",
    response_model=bool,
)
async def reset_password_otp(
    user_id: uuid.UUID = Body(..., embed=True),
    otp: str = Body(..., embed=True),
    new_password: str = Body(..., embed=True),
    db: AsyncSession = db_dependency,
):
    user = await ctrls_users.get_user_by_id(user_id, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found",
        )

    verified = await ctrls_auth.verify_otp(
        user_id=user_id,
        otp=otp,
        db=db,
    )

    if not verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect otp",
        )

    update = await ctrls_auth.update_password(
        user_id=user.id,
        password=new_password,
        db=db,
    )

    if update:
        await ctrls_auth.logout_everywhere(
            user_id=user.id,
            db=db,
        )

    return update


@router.post(
    path="/refresh",
    response_model=LoginResponse,
)
async def refresh_tokens(
    refresh_token: str = Body(..., embed=True),
    db: AsyncSession = db_dependency,
):
    refresh_token_db = await ctrls_auth.get_refresh_token_by_token(
        refresh_token=refresh_token,
        db=db,
    )

    if not refresh_token_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token not found",
        )

    if refresh_token_db.revoked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token revoked",
        )

    refresh_token_id = refresh_token_db.id

    user = await ctrls_users.get_user_by_id(
        user_id=refresh_token_db.user_id,
        db=db,
    )

    remaining = refresh_token_db.expires_at - datetime.utcnow()
    if remaining.total_seconds() < 7200:
        await ctrls_auth.update_refresh_token(
            data={"revoked": True},
            id=refresh_token_db.id,
            db=db,
        )

        refresh_token_db = await ctrls_auth.create_refresh_token(
            user=user,
            db=db,
        )

        refresh_token_id = str(refresh_token_db[1])
        refresh_token = refresh_token_db[0]

    access_token = await ctrls_auth.create_access_token(
        user=user,
        refresh_token_id=str(refresh_token_id),
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


@router.post(
    path="/logout",
    response_model=bool,
)
async def logout(
    token: token_dependency,
    db: AsyncSession = db_dependency,
):
    refresh_token_id = token.get("refresh_token_id")

    refresh_token = await ctrls_auth.get_refresh_token_by_id(
        token_id=refresh_token_id,
        db=db,
    )

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect access token",
        )

    await ctrls_auth.update_refresh_token(
        data={
            "revoked": True,
        },
        id=refresh_token.id,
        db=db,
    )

    return True


@router.get(
    path="/me",
    response_model=UserResponse,
)
async def get_me(
    user: user_dependency,
    db: AsyncSession = db_dependency,
):
    return user
