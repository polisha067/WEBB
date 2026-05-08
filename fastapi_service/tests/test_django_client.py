import pytest
import respx
from httpx import Response, ConnectError

from app.services.django_client import DjangoClient
from app.core.config import settings
from app.core.exceptions import AppException

DJANGO_BASE = settings.DJANGO_API_URL.rstrip("/")


class TestDjangoClient:
    """Юнит-тесты на DjangoClient (без HTTP-сервера)"""

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_success(self):
        """Успешный GET-запрос"""
        respx.get(f"{DJANGO_BASE}/movies/").mock(
            return_value=Response(200, json=[{"id": 1, "title": "Test"}])
        )
        client = DjangoClient()
        result = await client.request("GET", "/movies/")
        assert isinstance(result, list)
        assert result[0]["title"] == "Test"

    @pytest.mark.asyncio
    @respx.mock
    async def test_post_success(self):
        """Успешный POST-запрос"""
        respx.post(f"{DJANGO_BASE}/accounts/register/").mock(
            return_value=Response(201, json={"id": 1, "username": "new"})
        )
        client = DjangoClient()
        result = await client.request("POST", "/accounts/register/", json_body={"username": "new"})
        assert result["id"] == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_404_raises_app_exception(self):
        """404 от Django -> AppException(NOT_FOUND)"""
        respx.get(f"{DJANGO_BASE}/movies/999/").mock(
            return_value=Response(404, json={"detail": "Not found"})
        )
        client = DjangoClient()
        with pytest.raises(AppException) as exc_info:
            await client.request("GET", "/movies/999/")
        assert exc_info.value.code == "NOT_FOUND"
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    @respx.mock
    async def test_401_raises_unauthorized(self):
        """401 от Django -> AppException(UNAUTHORIZED)"""
        respx.get(f"{DJANGO_BASE}/accounts/me/").mock(
            return_value=Response(401, json={"detail": "Invalid token"})
        )
        client = DjangoClient()
        with pytest.raises(AppException) as exc_info:
            await client.request("GET", "/accounts/me/")
        assert exc_info.value.code == "UNAUTHORIZED"

    @pytest.mark.asyncio
    @respx.mock
    async def test_500_retries_then_raises(self):
        """5xx от Django -> retry, затем AppException"""
        route = respx.get(f"{DJANGO_BASE}/movies/").mock(
            return_value=Response(500, json={"detail": "Server error"})
        )
        client = DjangoClient()
        with pytest.raises(AppException) as exc_info:
            await client.request("GET", "/movies/")
        assert exc_info.value.code == "DJANGO_API_ERROR"
        # Должно быть retries + 1 вызовов (initial + 2 retries)
        assert route.call_count == settings.DJANGO_API_RETRIES + 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_network_error_retries_then_raises(self):
        """Сетевая ошибка -> retry, затем DJANGO_API_UNAVAILABLE"""
        respx.get(f"{DJANGO_BASE}/movies/").mock(
            side_effect=ConnectError("Connection refused")
        )
        client = DjangoClient()
        with pytest.raises(AppException) as exc_info:
            await client.request("GET", "/movies/")
        assert exc_info.value.code == "DJANGO_API_UNAVAILABLE"
        assert exc_info.value.status_code == 503
