import pytest
from fastapi import status
import respx
from httpx import ConnectError, Response

from app.core.config import settings
from app.services.movie_page import format_duration

DJANGO_BASE = settings.DJANGO_API_URL.rstrip("/")
UGC_BASE = settings.UGC_API_URL.rstrip("/")

MOVIE = {
    "id": 7,
    "title": "Interstellar",
    "description": "Space",
    "duration": 169,
    "rating": 8.6,
    "release_year": 2014,
    "genres": [{"id": 1, "name": "Фантастика", "description": "", "created_at": "2024-01-01T00:00:00Z"}],
    "poster": None,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
}

COMMENTS = [
    {
        "id": 1, "user_id": 5, "movie_id": 7, "parent_id": None, "text": "Топ", "status": "active",
        "created_at": "2024-01-02T00:00:00", "updated_at": None,
        "replies": [
            {
                "id": 2, "user_id": 6, "movie_id": 7, "parent_id": 1, "text": "Согласен", "status": "active",
                "created_at": "2024-01-03T00:00:00", "updated_at": None, "replies": [],
            }
        ],
    }
]

REVIEWS = [
    {
        "id": 10, "user_id": 5, "movie_id": 7, "rating": 9, "text": "Шедевр", "status": "active",
        "created_at": "2024-01-02T00:00:00", "updated_at": None,
    }
]


def _mock_django_movie(status_code: int = 200, json=None):
    return respx.get(f"{DJANGO_BASE}/movies/movies/7/").mock(
        return_value=Response(status_code, json=MOVIE if json is None else json)
    )


class TestMoviePage:
    """BFF: агрегированная страница фильма"""

    @pytest.mark.asyncio
    @respx.mock
    async def test_movie_page_aggregates_and_shapes(self, async_client):
        _mock_django_movie()
        respx.get(f"{UGC_BASE}/ratings/average/").mock(
            return_value=Response(200, json={"movie_id": 7, "average_score": 8.4, "total_votes": 12})
        )
        respx.get(f"{UGC_BASE}/reviews/").mock(return_value=Response(200, json=REVIEWS))
        respx.get(f"{UGC_BASE}/comments/").mock(return_value=Response(200, json=COMMENTS))

        response = await async_client.get("/api/v1/pages/movies/7")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["movie"]["duration_label"] == "2 ч 49 мин"
        assert data["movie"]["genres"] == ["Фантастика"]
        assert data["movie"]["critics_rating"] == 8.6
        assert data["audience_rating"] == {"average": 8.4, "votes": 12, "label": "8.4 / 10 (Голосов: 12)"}
        assert data["reviews_count"] == 1
        assert data["reviews"][0]["author"] == "Пользователь #5"
        assert data["comments_count"] == 2
        assert data["comments"][0]["replies"][0]["author"] == "Пользователь #6"
        assert data["unavailable"] == []

    @pytest.mark.asyncio
    @respx.mock
    async def test_movie_page_degrades_when_ugc_down(self, async_client):
        _mock_django_movie()
        respx.get(url__startswith=UGC_BASE).mock(side_effect=ConnectError("Connection refused"))

        response = await async_client.get("/api/v1/pages/movies/7")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["movie"]["title"] == "Interstellar"
        assert data["reviews"] == []
        assert data["comments"] == []
        assert data["audience_rating"]["average"] is None
        assert set(data["unavailable"]) == {"audience_rating", "reviews", "comments"}

    @pytest.mark.asyncio
    @respx.mock
    async def test_movie_page_no_votes(self, async_client):
        _mock_django_movie()
        respx.get(f"{UGC_BASE}/ratings/average/").mock(
            return_value=Response(200, json={"movie_id": 7, "average_score": 0.0, "total_votes": 0})
        )
        respx.get(f"{UGC_BASE}/reviews/").mock(return_value=Response(200, json=[]))
        respx.get(f"{UGC_BASE}/comments/").mock(return_value=Response(200, json=[]))

        response = await async_client.get("/api/v1/pages/movies/7")

        data = response.json()
        assert data["audience_rating"] == {"average": None, "votes": 0, "label": "Пока нет оценок"}

    @pytest.mark.asyncio
    @respx.mock
    async def test_movie_page_not_found(self, async_client):
        _mock_django_movie(404, {"detail": "Not found"})
        respx.get(url__startswith=UGC_BASE).mock(return_value=Response(200, json=[]))

        response = await async_client.get("/api/v1/pages/movies/7")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"]["code"] == "NOT_FOUND"

    @pytest.mark.parametrize(
        "minutes, expected",
        [(None, None), (0, None), (45, "45 мин"), (120, "2 ч"), (169, "2 ч 49 мин")],
    )
    def test_format_duration(self, minutes, expected):
        assert format_duration(minutes) == expected
