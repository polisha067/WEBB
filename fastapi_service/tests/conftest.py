import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.security import create_access_token


@pytest.fixture
def mock_user():
    """Тестовый пользователь"""
    return {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123!",
    }


@pytest.fixture
def auth_headers(mock_user) -> dict:
    """Заголовки с валидным JWT access-токеном (для protected-эндпоинтов через JWT)"""
    token = create_access_token(user_id=mock_user["id"], username=mock_user["username"])
    return {"Authorization": f"Token {token}"}


@pytest.fixture
def jwt_bearer_headers(mock_user) -> dict:
    """Заголовки с Bearer JWT (для эндпоинтов, использующих get_current_user_jwt)"""
    token = create_access_token(user_id=mock_user["id"], username=mock_user["username"])
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def async_client():
    """Async HTTP-клиент для тестов (без реальной БД/сети)"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client