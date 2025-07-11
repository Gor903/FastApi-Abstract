from core import settings
from fastapi import APIRouter, Request
from src.utils import dispatch, forward_request

router = APIRouter(
    prefix="/storage",
    tags=["storage-service"],
)

SERVICE_NAME = "storage_app"


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def gateway_proxy(request: Request, path: str):

    request = await dispatch(request=request)

    method = request.method
    base_url = f"http://{settings.STORAGE_APP_HOST}:{settings.STORAGE_APP_PORT}"
    headers = dict(request.headers)
    headers.pop("content-length", None)
    body = await request.body() if method in ["POST", "PUT", "PATCH"] else None

    response = await forward_request(
        method=method,
        base_url=base_url,
        endpoint=path,
        headers=headers,
        body=body,
        service_name=SERVICE_NAME,
    )

    return response
