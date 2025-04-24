from typing import Any, List, Sequence, Type

from pydantic import BaseModel
from sqlalchemy import Row
from sqlalchemy.orm import Query
from sqlalchemy import RowMapping
from sqlalchemy.ext.asyncio import AsyncSession


async def get_data_from_table(
    query: Type[Query],
    session: AsyncSession,
    __get_all__: bool = False,
) -> None | BaseModel | Sequence[Row[Any] | RowMapping | Any]:

    try:
        if __get_all__:
            __models__: List[BaseModel] | [] = await session.scalars(query)

            if not __models__:
                return None

            else:
                return __models__.all()
        else:
            __model__: BaseModel | None = await session.scalar(query)
            return __model__

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
