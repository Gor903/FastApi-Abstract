import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.services import insert_into_table, get_data_from_table
from src.db.models import User
from src.db.ctrls.auth import create_email_verification, save_password


async def register_user(
    user_data: dict,
    password: str,
    db: AsyncSession,
):
    new_user = await insert_into_table(
        model_class=User,
        session=db,
        schema=user_data,
        auto_flush=True,
    )
    await db.flush()

    await save_password(
        user_id=new_user.id,
        password=password,
        db=db,
    )

    await create_email_verification(
        user_id=new_user.id,
        user_email=new_user.email,
        db=db,
    )

    return new_user


async def get_user_by_id(
    user_id: uuid.UUID,
    db: AsyncSession,
):
    query = select(User).where(User.id == user_id)
    user = await get_data_from_table(
        query=query,
        session=db,
    )

    return user


async def get_user_by_email(
    email: str,
    db: AsyncSession,
):
    query = select(User).where(User.email == email)
    user = await get_data_from_table(
        query=query,
        session=db,
    )

    return user


async def get_user_by_username(
    username: str,
    db: AsyncSession,
):
    query = select(User).where(User.username == username)
    user = await get_data_from_table(
        query=query,
        session=db,
    )

    return user
