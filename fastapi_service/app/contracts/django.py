"""Контракты ответов Django API (см. docs/integration_contracts.md)"""

from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class DjangoUser(BaseModel):
    """GET /api/accounts/me/"""
    id: int
    username: str
    email: str = ""


class DjangoAuthResponse(BaseModel):
    """POST /api/accounts/register/ и /api/accounts/login/"""
    user: DjangoUser
    token: str


class DjangoGenre(BaseModel):
    id: int
    name: str


class DjangoMovie(BaseModel):
    """GET /api/movies/movies/{id}/"""
    id: int
    title: str
    description: str = ""
    duration: int | None = None
    rating: float | None = None
    release_year: int | None = None
    genres: list[DjangoGenre] = []
    poster: str | None = None
    created_at: datetime | None = None


class DjangoPage(BaseModel, Generic[T]):
    """Пагинированный ответ DRF (PageNumberPagination)"""
    count: int
    next: str | None = None
    previous: str | None = None
    results: list[T]
