from typing import Type
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status


async def delete_record(
    model_class: object,
    session: AsyncSession,
    id: Type[UUID],
):
    try:
        stmt = delete(table=model_class).where(
            model_class.id == id,
        )

        result = await session.execute(stmt)

        if result.rowcount == 0:
            raise Exception(f"no record deleted: {id}")

        await session.commit()

        return True
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
