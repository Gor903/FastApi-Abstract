from uuid import UUID

from fastapi import APIRouter, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from user_service.api.dependencies import db_dependency, user_id_dependency
from user_service.ctrls import users as users_ctrls
from user_service.schemas import users as users_schemas

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
    response_model=users_schemas.UserIdResponse,
    status_code=status.HTTP_200_OK,
)
async def get_user_id(
    request: Request,
    db: AsyncSession = db_dependency,
):
    data = {
        "request": request,
    }

    user_id = await users_ctrls.get_user_id(
        data=data,
        db=db,
    )

    return {
        "user_id": user_id,
    }


@router.get(
    path="/{username}",
    response_model=users_schemas.UserResponse,
    status_code=status.HTTP_200_OK,
)
async def get_user(
    username: str,
    db: AsyncSession = db_dependency,
):
    user = await users_ctrls.get_user(
        username=username,
        db=db,
    )

    return user


@router.get(
    path="/short/{username}",
    response_model=users_schemas.UserShortResponse,
    status_code=status.HTTP_200_OK,
)
async def get_user(
    username: str,
    db: AsyncSession = db_dependency,
):
    user = await users_ctrls.get_user(
        username=username,
        db=db,
    )

    return user


@router.patch(
    path="/update",
    response_model=users_schemas.UserResponse,
    status_code=status.HTTP_200_OK,
)
async def update_user(
    data: users_schemas.UserUpdate,
    user_id: UUID = user_id_dependency,
    db: AsyncSession = db_dependency,
):
    data: dict = data.model_dump(exclude_none=True)

    if not data:
        raise HTTPException(
            detail="Empty content",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    user = await users_ctrls.update_user(
        data=data,
        user_id=user_id,
        db=db,
    )

    return user
