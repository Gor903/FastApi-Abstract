from fastapi import APIRouter

from .endpoints import auth_router, users_router

router = APIRouter(
    prefix="/v1",
)

router.include_router(auth_router)
router.include_router(users_router)
