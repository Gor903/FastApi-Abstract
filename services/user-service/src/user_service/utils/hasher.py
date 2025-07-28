import asyncio
import hashlib

import bcrypt
from user_service.core import settings


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


def hash_token(token: str) -> str:
    salted_token = (settings.SERVER_SECRET_SALT + token).encode("utf-8")
    return hashlib.sha256(salted_token).hexdigest()
