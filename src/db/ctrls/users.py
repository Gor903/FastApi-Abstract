from sqlalchemy.ext.asyncio import AsyncSession

from src.db.services import insert_into_table
from src.dependencies import db_dependency
from src.db.models import User
from src.db.ctrls.auth import create_email_verification, save_password


async def register_user(
    user_data: dict,
    password: str,
    db: AsyncSession = db_dependency,
):
    new_user = await insert_into_table(
        model_class=User,
        session=db,
        schema=user_data,
        auto_flush=True,
    )
    await db.flush()

    if not new_user[0]:
        return new_user

    auth = await save_password(
        user_id=new_user[1].id,
        password=password,
        db=db,
    )

    if not auth[0]:
        return auth

    await create_email_verification(
        user_id=new_user[1].id,
        user_email=new_user[1].email,
        db=db,
    )

    return new_user
