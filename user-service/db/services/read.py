from typing import List, Type

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Query
from starlette import status


async def get_data_from_table(
    query: Type[Query],
    session: AsyncSession,
    __get_all__: bool = False,
):

    try:
        if __get_all__:
            __models__: List[BaseModel] | [] = await session.scalars(query)

            return __models__.all()
        else:
            __model__: BaseModel | None = await session.scalar(query)

            if __model__ is None:
                raise Exception("Data not found")

            return __model__

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
