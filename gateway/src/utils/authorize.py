import httpx
from core import settings
from exceptions.http_exceptions import GatewayException
from fastapi import HTTPException, Request
from httpx import AsyncClient

NO_TOKEN_PATHS = [
    "/users/auth/register",
    "/users/auth/login",
    "/users/auth/verify_otp",
    "/users/auth/send_otp",
    "/users/auth/reset_password/otp",
    "/docs",
    "/openapi.json",
]


async def dispatch(request: Request):
    if request.url.path in NO_TOKEN_PATHS:
        return request

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
            raise GatewayException(
                service_name="user_service", detail="Authorization request error"
            )

    if response.status_code >= 400:
        try:
            detail = response.json().get("detail", response.text)
        except Exception:
            detail = response.text
        raise GatewayException(service_name="user_service", detail=detail)

    user_id = response.json().get("user_id")

    request.headers.__dict__["_list"].append((b"user_id", str(user_id).encode()))

    return request
