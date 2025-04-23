from typing import Annotated, Any, Dict
from pydantic import schema
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession


async def insert_into_table(
    __model_class__: object,
    __session__: async_sessionmaker[AsyncSession],
    __schema__: Annotated[
        schema | Dict[str, Any],
        None,
    ],
    __auto_commit: Annotated[bool, True],
) -> Dict[str, Any]:

    __response: Dict[str, Dict[str, Any]] = {"response": {}}
    __model__: __model_class__ = None

    try:
        if __schema__ is not None:
            __model__ = __model_class__(**__schema__)

            __session__.add(__model__)

            if __auto_commit:
                await __session__.commit()

            __response = {
                "response": {
                    "error": False,
                    "message": "Records already inserted.",
                },
                "data": __model__,
            }
            return __response

    except Exception as e:
        print(f"Error: {e}")
