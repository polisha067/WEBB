from fastapi import status

from app.contracts import parse_contract
from app.contracts.django import DjangoAuthResponse
from app.core.config import settings
from app.core.exceptions import AppException
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse, UserCreate
from app.services.django_client import DjangoClient


class AuthService:
    """Аутентификация через Django (провайдер) с выдачей собственных JWT.

    Эндпоинты знают только про этот сервис: при смене провайдера
    авторизации меняется реализация здесь, а не ручки
    """

    def __init__(self, django_client: DjangoClient) -> None:
        self._django_client = django_client

    async def register(self, user_in: UserCreate) -> TokenResponse:
        data = await self._django_client.request(
            method="POST",
            endpoint=settings.DJANGO_REGISTER_ENDPOINT,
            json_body=user_in.model_dump(),
        )
        return self._issue_tokens(parse_contract(DjangoAuthResponse, data, source="Django"))

    async def login(self, credentials: LoginRequest) -> TokenResponse:
        try:
            data = await self._django_client.request(
                method="POST",
                endpoint=settings.DJANGO_LOGIN_ENDPOINT,
                json_body=credentials.model_dump(),
            )
        except AppException as exc:
            if exc.status_code >= 500:
                raise
            raise AppException(
                code="INVALID_CREDENTIALS",
                message="Incorrect username or password",
                status_code=status.HTTP_401_UNAUTHORIZED,
            ) from exc
        return self._issue_tokens(parse_contract(DjangoAuthResponse, data, source="Django"))

    async def refresh(self, body: RefreshRequest) -> TokenResponse:
        """Rotation: по валидному refresh-токену выдаётся новая пара"""
        payload = decode_token(body.refresh_token, expected_type="refresh")
        if payload is None:
            raise AppException(
                code="INVALID_TOKEN",
                message="Invalid or expired refresh token",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        return self._make_pair(int(payload.sub), payload.username, payload.django_token)

    def _issue_tokens(self, auth: DjangoAuthResponse) -> TokenResponse:
        return self._make_pair(auth.user.id, auth.user.username, auth.token)

    @staticmethod
    def _make_pair(user_id: int, username: str, django_token: str) -> TokenResponse:
        return TokenResponse(
            access_token=create_access_token(user_id=user_id, username=username, django_token=django_token),
            refresh_token=create_refresh_token(user_id=user_id, username=username, django_token=django_token),
        )
