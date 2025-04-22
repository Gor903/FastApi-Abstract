from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.db import init_db
from src.core import setup_middlewares


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()
    except Exception as e:
        print(f"[Startup Error] DB init failed: {e}")
    yield


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    setup_middlewares(app)

    return app


app = create_app()


@app.get("/")
async def get_root():
    return {"message": "OK"}
