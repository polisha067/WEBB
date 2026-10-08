from app.contracts import parse_contract
from app.contracts.django import DjangoMovie, DjangoPage, DjangoUser
from app.core.config import settings
from app.schemas.protected import ProfileResponse, RecommendationItem, RecommendationsResponse
from app.services.django_client import DjangoClient


class ProtectedService:
    """Сервис для защищенных эндпоинтов"""

    def __init__(self, django_client: DjangoClient) -> None:
        self._django_client = django_client

    async def get_profile(self, authorization: str) -> ProfileResponse:
        data = await self._django_client.request(
            method="GET",
            endpoint=settings.DJANGO_PROFILE_ENDPOINT,
            headers={"Authorization": authorization},
        )
        user = parse_contract(DjangoUser, data, source="Django")
        return ProfileResponse(id=user.id, username=user.username, email=user.email)

    async def get_recommendations(self, authorization: str, limit: int = 5) -> RecommendationsResponse:
        data = await self._django_client.request(
            method="GET",
            endpoint=settings.DJANGO_MOVIES_ENDPOINT,
            headers={"Authorization": authorization},
            params={"ordering": "-rating"},
        )
        page = parse_contract(DjangoPage[DjangoMovie], data, source="Django")
        return RecommendationsResponse(
            recommendations=[
                RecommendationItem(id=movie.id, title=movie.title, rating=movie.rating)
                for movie in page.results[:limit]
            ]
        )
