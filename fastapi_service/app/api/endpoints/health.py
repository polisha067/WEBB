from fastapi import APIRouter, status
from pydantic import BaseModel
from typing import Dict, Literal
import httpx
from app.core.config import settings
from app.core.database import check_db_connection

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
    """Проверяет готовность зависимостей БД, Django API"""
    db_ok = await check_db_connection()

    django_ok = False
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(settings.DJANGO_API_URL.rstrip("/"))
            django_ok = resp.status_code < 500
    except Exception:
        django_ok = False

    dependencies = {
        "database": "ok" if db_ok else "failed",
        "django_api": "ok" if django_ok else "failed"
    }
    all_ready = all(v == "ok" for v in dependencies.values())
    return ReadinessResponse(status="ready" if all_ready else "not_ready", dependencies=dependencies)