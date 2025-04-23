from typing import Dict, Any

from starlette import status
from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy import update, UUID
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from typing_extensions import Annotated

from src.db import get_async_session


async def update_model(
    __model_class__: object,
    code: UUID,
    __session__: async_sessionmaker[AsyncSession],
    __schema__: Annotated[
        Dict[str, Any],
        None,
    ],
) -> Dict[str, Any]:
    try:

        async with __session__() as session:
            __result__ = await session.execute(
                update(__model_class__)
                .where(__model_class__.code == code)
                .values(**__schema__, updated_at=func.now())
            )

            await session.commit()

        return {
            "message": "Records updated successfully",
            "error": False,
        }
    except Exception as Error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(Error),
        )
