from pydantic import BaseModel, Field
from datetime import datetime

class RatingBase(BaseModel):
    """Базовая схема рейтинга с валидацией оценки"""
    movie_id: int = Field(..., description="ID фильма")
    score: int = Field(..., ge=1, le=10, description="Оценка должна быть от 1 до 10")

class RatingCreate(RatingBase):
    """Схема для POST-запроса (пользователь передает только фильм и оценку)"""
    pass

class RatingResponse(RatingBase):
    """Схема для ответа API (возвращаем полные данные)"""
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class AverageRatingResponse(BaseModel):
    """Схема для возврата среднего рейтинга фильма"""
    movie_id: int
    average_score: float
    total_votes: int