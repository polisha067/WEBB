from fastapi import Depends, HTTPException, status, Header
from app.core.config import settings
import httpx
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.core.security import ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

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


async def get_current_user_jwt(token: str = Depends(oauth2_scheme)) -> dict:
    """Получает пользователя из JWT токена (Bearer)"""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "Not authenticated"}
        )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "INVALID_TOKEN", "message": "Token is not an access token"}
            )
            
        return {"id": payload.get("sub"), "username": payload.get("username"), "django_token": payload.get("django_token", "")}
        
    except (JWTError, Exception):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_TOKEN", "message": "Token is invalid or expired"}
        )


async def get_current_active_user(current_user: dict = Depends(get_current_user_jwt)) -> dict:
    """Проверяет, что пользователь активен (заглушка для расширения)"""
    # В реальности: запрос в Django на проверку is_active
    return current_user