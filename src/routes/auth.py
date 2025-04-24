from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.db.schemas import register_Request, user_Response
from src.dependencies import db_dependency
from src.db.ctrls import (
    register_user,
    get_id_from_email_token,
    get_user_by_id,
    update_email_verification,
    verify_email_token,
)

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

    return verification[1]
