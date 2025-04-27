from typing import Dict, Any

from sqlalchemy import update, UUID
from sqlalchemy.ext.asyncio import AsyncSession


async def update_model(
    model_class: object,
    id: UUID,
    session: AsyncSession,
    schema: Dict[str, Any],
) -> bool:
    try:
        __result__ = await session.execute(
            update(model_class).where(model_class.id == id).values(**schema)
        )

        await session.commit()

        return True
    except Exception:
        raise False
