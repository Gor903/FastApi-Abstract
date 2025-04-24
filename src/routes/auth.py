from datetime import timedelta

from fastapi import APIRouter, Body, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.db.ctrls.auth import get_ev_by_user_id
from src.db.schemas import register_Request, user_Response
from src.dependencies import db_dependency
from src.db.ctrls import (
    get_user_by_email,
    register_user,
    get_id_from_email_token,
    update_email_verification,
    verify_email_token,
    create_token,
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

    password = user_data.get("password")
    if not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect request",
        )
    user_data.pop("password")

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
