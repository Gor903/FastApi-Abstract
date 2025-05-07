import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.ctrls.auth import save_password, create_and_send_otp
from db.models import User
from db.services import get_data_from_table, insert_into_table, update_model


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

    await create_and_send_otp(
        user_id=new_user.id,
        email=new_user.email,
        db=db,
    )

    return new_user


async def verify_user(
    db: AsyncSession,
    user_id: uuid.UUID,
    value: bool = True,
):
    await update_model(
        model_class=User,
        id=user_id,
        session=db,
        schema={
            "is_verified": value,
        },
    )

    return True


async def update_user(
    user_id: uuid.UUID,
    data: dict,
    db: AsyncSession,
):
    await update_model(
        model_class=User,
        id=user_id,
        schema=data,
        session=db,
    )

    return True


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
