from fastapi import FastAPI
from src.routes import notific_router


def create_app() -> FastAPI:
    app = FastAPI()

    app.include_router(notific_router)

    return app


app = create_app()


@app.get("/")
async def get_root():
    return {"message": "OK"}
