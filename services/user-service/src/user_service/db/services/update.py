import uuid

from fastapi import HTTPException
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from user_service.exceptions.http_exceptions import RecordUpdate


async def update_model(
    model_class: object,
    id: uuid.UUID,
    session: AsyncSession,
    schema: dict,
) -> bool:
    try:
        await session.execute(
            update(model_class).where(model_class.id == id).values(**schema)
        )

        await session.commit()

        return True

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
