import pytest
from fastapi import status
import respx
from httpx import Response

from app.core.config import settings

DJANGO_BASE = settings.DJANGO_API_URL.rstrip("/")


class TestHealthEndpoints:
    """Тесты системных эндпоинтов health / readiness"""

    @pytest.mark.asyncio
    async def test_health_check(self, async_client):
        """GET /system/health: сервис отвечает healthy"""
        response = await async_client.get("/api/v1/system/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "fastapi_core"
        assert data["version"] == "1.0.0"

    @pytest.mark.asyncio
    @respx.mock
    async def test_readiness_check_all_ok(self, async_client):
        """GET /system/ready: все зависимости доступны"""
        respx.get(f"{DJANGO_BASE}").mock(
            return_value=Response(200, json={"status": "ok"})
        )

        response = await async_client.get("/api/v1/system/ready")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # DB может быть ok (sqlite) или failed, но Django мокнут
        assert "dependencies" in data
        assert data["dependencies"]["django_api"] == "ok"

    @pytest.mark.asyncio
    @respx.mock
    async def test_readiness_check_django_down(self, async_client):
        """GET /system/ready: Django API недоступен"""
        respx.get(f"{DJANGO_BASE}").mock(
            return_value=Response(500, json={"error": "Internal server error"})
        )

        response = await async_client.get("/api/v1/system/ready")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["dependencies"]["django_api"] == "failed"

    @pytest.mark.asyncio
    async def test_ping(self, async_client):
        """GET /ping: базовый healthcheck"""
        response = await async_client.get("/ping")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "ok"}
