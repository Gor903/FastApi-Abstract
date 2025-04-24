from typing import Type
from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession


async def delete_record(
    model_class: object,
    session: AsyncSession,
    id: Type[UUID],
):
    stmt = delete(table=model_class).where(
        model_class.id == id,
    )

    result = await session.execute(stmt)

    if result.rowcount == 0:
        return False

    await session.commit()

    return True
