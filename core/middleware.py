import json
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from core import settings


def setup_middlewares(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 2. Custom Logging Middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000

        print(
            f"[{request.method}] {request.url.path} "
            f"completed in {process_time:.2f}ms "
            f"with status {response.status_code}"
        )
        return response

    # @app.middleware("http")
    # async def auth(request: Request, call_next):
    #
    #     if request.method == "POST":
    #         body_bytes = await request.body()
    #         body = json.loads(body_bytes.decode("utf-8"))
    #
    #         print(body)
    #
    #     response = await call_next(request)
    #     return response
