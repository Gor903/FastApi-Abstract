import jwt
from datetime import datetime, timedelta
from typing import Union, Any

from src.core import settings


def create_token(data: dict, expires_delta: Union[timedelta, None]) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    return encoded_jwt


def decode_token(token: str) -> Union[dict[str, Any], None]:
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
        print("Token has expired.")
        return None
    except jwt.InvalidTokenError:
        print("Invalid token.")
        return None
