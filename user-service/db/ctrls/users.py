from fastapi import HTTPException
from starlette import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User, RefreshToken
from db.services import get_data_from_table, update_model
from src.utils import decode_token

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

    return user


async def get_user_id(
    data: dict,
    db: AsyncSession,
):
    request = data.get("request")
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid token",
        )
    
    token = auth.split("Bearer ")[-1]

    payload = decode_token(token)

    query = (
        select(RefreshToken)
        .where(RefreshToken.id == payload.get("refresh_token_id"))
    )
    await get_data_from_table(
        query=query,
        session=db,
    )

    query = (
        select(User)
        .where(User.id == payload.get("user_id"))
    )
    await get_data_from_table(
        query=query,
        session=db,
    )

    return payload.get("user_id")


