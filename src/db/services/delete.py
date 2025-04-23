from typing import Type
from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession


async def delete_record(
    __model_class__: object,
    __session__: AsyncSession,
    __code__: Type[UUID],
    __auto_commit__: bool = True,
):
    stmt = delete(table=__model_class__).where(
        __model_class__.code == __code__,
    )

    result = await __session__.execute(stmt)

    if result.rowcount == 0:
        return False

    if __auto_commit__:
        await __session__.commit()

    return True
