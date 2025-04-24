from fastapi import APIRouter, HTTPException
from starlette import status

from src.db.schemas import register_Request, user_Response
from src.dependencies import db_dependency
from src.db.ctrls import register_user

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
    db=db_dependency,
):
    user_data = user.model_dump()

    password = user_data.get("password")
    if not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect request",
        )
    user_data.pop("password")

    user = await register_user(
        user_data=user_data,
        password=password,
        db=db,
    )

    if not user[0]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=user[1],
        )

    return user[1]
