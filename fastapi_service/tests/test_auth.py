import pytest
from fastapi import status


class TestAuthEndpoints:
    """Тесты эндпоинтов аутентификации"""

    @pytest.mark.asyncio
    async def test_register_success(self, async_client, mock_user):
        """Регистрация: успешный сценарий"""
        response = await async_client.post(
            "/api/v1/auth/register",
            json={
                "username": mock_user["username"],
                "email": mock_user["email"],
                "password": mock_user["password"]
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_register_weak_password(self, async_client, mock_user):
        """Регистрация: слабый пароль"""
        response = await async_client.post(
            "/api/v1/auth/register",
            json={
                "username": mock_user["username"],
                "email": mock_user["email"],
                "password": "weak"  # нет заглавной и цифры
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_login_success(self, async_client, mock_user):
        """Логин: успешный сценарий"""
        response = await async_client.post(
            "/api/v1/auth/login",
            json={
                "username": mock_user["username"],
                "password": mock_user["password"]
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data

    @pytest.mark.asyncio
    async def test_refresh_token_success(self, async_client, mock_user):
        """Refresh: успешное обновление токена"""
        from app.core.security import create_refresh_token
        refresh = create_refresh_token(mock_user["id"], mock_user["username"])
        
        response = await async_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["access_token"] != refresh  # новый access токен

    @pytest.mark.asyncio
    async def test_refresh_invalid_token(self, async_client):
        """Refresh: невалидный токен"""
        response = await async_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid.token.here"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"]["code"] == "INVALID_TOKEN"