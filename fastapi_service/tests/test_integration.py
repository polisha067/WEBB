import pytest
from fastapi import status
import respx
from httpx import Response

from app.core.config import settings

DJANGO_BASE = settings.DJANGO_API_URL.rstrip("/")


class TestDjangoIntegration:
    """Интеграционные тесты с Django API (мокирование через respx)"""

    @pytest.mark.asyncio
    @respx.mock
    async def test_protected_profile_success(self, async_client, jwt_bearer_headers):
        """GET /protected/profile: успешный запрос с моком Django"""
        respx.get(f"{DJANGO_BASE}/accounts/me/").mock(
            return_value=Response(200, json={"id": 1, "username": "test", "email": "t@e.com"})
        )

        response = await async_client.get(
            "/api/v1/protected/profile",
            headers=jwt_bearer_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == "test"
        assert data["email"] == "t@e.com"

    @pytest.mark.asyncio
    @respx.mock
    async def test_protected_recommendations(self, async_client, jwt_bearer_headers):
        """GET /protected/recommendations: проверка структуры ответа"""
        # Мокаем два вызова: verify_django_token + recommendations
        respx.get(f"{DJANGO_BASE}/accounts/me/").mock(
            return_value=Response(200, json={"id": 1, "username": "test", "email": "t@e.com"})
        )
        respx.get(f"{DJANGO_BASE}/movies/").mock(
            return_value=Response(200, json=[
                {"id": 1, "title": "Movie 1", "rating": 8.5},
                {"id": 2, "title": "Movie 2", "rating": 7.2}
            ])
        )

        response = await async_client.get(
            "/api/v1/protected/recommendations",
            headers=jwt_bearer_headers,
            params={"limit": 2}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["recommendations"]) == 2
        assert data["recommendations"][0]["title"] == "Movie 1"

    @pytest.mark.asyncio
    async def test_protected_no_auth(self, async_client):
        """Защищённый эндпоинт без токена = 422 (отсутствует Header)"""
        response = await async_client.get("/api/v1/protected/profile")
        assert response.status_code in (
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    @pytest.mark.asyncio
    @respx.mock
    async def test_protected_django_401(self, async_client, jwt_bearer_headers):
        """Защищённый эндпоинт с невалидным Django-токеном -> 401"""
        respx.get(f"{DJANGO_BASE}/accounts/me/").mock(
            return_value=Response(401, json={"detail": "Invalid token"})
        )

        response = await async_client.get(
            "/api/v1/protected/profile",
            headers=jwt_bearer_headers
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    @respx.mock
    async def test_background_task_progress_report(self, async_client, jwt_bearer_headers):
        """POST /protected/progress/report -> 202 и BackgroundTask запланирована"""
        respx.get(f"{DJANGO_BASE}/accounts/me/").mock(
            return_value=Response(200, json={"id": 1, "username": "test", "email": "t@e.com"})
        )

        response = await async_client.post(
            "/api/v1/protected/progress/report",
            headers=jwt_bearer_headers,
            json={"period_days": 7, "include_recommendations": True}
        )
        assert response.status_code == status.HTTP_202_ACCEPTED
        data = response.json()
        assert data["status"] == "accepted"
        assert "request_id" in data
        assert "queued_at" in data