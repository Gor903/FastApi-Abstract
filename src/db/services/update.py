from typing import Dict, Any

from starlette import status
from fastapi import HTTPException
from sqlalchemy import update, UUID
from sqlalchemy.ext.asyncio import AsyncSession


async def update_model(
    model_class: object,
    id: UUID,
    session: AsyncSession,
    schema: Dict[str, Any],
) -> Dict[str, Any]:
    try:
        __result__ = await session.execute(
            update(model_class).where(model_class.id == id).values(**schema)
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
