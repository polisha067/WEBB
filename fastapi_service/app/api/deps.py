from fastapi import Depends, HTTPException, status, Header
from app.core.config import settings
import httpx


async def verify_django_token(authorization: str = Header(..., alias="Authorization")) -> dict:
    """Верифицирует токен через Django API. Ожидает формат: Token <key>"""
    if not authorization.startswith("Token "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_HEADER", "message": "Authorization header must start with 'Token '"}
        )

    token = authorization.split("Token ", 1)[1]
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "Token is empty"}
        )

    async with httpx.AsyncClient(timeout=settings.DJANGO_API_TIMEOUT) as client:
        try:
            response = await client.get(
                f"{settings.DJANGO_API_URL}{settings.DJANGO_VERIFY_ENDPOINT}",
                headers={"Authorization": f"Token {token}"}
            )

            if response.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={"code": "UNAUTHORIZED", "message": "Invalid or expired Django token"}
                )

            if response.status_code != 200:
                django_err = response.json()
                raise HTTPException(
                    status_code=response.status_code,
                    detail={"code": django_err.get("code", "DJANGO_API_ERROR"),
                            "message": django_err.get("detail", "Django API error")}
                )

            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"code": "DJANGO_API_UNAVAILABLE", "message": str(e)}
            )


async def get_current_user(payload: dict = Depends(verify_django_token)) -> dict:
    """Возвращает данные пользователя после успешной верификации"""
    return payload