from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    """Настройки приложения из переменных окружения"""
    APP_NAME: str = Field(default="FastAPI Core Service", alias="FASTAPI_APP_NAME")
    DEBUG: bool = Field(default=False, alias="FASTAPI_DEBUG")
    LOG_LEVEL: str = Field(default="INFO", alias="FASTAPI_LOG_LEVEL")
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:3000"], alias="FASTAPI_CORS_ORIGINS")
    SECRET_KEY: str = Field(default="dev-secret", alias="FASTAPI_SECRET_KEY")

    # Интеграция с Django
    DJANGO_API_URL: str = Field(default="http://web:8000/api", alias="FASTAPI_DJANGO_API_URL")
    DJANGO_API_TIMEOUT: float = Field(default=5.0, alias="FASTAPI_DJANGO_API_TIMEOUT")
    DJANGO_API_RETRIES: int = Field(default=2, alias="FASTAPI_DJANGO_API_RETRIES")
    DJANGO_API_BACKOFF_BASE: float = Field(default=0.3, alias="FASTAPI_DJANGO_API_BACKOFF_BASE")
    DJANGO_VERIFY_ENDPOINT: str = "/accounts/me/"
    DJANGO_RECOMMENDATIONS_ENDPOINT: str = "/movies/"

    # Фоновые задачки
    NOTIFICATION_WEBHOOK_URL: str = Field(default="", alias="FASTAPI_NOTIFICATION_WEBHOOK_URL")

    # БД
    DATABASE_URL: str = Field(default="", alias="FASTAPI_DATABASE_URL")

    model_config = {"env_file": ".env", "extra": "ignore", "populate_by_name": True}


settings = Settings()