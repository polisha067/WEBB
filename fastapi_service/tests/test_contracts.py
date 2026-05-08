import pytest
from pydantic import TypeAdapter, ValidationError

from app.schemas.auth import TokenResponse, UserCreate, LoginRequest, RefreshRequest
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
        assert result.email == "t@e.com"

    def test_profile_response_rejects_missing_fields(self):
        """ProfileResponse: отклоняет данные без обязательных полей"""
        adapter = TypeAdapter(ProfileResponse)
        with pytest.raises(ValidationError):
            adapter.validate_python({"id": 1})  # нет username, email

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

    def test_recommendations_empty_list(self):
        """RecommendationsResponse: пустой список"""
        adapter = TypeAdapter(RecommendationsResponse)
        result = adapter.validate_python({"recommendations": []})
        assert len(result.recommendations) == 0

    def test_auth_schemas_validation(self):
        """Auth-схемы: валидация входных данных"""
        # UserCreate
        user = UserCreate(username="new_user", email="n@e.com", password="Pass123!", password_confirm="Pass123!")
        assert user.username == "new_user"

        # LoginRequest
        login = LoginRequest(username="test", password="pwd")
        assert login.username == "test"

        # TokenResponse
        token = TokenResponse(access_token="abc", refresh_token="xyz")
        assert token.token_type == "bearer"

        # RefreshRequest
        refresh = RefreshRequest(refresh_token="some.jwt.token")
        assert refresh.refresh_token == "some.jwt.token"

    def test_user_create_weak_password_rejected(self):
        """UserCreate: пароль без заглавной/цифры отклоняется"""
        with pytest.raises(ValidationError):
            UserCreate(username="usr", email="u@e.com", password="nouppercaseordigit", password_confirm="nouppercaseordigit")

    def test_user_create_short_password_rejected(self):
        """UserCreate: короткий пароль отклоняется"""
        with pytest.raises(ValidationError):
            UserCreate(username="usr", email="u@e.com", password="Ab1", password_confirm="Ab1")

    def test_user_create_invalid_email_rejected(self):
        """UserCreate: невалидный email отклоняется"""
        with pytest.raises(ValidationError):
            UserCreate(username="usr", email="not-email", password="ValidPass1!", password_confirm="ValidPass1!")

    def test_user_create_passwords_mismatch(self):
        """UserCreate: пароли не совпадают"""
        with pytest.raises(ValidationError):
            UserCreate(username="usr", email="u@e.com", password="ValidPass1!", password_confirm="DifferentPass2!")