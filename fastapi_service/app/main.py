import logging
from contextlib import asynccontextmanager
from sqlalchemy import text
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.database import engine
from app.middleware.request_id import RequestIDMiddleware
from app.api import api_router

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper()),
                    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Жизненный цикл: инициализация при старте, очистка при остановке"""
    logger.info("FastAPI service starting...")

    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")

    yield

    logger.info("FastAPI service shutting down...")
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Core FastAPI service (Sprint 3)",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    security_schemes={
        "TokenAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "DRF Token format: Token <your_token_key>"
        }
    }
)

app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
app.include_router(api_router, prefix="/api/v1")


@app.get("/ping", tags=["System"])
async def ping():
    """Базовая проверка доступности сервиса"""
    return {"status": "ok"}