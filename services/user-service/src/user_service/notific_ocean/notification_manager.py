import json

import httpx
from fastapi import HTTPException
from httpx import AsyncClient
from starlette import status
from user_service.exceptions.http_exceptions import HTTPXException


async def async_request(
    method: str, base_url: str, endpoint: str, headers=None, body=None
):
    async with AsyncClient(base_url=base_url) as client:
        try:
            body = json.dumps(body)

            await client.request(
                method=method.upper(),
                url=endpoint,
                headers=headers,
                content=body,
            )
        except httpx.RequestError:
            raise HTTPXException(
                sender="Notific Oceaen", detail=f"Request error at: {endpoint}"
            )
