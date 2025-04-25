from datetime import timedelta

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.db.ctrls.auth import get_ev_by_user_id
from src.db.schemas import LoginRequest, LoginResponse, register_Request, user_Response
from src.dependencies import db_dependency, user_dependency
from src.db.ctrls import (
    create_auth_tokens,
    get_user_by_email,
    get_user_by_username,
    get_user_by_id,
    register_user,
    get_id_from_email_token,
    update_email_verification,
    verify_email_token,
    create_token,
    verify_authorization,
)
from src.tasks import send_verification_email_task


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post(
    path="/register",
    response_model=user_Response,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user: register_Request,
    db: AsyncSession = db_dependency,
):
    user_data = user.model_dump()
    password = user_data.pop("password")

    user = await register_user(
        user_data=user_data,
        password=password,
        db=db,
    )

    if not user[0]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=user[1],
        )

    return user[1]


@router.post(
    path="/resend-email",
)
async def resend_verification_email(
    email: str = Body(..., embed=True), db: AsyncSession = db_dependency
):
    user = await get_user_by_email(
        email=email,
        db=db,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect request",
        )

    verification = await get_ev_by_user_id(
        user_id=user.id,
        db=db,
    )

    if not verification[0]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=verification[1],
        )

    data = {
        "sub": str(user.id),
        "type": "email_verification",
    }
    expires = timedelta(hours=24)
    token = create_token(
        data,
        expires,
    )

    await update_email_verification(
        ev_id=verification[0].id,
        data={"token": token},
        db=db,
    )

    send_verification_email_task.delay(
        email=user.email,
        token=token,
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

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wrong username or email",
        )

    ev = await get_ev_by_user_id(
        user_id=user.id,
        db=db,
    )

    if not ev[1] == "Email already verified!":
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

    tokens = await create_auth_tokens(
        user=user,
        db=db,
    )

    return tokens


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

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wrong username or email",
        )

    ev = await get_ev_by_user_id(
        user_id=user.id,
        db=db,
    )

    if not ev[1] == "Email already verified!":
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

    tokens = await create_auth_tokens(
        user=user,
        db=db,
    )

    return tokens


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

    if not verification[0]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=verification[1],
        )

    await update_email_verification(
        ev_id=verification[0].id,
        data={"is_used": True},
        db=db,
    )


@router.get(
    path="/me",
    response_model=user_Response,
)
async def get_me(
    user: user_dependency,
    db: AsyncSession = db_dependency,
):
    return user
