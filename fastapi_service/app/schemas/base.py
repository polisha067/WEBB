from pydantic import BaseModel
from typing import Optional, Any, Dict
from datetime import datetime

class BaseResponse(BaseModel):
    """Базовая модель ответа"""
    success: bool = True
    message: Optional[str] = None

class ErrorResponse(BaseModel):
    """Модель ошибки"""
    detail: Dict[str, Any]

class TimestampMixin(BaseModel):
    """Mixin для created_at/updated_at"""
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True