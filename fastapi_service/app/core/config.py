from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """Базовые настройки приложения из ENV"""
    APP_NAME: str = "FastAPI Service"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    SECRET_KEY: str = "dev-secret"

    model_config = {"env_file": ".env", "extra": "ignore"}

settings = Settings()