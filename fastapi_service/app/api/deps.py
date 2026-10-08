from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.security import decode_token
from app.schemas.auth import CurrentUser
from app.services.auth import AuthService
from app.services.django_client import DjangoClient
from app.services.movie_page import MoviePageService
from app.services.protected import ProtectedService
from app.services.ugc_client import UgcClient

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user_jwt(token: str | None = Depends(oauth2_scheme)) -> CurrentUser:
    """Получает пользователя из JWT (Bearer), декодируя токен локально в BFF.

    Похода в Django на каждый запрос нет: подпись и срок жизни access-токена
    проверяются здесь. Если Django-токен отозван, Django вернёт 401 при первом
    же проксируемом запросе, и он будет прокинут клиенту
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "Not authenticated"}
        )

    payload = decode_token(token, expected_type="access")
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_TOKEN", "message": "Token is invalid or expired"}
        )

    return CurrentUser(id=int(payload.sub), username=payload.username, django_token=payload.django_token)


def get_auth_service() -> AuthService:
    return AuthService(DjangoClient())


def get_protected_service() -> ProtectedService:
    return ProtectedService(DjangoClient())


def get_movie_page_service() -> MoviePageService:
    return MoviePageService(DjangoClient(), UgcClient())
