from uuid import UUID

from fastapi import Depends, HTTPException, Request


def get_user_id(request: Request) -> UUID:
    user_id = request.headers.get("user_id")
    print(f"User ID from request headers: {user_id}")

    if user_id is None:
        raise HTTPException(401, detail="Unauthorized")

    return user_id


user_id_dependency = Depends(get_user_id)
