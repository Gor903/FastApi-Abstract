from uuid import UUID

from fastapi import Depends, HTTPException, Request
from user_service.exceptions.http_exceptions import NoAuthException


def get_user_id(request: Request) -> UUID:
    user_id = request.headers.get("user_id")

    if user_id is None:
        raise NoAuthException(
            sender="user_dependency", detail="Not authenticated: no user_id in headers"
        )

    return user_id


user_id_dependency = Depends(get_user_id)
