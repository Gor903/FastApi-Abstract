from typing import List, Type

from exceptions.http_exceptions import RecordRead
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

            return __model__

    except (DataError, ProgrammingError):
        raise RecordRead(
            detail="Query error: possibly wrong column, bad filter, or invalid data type."
        )

    except (OperationalError, DBAPIError):
        raise RecordRead(detail="Database connection error or timeout.")

    except SQLAlchemyError:
        raise RecordRead(detail="Unexpected database error during read operation.")

    except Exception:
        raise RecordRead(detail="Unknown error occurred while reading from database.")
