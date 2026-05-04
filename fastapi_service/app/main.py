import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.middleware.request_id import RequestIDMiddleware

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper()), format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Жизненный цикл приложения: инициализация и graceful shutdown"""
    logger.info("FastAPI service starting...")
    # TODO: Инициализация БД, кэша, внешних клиентов
    yield
    logger.info("FastAPI service shutting down...")
    # TODO: Закрытие соединений

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Core FastAPI service (Sprint 3)",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.add_middleware(RequestIDMiddleware)
app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
register_exception_handlers(app)

@app.get("/ping", tags=["System"])
async def ping():
    """Базовая проверка доступности сервиса"""
    return {"status": "ok"}