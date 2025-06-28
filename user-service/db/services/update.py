import uuid

from fastapi import HTTPException
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status


async def update_model(
    model_class: object,
    id: uuid.UUID,
    session: AsyncSession,
    schema: dict,
) -> bool:
    try:
        __result__ = await session.execute(
            update(model_class).where(model_class.id == id).values(**schema)
        )

        await session.commit()

        return True
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
