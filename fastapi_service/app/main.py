import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.middleware.request_id import RequestIDMiddleware
from app.api import api_router

# Базовая настройка логирования
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Жизненный цикл приложения: инициализация при старте и очистка при остановке"""
    logger.info("FastAPI service starting...")
    # TODO: Инициализация БД (asyncpg/SQLAlchemy), кэша, внешних клиентов
    # TODO: Применение миграций Alembic (если требуется авто-миграция при старте)
    yield
    logger.info("FastAPI service shutting down...")
    # TODO: Graceful shutdown подключений к БД, кэшу, фоновым задачам

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Core FastAPI service (Sprint 3) - Async, Auth, Production-ready",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={"name": "Dev Team", "email": "dev@example.com"},
    license_info={"name": "MIT"},
    security_schemes={
        "TokenAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "DRF Token format: Token <your_token_key>"
        }
    }
)
# Middleware
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Глобальные обработчики ошибок (единый формат ответов)
register_exception_handlers(app)

# Регистрация роутеров (версионирование API v1)
app.include_router(api_router, prefix="/api/v1")

# Базовый ping для быстрой проверки доступности (вне версионирования)
@app.get("/ping", tags=["System"])
async def ping():
    """Быстрая проверка доступности сервиса."""
    return {"status": "ok"}