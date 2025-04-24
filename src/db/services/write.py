from typing import Annotated, Any, Dict
from pydantic import schema
from sqlalchemy.exc import DBAPIError, IntegrityError, StatementError
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import Base


async def insert_into_table(
    model_class: object,
    session: AsyncSession,
    schema: dict,
    auto_commit: bool = True,
    auto_flush: bool = False,
) -> tuple[bool, Base]:

    __model__: model_class = None

    try:
        if schema is not None:

            __model__ = model_class(**schema)

            session.add(__model__)

            if auto_flush:
                await session.flush()
            elif auto_commit:
                await session.commit()

            return True, __model__

    except DBAPIError as e:
        message = str(e.orig)
    except StatementError as e:
        message = str(e.orig)
    except IntegrityError as e:
        orig_msg = str(e.orig)
        detail_line = next(
            (
                line.split(":")[1].strip()
                for line in orig_msg.splitlines()
                if line.strip().startswith("DETAIL:")
            ),
            "Unknown integrity error",
        )
        message = detail_line
    except Exception as e:
        print(type(e))
        message = str(e)

    return False, message
