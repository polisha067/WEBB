import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.middleware.request_id import RequestIDMiddleware
from app.api import api_router

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Жизненный цикл приложения: старт и остановка"""
    logger.info("FastAPI service starting...")
    yield
    logger.info("FastAPI service shutting down...")

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Core FastAPI service ",
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