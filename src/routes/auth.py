from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.db.schemas import register_Request, user_Response
from src.dependencies import async_session

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post(
    path="/register",
    response_model=user_Response,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user: register_Request,
    db: AsyncSession = async_session,
):
    return {
        "id": "guid",
    }
