import os
from typing import Annotated

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from db import get_async_session
from db.ctrls.users import get_user_by_username
from db.ctrls.auth import get_refresh_token_by_id
from src.utils import decode_token

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/swagger")


# TODO: check the token's content
async def get_token_data(
    token: Annotated[str, Depends(oauth2_scheme)],
):
    try:
        payload = decode_token(token)

        return payload

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_async_session),
):
    try:
        payload = await get_token_data(token)

        username: str = payload.get("sub")
        refresh_token_id: str = payload.get("refresh_token_id")

        user = await get_user_by_username(
            username=username,
            db=db,
        )

        if not user:
            raise Exception("User not found")

        refresh_token = await get_refresh_token_by_id(
            token_id=refresh_token_id,
            db=db,
        )

        if not refresh_token:
            raise Exception("Refresh token not found")
        if refresh_token.revoked:
            raise Exception("Refresh token revoked")

        return user

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


user_dependency = Annotated[dict, Depends(get_current_user)]
token_dependency = Annotated[dict, Depends(get_token_data)]
