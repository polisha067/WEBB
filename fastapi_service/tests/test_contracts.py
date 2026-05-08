import pytest
from pydantic import TypeAdapter

from app.schemas.auth import TokenResponse, UserCreate, LoginRequest
from app.schemas.protected import ProfileResponse, RecommendationsResponse


class TestContractCompliance:
    """Проверка соответствия DTO контрактам из docs/integration_contracts.md"""

    def test_profile_response_matches_contract(self):
        """ProfileResponse: поля соответствуют контракту Django"""
        adapter = TypeAdapter(ProfileResponse)
        sample = {"id": 1, "username": "test", "email": "t@e.com"}
        result = adapter.validate_python(sample)
        assert result.id == 1
        assert result.username == "test"

    def test_recommendations_structure(self):
        """RecommendationsResponse: структура списка рекомендаций"""
        adapter = TypeAdapter(RecommendationsResponse)
        sample = {
            "recommendations": [
                {"id": 102, "title": "Interstellar", "rating": 8.6}
            ]
        }
        result = adapter.validate_python(sample)
        assert len(result.recommendations) == 1
        assert result.recommendations[0].title == "Interstellar"

    def test_auth_schemas_validation(self):
        """Auth-схемы: валидация входных данных"""
        # UserCreate
        user = UserCreate(username="new", email="n@e.com", password="Pass123!")
        assert user.username == "new"
        
        # LoginRequest
        login = LoginRequest(username="test", password="pwd")
        assert login.username == "test"
        
        # TokenResponse
        token = TokenResponse(access_token="abc", refresh_token="xyz")
        assert token.token_type == "bearer"