from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    """Настройки приложения из переменных окружения"""
    APP_NAME: str = Field(default="FastAPI Core Service", alias="FASTAPI_APP_NAME")

    DEBUG: bool = Field(default=True, alias="FASTAPI_DEBUG")
    
    LOG_LEVEL: str = Field(default="INFO", alias="FASTAPI_LOG_LEVEL")
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:3000"], alias="FASTAPI_CORS_ORIGINS")

    # JWT
    SECRET_KEY: str = Field(default="dev-secret", alias="FASTAPI_SECRET_KEY")
    JWT_ALGORITHM: str = Field(default="HS256", alias="FASTAPI_JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, alias="FASTAPI_ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, alias="FASTAPI_REFRESH_TOKEN_EXPIRE_DAYS")

    # Интеграция с Django
    DJANGO_API_URL: str = Field(default="http://web:8000/api", alias="FASTAPI_DJANGO_API_URL")
    DJANGO_API_TIMEOUT: float = Field(default=5.0, alias="FASTAPI_DJANGO_API_TIMEOUT")
    DJANGO_API_RETRIES: int = Field(default=2, alias="FASTAPI_DJANGO_API_RETRIES")
    DJANGO_API_BACKOFF_BASE: float = Field(default=0.3, alias="FASTAPI_DJANGO_API_BACKOFF_BASE")
    DJANGO_PROFILE_ENDPOINT: str = "/accounts/me/"
    DJANGO_REGISTER_ENDPOINT: str = "/accounts/register/"
    DJANGO_LOGIN_ENDPOINT: str = "/accounts/login/"
    DJANGO_MOVIES_ENDPOINT: str = Field(default="/movies/movies/", alias="FASTAPI_DJANGO_MOVIES_ENDPOINT")

    # Интеграция с UGC (Flask)
    UGC_API_URL: str = Field(default="http://ugc_service:5001/api/v1", alias="FASTAPI_UGC_API_URL")
    UGC_API_TIMEOUT: float = Field(default=3.0, alias="FASTAPI_UGC_API_TIMEOUT")
    UGC_API_RETRIES: int = Field(default=1, alias="FASTAPI_UGC_API_RETRIES")

    # Фоновые задачки
    NOTIFICATION_WEBHOOK_URL: str = Field(default="", alias="FASTAPI_NOTIFICATION_WEBHOOK_URL")

    # БД
    DATABASE_URL: str = Field(default="", alias="FASTAPI_DATABASE_URL")

    model_config = {"env_file": ".env", "extra": "ignore", "populate_by_name": True}


settings = Settings()