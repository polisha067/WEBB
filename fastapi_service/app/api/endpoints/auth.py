from fastapi import APIRouter, Depends, status

from app.api.deps import get_auth_service
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse, UserCreate
from app.services.auth import AuthService

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, service: AuthService = Depends(get_auth_service)) -> TokenResponse:
    """Регистрация нового пользователя через Django"""
    return await service.register(user_in)


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, service: AuthService = Depends(get_auth_service)) -> TokenResponse:
    """Вход: проверка через Django и выдача JWT"""
    return await service.login(credentials)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(body: RefreshRequest, service: AuthService = Depends(get_auth_service)) -> TokenResponse:
    """Обновление токенов с использованием rotation (выдача новой пары)"""
    return await service.refresh(body)
