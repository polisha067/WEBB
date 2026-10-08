"""Контракты ответов UGC-сервиса (Flask)"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class UgcAverageRating(BaseModel):
    """GET /api/v1/ratings/average/?movie_id="""
    movie_id: int
    average_score: float
    total_votes: int


class UgcReview(BaseModel):
    """GET /api/v1/reviews/?movie_id="""
    id: int
    user_id: int
    movie_id: int
    rating: int
    text: str
    status: str
    created_at: datetime | None = None


class UgcComment(BaseModel):
    """GET /api/v1/comments/?movie_id= (дерево с replies)"""
    id: int
    user_id: int
    movie_id: int
    parent_id: int | None = None
    text: str
    status: str
    created_at: datetime | None = None
    replies: list[UgcComment] = []
