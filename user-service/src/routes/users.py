from uuid import UUID

from db.schemas import users as schema_users
from fastapi import APIRouter, Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.ctrls import users as ctrls_users
from src.dependencies import db_dependency, user_id_dependency
from starlette import status

router = APIRouter(
    prefix="",
    tags=["Users"],
)


@router.get("/id")
async def receive_data(
    user_id: UUID = user_id_dependency,
):
    return {"user_id": user_id}


@router.get(
    path="/validate",
    response_model=schema_users.UserIdResponse,
    status_code=status.HTTP_200_OK,
)
async def get_user_id(
    request: Request,
    db: AsyncSession = db_dependency,
):
    data = {
        "request": request,
    }

    user_id = await ctrls_users.get_user_id(
        data=data,
        db=db,
    )

    return {
        "user_id": user_id,
    }
