from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """Настройки приложения из переменных окружения."""
    APP_NAME: str = "FastAPI Core Service"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    SECRET_KEY: str = "dev-secret"
    DJANGO_API_URL: str = "http://web:8000/api"
    DJANGO_API_TIMEOUT: float = 5.0
    DJANGO_VERIFY_ENDPOINT: str = "/accounts/me/"
    DATABASE_URL: str = ""

    model_config = {"env_file": ".env", "extra": "ignore"}

settings = Settings()