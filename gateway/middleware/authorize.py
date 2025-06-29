import httpx
from config import settings
from fastapi.responses import JSONResponse
from httpx import AsyncClient
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class AuthMiddleware(BaseHTTPMiddleware):
    NO_TOKEN_PATHS = [
        "/users/auth/register",
        "/users/auth/login",
        "/users/auth/verify_otp",
        "/users/auth/send_otp",
        "/users/auth/reset_password/otp",
        "/users/auth/refresh",
    ]

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.NO_TOKEN_PATHS:
            return await call_next(request)

        base_url = f"http://{settings.USER_SERVICE_HOST}:{settings.USER_SERVICE_PORT}/"
        method = "GET"
        endpoint = "validate"
        headers = dict(request.headers)
        headers.pop("content-length", None)

        async with AsyncClient(base_url=base_url) as client:
            try:
                response = await client.request(
                    method=method.upper(),
                    url=endpoint,
                    headers=headers,
                )
            except httpx.RequestError as e:
                return JSONResponse(
                    status_code=e.status_code, content={"detail": e.detail}
                )

            if response.status_code >= 400:
                try:
                    detail = response.json().get("detail", response.text)
                except Exception:
                    detail = response.text
                return JSONResponse(
                    status_code=response.status_code, content={"detail": detail}
                )

            user_id = response.json().get("user_id")

            request.headers.__dict__["_list"].append(
                (b"user_id", str(user_id).encode())
            )

        response = await call_next(request)

        return response
