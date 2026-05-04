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


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    tags=["System"],
    summary="Health check",
    description="Базовая проверка доступности сервиса"
)
async def health_check():
    """Возвращает статус работоспособности сервиса"""
    return HealthResponse(
        status="healthy",
        service="fastapi_core",
        version="1.0.0"
    )


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    status_code=status.HTTP_200_OK,
    tags=["System"],
    summary="Readiness check",
    description="Проверка готовности сервиса принимать трафик"
)
async def readiness_check():
    """
    Проверяет готовность всех зависимостей (БД, кэш, внешние API)
    TODO: Добавить реальную проверку БД после подключения SQLAlchemy
    TODO: Добавить проверку Django API после настройки django_client
    """
    dependencies = {
        "database": "ok",  # TODO: await check_database()
        "django_api": "ok"  # TODO: await check_django_api()
    }

    all_ready = all(v == "ok" for v in dependencies.values())

    return ReadinessResponse(
        status="ready" if all_ready else "not_ready",
        dependencies=dependencies
    )