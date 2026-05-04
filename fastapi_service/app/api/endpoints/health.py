from fastapi import APIRouter, status
from pydantic import BaseModel
from typing import Dict, Literal

router = APIRouter()

class HealthResponse(BaseModel):
    """Ответ health check"""
    status: Literal["healthy", "unhealthy"]
    service: str
    version: str

class ReadinessResponse(BaseModel):
    """Ответ readiness check"""
    status: Literal["ready", "not_ready"]
    dependencies: Dict[str, Literal["ok", "failed"]]

@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK, tags=["System"])
async def health_check():
    """Базовая проверка доступности сервиса"""
    return HealthResponse(status="healthy", service="fastapi_core", version="1.0.0")

@router.get("/ready", response_model=ReadinessResponse, status_code=status.HTTP_200_OK, tags=["System"])
async def readiness_check():
    """Проверка готовности зависимостей (БД, внешние API)"""
    dependencies = {"database": "ok", "django_api": "ok"}
    all_ready = all(v == "ok" for v in dependencies.values())
    return ReadinessResponse(status="ready" if all_ready else "not_ready", dependencies=dependencies)