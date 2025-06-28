import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User
from db.services import get_data_from_table, update_model



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
