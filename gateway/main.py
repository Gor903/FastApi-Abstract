from exceptions import AppException, app_exception_handler
from exceptions.http_exceptions import GatewayException
from fastapi import FastAPI
from src.middlewares import logger
from src.routes import storage_app_router, user_service_router


def create_app() -> FastAPI:
    app = FastAPI()
    app.add_exception_handler(AppException, app_exception_handler)

    app.add_middleware(logger.LoggerMiddleware)

    app.include_router(user_service_router)
    app.include_router(storage_app_router)

    return app


app = create_app()


@app.get("/")
async def get_root():
    return {"message": "OK"}
