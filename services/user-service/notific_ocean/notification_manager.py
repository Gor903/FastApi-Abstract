import json

import httpx
from exceptions.http_exceptions import HTTPXException
from fastapi import HTTPException
from httpx import AsyncClient
from starlette import status


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
