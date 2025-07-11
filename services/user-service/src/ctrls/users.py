from typing import Any, Dict
from uuid import UUID

from db.models import RefreshToken, User
from db.services import get_data_from_table, update_model
from exceptions.http_exceptions import CTRLException
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.utils import decode_token
from starlette import status


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
