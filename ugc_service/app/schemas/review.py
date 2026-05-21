from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Literal


class ReviewBase(BaseModel):
    """Базовая схема отзыва с валидацией"""
    movie_id: int = Field(..., ge=1, description="ID фильма (должен быть положительным)")
    rating: int = Field(..., ge=1, le=10, description="Оценка от 1 до 10")
    text: str = Field(..., min_length=10, max_length=5000, description="Текст отзыва от 10 до 5000 символов")


class ReviewCreate(ReviewBase):
    """Схема для POST-запроса (создание отзыва)"""
    status: Optional[Literal['active', 'hidden', 'pending']] = 'pending'

    model_config = ConfigDict(extra='forbid')


class ReviewUpdate(BaseModel):
    """Схема для PATCH-запроса (обновление отзыва)"""
    rating: Optional[int] = Field(None, ge=1, le=10, description="Оценка от 1 до 10")
    text: Optional[str] = Field(None, min_length=10, max_length=5000, description="Текст отзыва от 10 до 5000 символов")

    model_config = ConfigDict(extra='forbid')


class ReviewResponse(ReviewBase):
    """Схема для ответа API (возвращаем полные данные)"""
    id: int
    user_id: int
    status: Literal['active', 'hidden', 'pending']
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ReviewListResponse(BaseModel):
    """Схема для списка отзывов"""
    items: list[ReviewResponse]
    total: int