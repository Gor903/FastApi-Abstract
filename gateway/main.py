from contextlib import asynccontextmanager

from fastapi import FastAPI

# from core import setup_middlewares
# from db import init_db
# from src.routes import auth_router


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     try:
#         await init_db()
#     except Exception as e:
#         print(f"[Startup Error] DB init failed: {e}")
#     yield


def create_app() -> FastAPI:
    app = FastAPI(
        # lifespan=lifespan,
    )

    # setup_middlewares(app)

    # app.include_router(auth_router)

    return app


app = create_app()


@app.get("/")
async def get_root():
    return {"message": "OK"}
