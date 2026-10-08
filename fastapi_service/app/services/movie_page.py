import asyncio
import logging
from typing import Any, TypeVar

from app.contracts import parse_contract
from app.contracts.django import DjangoMovie
from app.contracts.ugc import UgcAverageRating, UgcComment, UgcReview
from app.core.config import settings
from app.core.exceptions import AppException
from app.schemas.pages import (
    AudienceRating,
    CommentView,
    MovieCard,
    MoviePageResponse,
    ReviewView,
)
from app.services.django_client import DjangoClient
from app.services.ugc_client import UgcClient

logger = logging.getLogger(__name__)

T = TypeVar("T")


class MoviePageService:
    """Собирает страницу фильма из Django (каталог) и UGC (рейтинг, отзывы, комментарии).

    Фильм обязателен: без него страницы нет. UGC-блоки опциональны: если UGC
    недоступен, страница отдаётся без них, а блок попадает в `unavailable`
    """

    def __init__(self, django_client: DjangoClient, ugc_client: UgcClient) -> None:
        self._django = django_client
        self._ugc = ugc_client

    async def get_movie_page(self, movie_id: int) -> MoviePageResponse:
        params = {"movie_id": movie_id}
        movie_endpoint = f"{settings.DJANGO_MOVIES_ENDPOINT.rstrip('/')}/{movie_id}/"
        movie_raw, rating_raw, reviews_raw, comments_raw = await asyncio.gather(
            self._django.request("GET", movie_endpoint),
            self._ugc.request("GET", "/ratings/average/", params=params),
            self._ugc.request("GET", "/reviews/", params=params),
            self._ugc.request("GET", "/comments/", params=params),
            return_exceptions=True,
        )
        if isinstance(movie_raw, BaseException):
            raise movie_raw
        movie = parse_contract(DjangoMovie, movie_raw, source="Django")

        unavailable: list[str] = []
        rating = self._optional(UgcAverageRating, rating_raw, "audience_rating", unavailable)
        reviews = self._optional(list[UgcReview], reviews_raw, "reviews", unavailable) or []
        comments = self._optional(list[UgcComment], comments_raw, "comments", unavailable) or []

        return MoviePageResponse(
            movie=self._movie_card(movie),
            audience_rating=self._audience_rating(rating),
            reviews=[self._review_view(r) for r in reviews],
            reviews_count=len(reviews),
            comments=[self._comment_view(c) for c in comments],
            comments_count=sum(self._count_comments(c) for c in comments),
            unavailable=unavailable,
        )

    @staticmethod
    def _optional(contract: type[T], raw: Any, block: str, unavailable: list[str]) -> T | None:
        """UGC-блок: при ошибке или нарушении контракта — деградируем, а не падаем"""
        if isinstance(raw, BaseException):
            if not isinstance(raw, AppException):
                raise raw
            logger.warning(f"Movie page block '{block}' unavailable: {raw.code}")
            unavailable.append(block)
            return None
        try:
            return parse_contract(contract, raw, source="UGC")
        except AppException as exc:
            logger.warning(f"Movie page block '{block}' unavailable: {exc.code}")
            unavailable.append(block)
            return None

    @staticmethod
    def _movie_card(movie: DjangoMovie) -> MovieCard:
        return MovieCard(
            id=movie.id,
            title=movie.title,
            description=movie.description,
            poster=movie.poster,
            release_year=movie.release_year,
            duration_label=format_duration(movie.duration),
            genres=[genre.name for genre in movie.genres],
            critics_rating=movie.rating,
        )

    @staticmethod
    def _audience_rating(rating: UgcAverageRating | None) -> AudienceRating:
        if rating is None:
            return AudienceRating(label="Рейтинг зрителей временно недоступен")
        if rating.total_votes == 0:
            return AudienceRating(votes=0, label="Пока нет оценок")
        return AudienceRating(
            average=rating.average_score,
            votes=rating.total_votes,
            label=f"{rating.average_score} / 10 (Голосов: {rating.total_votes})",
        )

    @staticmethod
    def _review_view(review: UgcReview) -> ReviewView:
        return ReviewView(
            id=review.id,
            author_id=review.user_id,
            author=author_label(review.user_id),
            rating=review.rating,
            text=review.text,
            created_at=review.created_at,
        )

    def _comment_view(self, comment: UgcComment) -> CommentView:
        return CommentView(
            id=comment.id,
            author_id=comment.user_id,
            author=author_label(comment.user_id),
            text=comment.text,
            created_at=comment.created_at,
            replies=[self._comment_view(reply) for reply in comment.replies],
        )

    def _count_comments(self, comment: UgcComment) -> int:
        return 1 + sum(self._count_comments(reply) for reply in comment.replies)


def format_duration(minutes: int | None) -> str | None:
    if not minutes:
        return None
    hours, mins = divmod(minutes, 60)
    if hours and mins:
        return f"{hours} ч {mins} мин"
    if hours:
        return f"{hours} ч"
    return f"{mins} мин"


def author_label(user_id: int) -> str:
    return f"Пользователь #{user_id}"
