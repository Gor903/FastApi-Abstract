import uuid
import bcrypt
import asyncio
import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, Union
from datetime import datetime, timedelta

from src.core import settings
from src.db.services import insert_into_table
from src.db.models import Auth
from src.tasks import send_verification_email_task


async def save_password(
    user_id: uuid.UUID,
    password: str,
    db: AsyncSession,
):
    hashed_password = await hash_password(password)

    auth_data = {
        "user_id": user_id,
        "hashed_password": hashed_password,
    }

    auth = await insert_into_table(
        model_class=Auth,
        session=db,
        schema=auth_data,
    )

    return auth


async def create_email_verification(
    user_id: uuid.UUID,
    user_email: str,
):
    data = {
        "sub": str(user_id),
        "type": "email_verification",
    }
    expires = timedelta(hours=24)
    token = create_token(
        data,
        expires,
    )

    send_verification_email_task.delay(
        email=user_email,
        token=token,
    )

    return {"message": "Email verification sent!"}


async def hash_password(password: str) -> str:
    hashed = await asyncio.to_thread(
        bcrypt.hashpw,
        password.encode(),
        bcrypt.gensalt(),
    )

    return hashed.decode()


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    is_valid = await asyncio.to_thread(
        bcrypt.checkpw,
        plain_password.encode(),
        hashed_password.encode(),
    )

    return is_valid


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
