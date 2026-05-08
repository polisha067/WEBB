import pytest
from fastapi import status
from datetime import datetime


class TestProtectedEndpoints:
    """Тесты защищённых эндпоинтов (валидация схем)"""

    @pytest.mark.asyncio
    async def test_progress_report_request(self, async_client, auth_headers):
        """POST /protected/progress/report: валидный запрос"""
        response = await async_client.post(
            "/api/v1/protected/progress/report",
            headers=auth_headers,
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
    async def test_progress_report_validation(self, async_client, auth_headers):
        """POST /protected/progress/report: невалидные данные"""
        response = await async_client.post(
            "/api/v1/protected/progress/report",
            headers=auth_headers,
            json={
                "period_days": 200,  # > 90, не пройдёт валидацию
                "include_recommendations": "yes"  # должен быть bool
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY