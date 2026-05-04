from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from app.core.config import settings
import httpx


async def verify_django_token(authorization: str = Header(..., alias="Authorization")) -> dict:
    """
    Верифицирует токен через Django API
    Ожидает формат: 'Token <key>' (как в DRF)
    """
    if not authorization.startswith("Token "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_HEADER", "message": "Authorization header must start with 'Token '"}
        )

    token = authorization.split("Token ")[1]

    async with httpx.AsyncClient(timeout=settings.DJANGO_API_TIMEOUT) as client:
        response = await client.get(
            f"{settings.DJANGO_API_URL}/accounts/me/",
            headers={"Authorization": f"Token {token}"}
        )

        if response.status_code == 401:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "UNAUTHORIZED", "message": "Invalid or expired Django token"}
            )
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail={"code": "DJANGO_API_ERROR", "message": "Auth service unavailable"}
            )

        return response.json()


async def get_current_user(payload: dict = Depends(verify_django_token)) -> dict:
    """
    Возвращает данные текущего пользователя после успешной верификации
    Используется как зависимость в защищённых эндпоинтах
    """
    return payload