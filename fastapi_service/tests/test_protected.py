import pytest
from fastapi import status
import respx
from httpx import Response
from datetime import datetime

from app.core.config import settings

DJANGO_BASE = settings.DJANGO_API_URL.rstrip("/")


class TestProtectedEndpoints:
    """Тесты защищённых эндпоинтов (валидация схем)"""

    @pytest.mark.asyncio
    @respx.mock
    async def test_progress_report_request(self, async_client, jwt_bearer_headers):
        """POST /protected/progress/report: валидный запрос"""
        respx.get(f"{DJANGO_BASE}/accounts/me/").mock(
            return_value=Response(200, json={"id": 1, "username": "test", "email": "t@e.com"})
        )

        response = await async_client.post(
            "/api/v1/protected/progress/report",
            headers=jwt_bearer_headers,
            json={
                "period_days": 14,
                "include_recommendations": True
            }
        )
        assert response.status_code == status.HTTP_202_ACCEPTED
        data = response.json()
        assert data["status"] == "accepted"
        assert "request_id" in data
        assert "queued_at" in data
        # Проверка формата даты
        datetime.fromisoformat(data["queued_at"].replace("Z", "+00:00"))

    @pytest.mark.asyncio
    @respx.mock
    async def test_progress_report_validation(self, async_client, jwt_bearer_headers):
        """POST /protected/progress/report: невалидные данные"""
        respx.get(f"{DJANGO_BASE}/accounts/me/").mock(
            return_value=Response(200, json={"id": 1, "username": "test", "email": "t@e.com"})
        )

        response = await async_client.post(
            "/api/v1/protected/progress/report",
            headers=jwt_bearer_headers,
            json={
                "period_days": 200,  # > 90, не пройдёт валидацию
                "include_recommendations": "yes"  # должен быть bool
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert data["detail"]["code"] == "VALIDATION_ERROR"