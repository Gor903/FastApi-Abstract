from exceptions.http_exceptions import RecordCreate
from fastapi import HTTPException
from sqlalchemy.exc import (
    DataError,
    DBAPIError,
    IntegrityError,
    OperationalError,
    ProgrammingError,
    SQLAlchemyError,
)
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

    except IntegrityError:
        await session.rollback()
        raise RecordCreate(
            detail="Integrity error: possible duplicate or invalid foreign key."
        )

    except (DataError, ProgrammingError):
        await session.rollback()
        raise RecordCreate(detail="Invalid data: check types, length, or format.")

    except (OperationalError, DBAPIError):
        await session.rollback()
        raise RecordCreate(detail="Database connection error or misconfiguration.")

    except SQLAlchemyError:
        await session.rollback()
        raise RecordCreate(detail="Unexpected database error occurred.")

    except Exception:
        await session.rollback()
        raise RecordCreate(detail="Unknown error while creating record.")
