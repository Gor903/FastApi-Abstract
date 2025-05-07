from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status


async def insert_into_table(
    model_class: object,
    session: AsyncSession,
    schema: dict,
    auto_commit: bool = True,
    auto_flush: bool = False,
):

    __model__: model_class = None

    try:
        if schema is not None:

            __model__ = model_class(**schema)

            session.add(__model__)

            if auto_flush:
                await session.flush()
            elif auto_commit:
                await session.commit()

            return __model__

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
