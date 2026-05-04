from fastapi import APIRouter
from app.api.endpoints import health, auth

api_router = APIRouter()

# System endpoints 
api_router.include_router(
    health.router,
    prefix="/system",
    tags=["System"]
)

# Auth endpoints
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

# TODO (Dev 3):
# from app.api.endpoints import protected
# api_router.include_router(protected.router, prefix="/protected", tags=["Protected"])

# TODO (Lead):
# Стратегия версионирования:
# - v1: /api/v1/... (текущая версия)
# - v2: /api/v2/... (будущая версия, backward compatible)
# Health endpoints вне версионирования (инфраструктура)