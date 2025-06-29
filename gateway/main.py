from fastapi import FastAPI, Request, Response

from httpx import AsyncClient

from config import settings
from middleware import logger, authorize


app = FastAPI()
app.add_middleware(logger.LoggerMiddleware)
app.add_middleware(authorize.AuthMiddleware)


async def forward_request(
    method: str, base_url: str, endpoint: str, headers=None, body=None
):
    async with AsyncClient(base_url=base_url) as client:
        response = None
        try:

            safe_headers = {
                k: v
                for k, v in (headers or {}).items()
                if k.lower() != "content-length"
            }

            response = await client.request(
                method=method.upper(),
                url=endpoint,
                headers=safe_headers,
                content=body,
            )
        except Exception as e:
            print(f"forward error: {e}")
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type")
        )


@app.api_route("/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def gateway_proxy(request: Request, path: str):
    method = request.method
    base_url = f"http://user-service:8001"
    headers = dict(request.headers)
    body = await request.body() if method in ["POST", "PUT", "PATCH"] else None

    response = await forward_request(
        method=method,
        base_url=base_url,
        endpoint=path,
        headers=headers,
        body=body,
    )
    
    return response