from fastapi import APIRouter
from .endpoints import auth_router
from .endpoints.protected import router as protected_router
from .endpoints.health import router as health_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(protected_router, prefix="/protected", tags=["Protected"])
api_router.include_router(health_router, prefix="/system", tags=["System"])