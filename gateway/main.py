from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from httpx import AsyncClient

from config import settings

app = FastAPI()



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
        return response


# @app.api_route("/proxy/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
# async def gateway_proxy(request: Request, path: str):
#     method = request.method
#     base_url = f"http://{settings.SERVICE2_HOST}:{settings.SERVICE2_PORT}"
#     headers = dict(request.headers)
#     body = await request.body() if method in ["POST", "PUT", "PATCH"] else None

#     response = await forward_request(
#         method=method,
#         base_url=base_url,
#         endpoint=path,
#         headers=headers,
#         body=body,
#     )

#     return JSONResponse(response)
