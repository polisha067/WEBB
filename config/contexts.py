"""Контракты контекстов SSR-страниц: какие данные получает каждый шаблон"""

from typing import TypedDict

from django.db.models import QuerySet

from movies.models import Movie
from subscriptions.models import Subscription
from watchlist.models import Watchlist


class HomeContext(TypedDict):
    popular_movies: QuerySet[Movie]
    top_movies: QuerySet[Movie]
    new_movies: QuerySet[Movie]
    plans: QuerySet[Subscription]


class SubscriptionDetailContext(TypedDict):
    subscription: Subscription


class MovieDetailContext(TypedDict):
    movie: Movie
    in_watchlist: Watchlist | None
    auth_token: str | None


class WatchlistContext(TypedDict):
    watchlist: QuerySet[Watchlist]


class AuthFormContext(TypedDict):
    error: str
