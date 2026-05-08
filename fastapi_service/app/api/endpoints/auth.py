from fastapi import APIRouter, HTTPException, status, Depends
from app.core.security import (
    get_password_hash, create_access_token, create_refresh_token,
    decode_token, verify_password
)
from app.schemas.auth import (
    UserCreate, LoginRequest, TokenResponse, RefreshRequest
)
from app.services.django_client import DjangoClient

router = APIRouter()

# В учебном проекте: "регистрация" = создание записи в Django через API
# Реальное хранение паролей — в Django, здесь только прокси-логика


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate):
    """Регистрация нового пользователя (прокси в Django)"""
    client = DjangoClient()
    
    # Проверяем, не занят ли username/email
    try:
        await client.request("GET", f"accounts/check/?username={user_in.username}")
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "USER_EXISTS", "message": "Username already taken"}
        )
    
    # В реальном проекте: отправка данных в Django для создания пользователя
    # Здесь эмулируем успешную регистрацию
    user_id = 1  # заглушка, в реальности — ответ от Django
    
    return TokenResponse(
        access_token=create_access_token(user_id, user_in.username),
        refresh_token=create_refresh_token(user_id, user_in.username)
    )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    """Вход: проверка через Django, возврат JWT"""
    client = DjangoClient()
    
    # В реальности: запрос к Django на проверку пароля
    # Здесь эмулируем успешный логин
    user = {"id": 1, "username": credentials.username}  # заглушка
    
    return TokenResponse(
        access_token=create_access_token(user["id"], user["username"]),
        refresh_token=create_refresh_token(user["id"], user["username"])
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshRequest):
    """Обновление access токена через refresh токен"""
    payload = decode_token(request.refresh_token, expected_type="refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_TOKEN", "message": "Refresh token is invalid or expired"}
        )
    
    # Rotation: новый refresh токен (опционально)
    new_access = create_access_token(payload.user_id, payload.username)
    new_refresh = create_refresh_token(payload.user_id, payload.username)
    
    return TokenResponse(access_token=new_access, refresh_token=new_refresh)