import pytest
from fastapi import status
import respx
from httpx import Response

from app.core.config import settings


DJANGO_BASE = settings.DJANGO_API_URL.rstrip("/")


class TestAuthEndpoints:
    """Тесты эндпоинтов аутентификации"""

    @pytest.mark.asyncio
    @respx.mock
    async def test_register_success(self, async_client, mock_user):
        """Регистрация: успешный сценарий"""
        # Мокаем Django register endpoint
        respx.post(f"{DJANGO_BASE}/accounts/register/").mock(
            return_value=Response(201, json={"id": 1, "username": mock_user["username"]})
        )

        response = await async_client.post(
            "/api/v1/auth/register",
            json={
                "username": mock_user["username"],
                "email": mock_user["email"],
                "password": mock_user["password"],
                "password_confirm": mock_user["password"]
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_register_weak_password(self, async_client, mock_user):
        """Регистрация: слабый пароль - валидация Pydantic"""
        response = await async_client.post(
            "/api/v1/auth/register",
            json={
                "username": mock_user["username"],
                "email": mock_user["email"],
                "password": "weak",  # нет заглавной и цифры, < 8 символов
                "password_confirm": "weak"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert data["detail"]["code"] == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, async_client, mock_user):
        """Регистрация: невалидный email"""
        response = await async_client.post(
            "/api/v1/auth/register",
            json={
                "username": mock_user["username"],
                "email": "not-an-email",
                "password": mock_user["password"],
                "password_confirm": mock_user["password"]
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    @respx.mock
    async def test_login_success(self, async_client, mock_user):
        """Логин: успешный сценарий"""
        respx.post(f"{DJANGO_BASE}/accounts/login/").mock(
            return_value=Response(200, json={"id": 1, "username": mock_user["username"]})
        )

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
        assert "refresh_token" in data

    @pytest.mark.asyncio
    @respx.mock
    async def test_login_wrong_credentials(self, async_client, mock_user):
        """Логин: неверные данные - Django отклоняет"""
        respx.post(f"{DJANGO_BASE}/accounts/login/").mock(
            return_value=Response(401, json={"detail": "Invalid credentials"})
        )

        response = await async_client.post(
            "/api/v1/auth/login",
            json={
                "username": mock_user["username"],
                "password": "WrongPass1!"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"]["code"] == "INVALID_CREDENTIALS"

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
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["access_token"] != refresh  

    @pytest.mark.asyncio
    async def test_refresh_invalid_token(self, async_client):
        """Refresh: невалидный токен"""
        response = await async_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid.token.here"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"]["code"] == "INVALID_TOKEN"

    @pytest.mark.asyncio
    async def test_refresh_with_access_token(self, async_client, mock_user):
        """Refresh: попытка использовать access-токен вместо refresh"""
        from app.core.security import create_access_token
        access = create_access_token(mock_user["id"], mock_user["username"])

        response = await async_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": access}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"]["code"] == "INVALID_TOKEN"