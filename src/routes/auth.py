from datetime import datetime

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.db.ctrls import (
    create_access_token,
    create_refresh_token,
    get_id_from_email_token,
    get_refresh_token_by_id,
    get_user_by_email,
    get_user_by_id,
    get_user_by_username,
    refresh_email_verification,
    register_user,
    update_email_verification,
    update_password, update_refresh_token,
    verify_authorization,
    verify_email_token,
    get_ev_by_user_id,
    get_refresh_token_by_token,
)
from src.db.schemas import LoginRequest, LoginResponse, UserRegister, UserResponse
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

    user = await register_user(
        user_data=user_data,
        password=password,
        db=db,
    )

    return user


@router.post(
    path="/resend-email",
)
async def resend_verification_email(
    email: str = Body(..., embed=True),
    db: AsyncSession = db_dependency,
):
    user = await get_user_by_email(
        email=email,
        db=db,
    )

    verification = await get_ev_by_user_id(
        user_id=user.id,
        db=db,
    )

    if verification.is_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified",
        )

    await refresh_email_verification(
        ev_id=verification.id,
        user_id=user.id,
        user_email=email,
        db=db,
    )


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
        user = await get_user_by_email(
            email=email,
            db=db,
        )
    elif username := login_data.get("username"):
        user = await get_user_by_username(
            username=username,
            db=db,
        )

    ev = await get_ev_by_user_id(
        user_id=user.id,
        db=db,
    )

    if not ev:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not verified!",
        )

    authorized = await verify_authorization(
        user=user,
        password=login_data.get("password"),
        db=db,
    )

    if not authorized:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password",
        )

    refresh_token = await create_refresh_token(
        user=user,
        db=db,
    )

    access_token = await create_access_token(
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
    user = await get_user_by_username(
        username=login_data.username,
        db=db,
    )

    ev = await get_ev_by_user_id(
        user_id=user.id,
        db=db,
    )

    if not ev:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not verified!",
        )

    authorized = await verify_authorization(
        user=user,
        password=login_data.password,
        db=db,
    )

    if not authorized:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password",
        )

    refresh_token = await create_refresh_token(
        user=user,
        db=db,
    )

    access_token = await create_access_token(
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
    authorized = await verify_authorization(
        user = user,
        password = old_password,
        db = db,
    )

    if not authorized:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Incorrect password",
        )

    update = await update_password(
        user_id = user.id,
        password = new_password,
        db = db,
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
    refresh_token_db = await get_refresh_token_by_token(
        refresh_token=refresh_token,
        db=db,
    )

    if refresh_token_db.revoked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token revoked",
        )

    refresh_token_id = refresh_token_db.id

    user = await get_user_by_id(
        user_id=refresh_token_db.user_id,
        db=db,
    )

    remaining = refresh_token_db.expires_at - datetime.utcnow()
    if remaining.total_seconds() < 7200:
        await update_refresh_token(
            data={"revoked": True},
            id=refresh_token_db.id,
            db=db,
        )

        refresh_token_db = await create_refresh_token(
            user=user,
            db=db,
        )

        refresh_token_id = str(refresh_token_db[1])
        refresh_token = refresh_token_db[0]

    access_token = await create_access_token(
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

    refresh_token = await get_refresh_token_by_id(
        token_id=refresh_token_id,
        db=db,
    )

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect access token",
        )

    update_rt = await update_refresh_token(
        data={
            "revoked": True,
        },
        id=refresh_token.id,
        db=db,
    )

    return True


@router.get(
    path="/verify_email",
)
async def verify_email(
    token: str = Query(...),
    db: AsyncSession = db_dependency,
):
    id = await get_id_from_email_token(token=token)

    verification = await verify_email_token(
        token=token,
        user_id=id,
        db=db,
    )

    if not verification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification Failed",
        )

    await update_email_verification(
        ev_id=verification.id,
        data={"is_used": True},
        db=db,
    )


@router.get(
    path="/me",
    response_model=UserResponse,
)
async def get_me(
    user: user_dependency,
    db: AsyncSession = db_dependency,
):
    return user
