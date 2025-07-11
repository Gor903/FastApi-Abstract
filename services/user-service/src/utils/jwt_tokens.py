from datetime import datetime, timedelta
from typing import Any, Dict, Union

import jwt
from core import settings
from exceptions.http_exceptions import JWTException
from fastapi import HTTPException
from starlette import status


def create_token(data: dict, expires_delta: Union[timedelta, None]) -> str:
    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            key=settings.SECRET_KEY,
            algorithms=[
                settings.ALGORITHM,
            ],
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise JWTException(
            detail="Token expired",
        )
    except jwt.InvalidTokenError:
        raise JWTException(detail="Token invalid")
