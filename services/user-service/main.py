from contextlib import asynccontextmanager

from db import init_db
from exceptions import AppException, app_exception_handler
from fastapi import FastAPI
from src.routes import auth_router, users_router


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

    app.include_router(auth_router)
    app.include_router(users_router)

    return app


app = create_app()


@app.get("/")
async def get_root():
    return {"message": "OK"}
