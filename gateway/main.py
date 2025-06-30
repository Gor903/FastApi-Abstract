import httpx
from config import settings
from fastapi import FastAPI, HTTPException, Request, Response
from httpx import AsyncClient
from middleware import authorize, logger

app = FastAPI()
app.add_middleware(logger.LoggerMiddleware)
app.add_middleware(authorize.AuthMiddleware)


async def forward_request(
    method: str, base_url: str, endpoint: str, headers=None, body=None
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
        except httpx.RequestError as e:
            raise HTTPException(status_code=400, detail=f"Gateway error: {str(e)}")
    if response.status_code >= 400:
        try:
            detail = response.json().get("detail", response.text)
        except Exception:
            detail = response.text
        raise HTTPException(status_code=response.status_code, detail=detail)
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.headers.get("content-type"),
    )


@app.api_route("/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def gateway_proxy(request: Request, path: str):
    method = request.method
    base_url = f"http://{settings.USER_SERVICE_HOST}:{settings.USER_SERVICE_PORT}"
    headers = dict(request.headers)
    headers.pop("content-length", None)
    body = await request.body() if method in ["POST", "PUT", "PATCH"] else None

    response = await forward_request(
        method=method,
        base_url=base_url,
        endpoint=path,
        headers=headers,
        body=body,
    )

    return response
