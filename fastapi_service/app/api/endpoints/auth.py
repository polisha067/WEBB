from fastapi import APIRouter, status
import httpx
from app.core.config import settings
from app.core.exceptions import AppException
from app.core.security import (
    create_access_token, 
    create_refresh_token,
    ALGORITHM
)
from app.schemas.auth import (
    UserCreate, LoginRequest, TokenResponse, RefreshRequest
)
from jose import jwt, JWTError

router = APIRouter()

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate):
    """Регистрация нового пользователя через прокси в Django"""
    async with httpx.AsyncClient(timeout=settings.DJANGO_API_TIMEOUT) as client:
        try:
            response = await client.post(
                f"{settings.DJANGO_API_URL}/accounts/register/",
                json=user_in.model_dump()
            )
            
            if response.status_code != 201:
                try:
                    err_data = response.json()
                except Exception:
                    err_data = {}
                    
                raise AppException(
                    code=err_data.get("code", "REGISTRATION_FAILED"),
                    message=err_data.get("detail", "Registration failed"),
                    status_code=response.status_code,
                )
            
            user_data = response.json()
            user_id = user_data.get("user", {}).get("id", 0)
            username = user_data.get("user", {}).get("username", user_in.username)
            django_token = user_data.get("token", "")
            
            return TokenResponse(
                access_token=create_access_token(user_id=user_id, username=username, django_token=django_token),
                refresh_token=create_refresh_token(user_id=user_id, username=username, django_token=django_token)
            )
        except httpx.RequestError as e:
            raise AppException(
                code="DJANGO_API_UNAVAILABLE",
                message=f"Django service unavailable: {e}",
                status_code=503,
            )

@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    """Вход: реальная проверка через Django и возврат JWT"""
    async with httpx.AsyncClient(timeout=settings.DJANGO_API_TIMEOUT) as client:
        try:
            response = await client.post(
                f"{settings.DJANGO_API_URL}/accounts/login/",
                json={"username": credentials.username, "password": credentials.password}
            )
            
            if response.status_code != 200:
                raise AppException(
                    code="INVALID_CREDENTIALS",
                    message="Incorrect username or password",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )
            
            user_data = response.json()
            user_id = user_data.get("user", {}).get("id", 0)
            username = user_data.get("user", {}).get("username", credentials.username)
            django_token = user_data.get("token", "")
            
            return TokenResponse(
                access_token=create_access_token(user_id=user_id, username=username, django_token=django_token),
                refresh_token=create_refresh_token(user_id=user_id, username=username, django_token=django_token)
            )
        except httpx.RequestError as e:
            raise AppException(
                code="DJANGO_API_UNAVAILABLE",
                message=f"Django service unavailable: {e}",
                status_code=503,
            )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(body: RefreshRequest):
    """Обновление токенов с использованием rotation (выдача новой пары)"""
    try:
        payload = jwt.decode(body.refresh_token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise AppException(
                code="INVALID_TOKEN",
                message="Token is not a refresh token",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
            
        user_id = payload.get("sub")
        username = payload.get("username", "")
        django_token = payload.get("django_token", "")
        
        return TokenResponse(
            access_token=create_access_token(user_id=int(user_id), username=username, django_token=django_token),
            refresh_token=create_refresh_token(user_id=int(user_id), username=username, django_token=django_token)
        )
    except JWTError:
        raise AppException(
            code="INVALID_TOKEN",
            message="Invalid or expired refresh token",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )