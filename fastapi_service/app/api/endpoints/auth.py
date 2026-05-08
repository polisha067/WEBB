from fastapi import APIRouter, HTTPException, status, Depends
import httpx
from app.core.config import settings
from app.core.security import (
    create_access_token, 
    create_refresh_token,
    ALGORITHM
)
from app.schemas.auth import (
    UserCreate, LoginRequest, TokenResponse
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
                json=user_in.dict()
            )
            
            if response.status_code != 201:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json()
                )
            
            user_data = response.json()
            user_id = user_data.get("id")
            
            return TokenResponse(
                access_token=create_access_token(subject=user_id),
                refresh_token=create_refresh_token(subject=user_id)
            )
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Django service unavailable")

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
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password"
                )
            
            user_data = response.json()
            user_id = user_data.get("id")
            
            return TokenResponse(
                access_token=create_access_token(subject=user_id),
                refresh_token=create_refresh_token(subject=user_id)
            )
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Django service unavailable")

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str):
    """Обновление токенов с использованием rotation (выдача новой пары)"""
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
            
        user_id = payload.get("sub")
        
        return TokenResponse(
            access_token=create_access_token(subject=user_id),
            refresh_token=create_refresh_token(subject=user_id)
        )
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")