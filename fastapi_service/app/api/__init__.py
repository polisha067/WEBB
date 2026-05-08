from fastapi import APIRouter

from app.api.endpoints import auth, health, protected

api_router = APIRouter()
api_router.include_router(health.router, prefix="/system", tags=["System"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(protected.router, prefix="/protected", tags=["Protected"])