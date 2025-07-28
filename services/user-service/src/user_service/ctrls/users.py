from typing import Any, Dict
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from user_service.db.models import RefreshToken, User
from user_service.db.services import get_data_from_table, update_model
from user_service.exceptions.http_exceptions import CTRLException
from user_service.utils import decode_token


async def get_user(
    db: AsyncSession,
    username: str = None,
    email: str = None,
    id: str = None,
):
    if not any([username, email, id]):
        raise ValueError("Input should be (username|email|id)")
    query = select(User)
    if id is not None:
        query = query.where(User.id == id)
    elif email is not None:
        query = query.where(User.email == email)
    elif username is not None:
        query = query.where(User.username == username)

    user = await get_data_from_table(
        query=query,
        session=db,
    )

    if not user:
        raise CTRLException(
            detail="User not found",
        )

    return user


async def get_user_id(
    data: dict,
    db: AsyncSession,
):
    request = data.get("request")
    auth = request.headers.get("Authorization")

    if not auth or not auth.startswith("Bearer "):
        raise CTRLException(
            detail="Missing or invalid token",
        )

    token = auth.split("Bearer ")[-1]

    payload = decode_token(token)

    query = (
        select(RefreshToken)
        .where(RefreshToken.id == payload.get("refresh_token_id"))
        .where(RefreshToken.revoked == False)
    )
    refresh_token = await get_data_from_table(
        query=query,
        session=db,
    )

    if not refresh_token:
        raise CTRLException(
            detail="No valid token found",
        )

    query = select(User).where(User.id == payload.get("user_id"))
    user = await get_data_from_table(
        query=query,
        session=db,
    )
    if not user:
        raise CTRLException(
            detail="User not found",
        )

    return payload.get("user_id")


async def update_user(
    data: Dict[str, Any],
    user_id: UUID,
    db: AsyncSession,
):
    result = await update_model(
        model_class=User,
        id=user_id,
        session=db,
        schema=data,
    )

    if not result:
        raise CTRLException(
            detail="User update fail",
        )

    query = select(User).where(User.id == user_id)

    user = await get_data_from_table(
        query=query,
        session=db,
    )

    if not user:
        raise CTRLException(
            detail="User not found",
        )

    return user
