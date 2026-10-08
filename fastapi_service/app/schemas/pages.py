"""Контракты BFF -> фронт: данные уже собраны и подготовлены под конкретную страницу"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class MovieCard(BaseModel):
    id: int = Field(..., examples=[1])
    title: str = Field(..., examples=["Interstellar"])
    description: str = ""
    poster: str | None = None
    release_year: int | None = Field(default=None, examples=[2014])
    duration_label: str | None = Field(default=None, examples=["2 ч 49 мин"])
    genres: list[str] = Field(default_factory=list, examples=[["Фантастика", "Драма"]])
    critics_rating: float | None = Field(default=None, examples=[8.6])


class AudienceRating(BaseModel):
    average: float | None = Field(default=None, examples=[8.4])
    votes: int = Field(default=0, examples=[12])
    label: str = Field(..., examples=["8.4 / 10 (Голосов: 12)"])


class ReviewView(BaseModel):
    id: int
    author_id: int
    author: str = Field(..., examples=["Пользователь #5"])
    rating: int = Field(..., examples=[9])
    text: str
    created_at: datetime | None = None


class CommentView(BaseModel):
    id: int
    author_id: int
    author: str = Field(..., examples=["Пользователь #5"])
    text: str
    created_at: datetime | None = None
    replies: list[CommentView] = Field(default_factory=list)


class MoviePageResponse(BaseModel):
    """Всё, что нужно странице фильма, одним запросом"""
    movie: MovieCard
    audience_rating: AudienceRating
    reviews: list[ReviewView]
    reviews_count: int
    comments: list[CommentView]
    comments_count: int
    unavailable: list[str] = Field(
        default_factory=list,
        description="Блоки, которые не удалось загрузить (страница отдаётся частично)",
        examples=[["reviews"]],
    )
