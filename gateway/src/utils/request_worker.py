import httpx
from exceptions.http_exceptions import GatewayException
from fastapi import HTTPException, Response
from httpx import AsyncClient


async def forward_request(
    method: str,
    base_url: str,
    endpoint: str,
    service_name: str,
    headers=None,
    body=None,
):
    async with AsyncClient(base_url=base_url) as client:
        response = None
        try:
            response = await client.request(
                method=method.upper(),
                url=endpoint,
                headers=headers,
                content=body,
            )
        except httpx.RequestError:
            raise GatewayException(
                service_name=service_name, detail="Request forward error"
            )
    if response.status_code >= 400:
        try:
            detail = response.json().get("detail", response.text)
        except Exception:
            detail = response.text
        raise GatewayException(service_name=service_name, detail=detail)

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.headers.get("content-type"),
    )
