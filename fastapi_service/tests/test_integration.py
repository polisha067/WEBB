import pytest
from fastapi import status
import respx
from httpx import Response


class TestDjangoIntegration:
    """Интеграционные тесты с Django API"""

    @pytest.mark.asyncio
    @respx.mock
    async def test_protected_profile_success(self, async_client, auth_headers):
        """GET /protected/profile: успешный запрос с моком Django"""
        # Мокаем ответ Django
        respx.get(f"{respx.settings.base_url}/api/accounts/me/").mock(
            return_value=Response(200, json={"id": 1, "username": "test", "email": "t@e.com"})
        )
        
        response = await async_client.get(
            "/api/v1/protected/profile",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == "test"

    @pytest.mark.asyncio
    @respx.mock
    async def test_protected_recommendations(self, async_client, auth_headers):
        """GET /protected/recommendations: проверка структуры ответа"""
        respx.get(f"{respx.settings.base_url}/api/movies/").mock(
            return_value=Response(200, json=[
                {"id": 1, "title": "Movie 1", "rating": 8.5},
                {"id": 2, "title": "Movie 2", "rating": 7.2}
            ])
        )
        
        response = await async_client.get(
            "/api/v1/protected/recommendations",
            headers=auth_headers,
            params={"limit": 2}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["recommendations"]) == 2
        assert "title" in data["recommendations"][0]

    @pytest.mark.asyncio
    async def test_protected_no_auth(self, async_client):
        """Защищённый эндпоинт без токена = 401"""
        response = await async_client.get("/api/v1/protected/profile")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED