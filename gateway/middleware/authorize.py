from fastapi import HTTPException

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from httpx import AsyncClient


from config import settings

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        
        base_url = f"http://user-service:8001"
        method = "GET"
        endpoint = "validate"
        headers = dict(request.headers)

        async with AsyncClient(base_url=base_url) as client:
            response = None
            try:
                response = await client.request(
                    method=method.upper(),
                    url=endpoint,
                    headers=headers,
                )

                user_id = response.json().get("user_id")

                request.headers.__dict__["_list"].append(
                    (b"user_id", str(user_id).encode())
                )

            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Authorization service error: {str(e)}"
                )

        response = await call_next(request)

        return response