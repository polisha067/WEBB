from typing import Any

from app.core.config import settings
from app.services.django_client import DjangoClient


class ProtectedService:
    """Сервис для защищенных эндпоинтов"""

    def __init__(self, django_client: DjangoClient) -> None:
        self._django_client = django_client

    async def get_profile(self, authorization: str) -> dict[str, Any]:
        return await self._django_client.request(
            method="GET",
            endpoint=settings.DJANGO_VERIFY_ENDPOINT,
            headers={"Authorization": authorization},
        )

    async def get_recommendations(
        self, authorization: str, limit: int = 5
    ) -> list[dict[str, Any]]:
        raw_movies = await self._django_client.request(
            method="GET",
            endpoint=settings.DJANGO_RECOMMENDATIONS_ENDPOINT,
            headers={"Authorization": authorization},
        )
        if not isinstance(raw_movies, list):
            return []

        recommendations: list[dict[str, Any]] = []
        for item in raw_movies[:limit]:
            recommendations.append(
                {
                    "id": item.get("id"),
                    "title": item.get("title", "Unknown"),
                    "rating": item.get("rating"),
                }
            )
        return recommendations
