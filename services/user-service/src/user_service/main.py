from contextlib import asynccontextmanager

from fastapi import FastAPI
from user_service.api.v1 import router as api_v1_router
from user_service.db import init_db
from user_service.exceptions import AppException, app_exception_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()
    except Exception as e:
        print(f"[Startup Error] DB init failed: {e}")
    yield


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    app.add_exception_handler(AppException, app_exception_handler)

    app.include_router(api_v1_router)

    return app


app = create_app()


@app.get("/")
async def get_root():
    return {"message": "OK"}
