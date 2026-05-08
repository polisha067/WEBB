import json
import logging
import sys
from contextlib import asynccontextmanager

from sqlalchemy import text
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.database import engine
from app.middleware.request_id import RequestIDMiddleware
from app.api import api_router


# Простой JSON Formatter 
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
            log_data["duration_ms"] = record.duration_ms
            log_data["url"] = record.url
            log_data["method"] = record.method
            log_data["status_code"] = record.status_code
            
        if record.exc_info:
            log_data["error"] = self.formatException(record.exc_info)
            
        return json.dumps(log_data, ensure_ascii=False)


handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JSONFormatter())
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    handlers=[handler],
    force=True,
)
logger = logging.getLogger(__name__)


# Lifespan 
@asynccontextmanager
async def lifespan(app: FastAPI):
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


# OpenAPI tags 
tags_metadata = [
    {"name": "Auth", "description": "JWT регистрация / логин / refresh"},
    {"name": "Protected", "description": "Защищённые эндпоинты (требуют токен)"},
    {"name": "System", "description": "Health / Readiness checks"},
]

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Core FastAPI service (Sprint 3)",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=tags_metadata,
)

@app.middleware("http")
async def add_security_headers(request, call_next):
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

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
    return {"status": "ok"}