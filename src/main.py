from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile

from src.core import setup_middlewares
from src.core.minio_client import upload_user_file
from src.db import init_db
from src.routes import auth_router


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

    app.include_router(auth_router)

    return app


app = create_app()


@app.post("/file")
async def post_file(
    file: UploadFile | None = None,
):
    if file:
        file_bytes = await file.read()
        image_url = upload_user_file(
            user_id=14,
            file_bytes=file_bytes,
            filename=file.filename,
            content_type=file.content_type,
            file_type="profile",
        )
    return {"image_url": image_url}


@app.get("/")
async def get_root():
    return {"message": "OK"}
