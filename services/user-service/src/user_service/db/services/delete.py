from typing import Type
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from user_service.exceptions.http_exceptions import RecordDelete


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

    except IntegrityError:
        await session.rollback()
        raise RecordDelete(
            detail="Integrity error: record may be referenced elsewhere."
        )

    except ProgrammingError:
        await session.rollback()
        raise RecordDelete(detail="Programming error: invalid SQL operation.")

    except (OperationalError, DBAPIError):
        await session.rollback()
        raise RecordDelete(detail="Database connection or driver error.")

    except SQLAlchemyError:
        await session.rollback()
        raise RecordDelete(detail="Unexpected database error during delete.")

    except Exception:
        await session.rollback()
        raise RecordDelete(detail="Unknown error occurred while deleting record.")
