from app.core.config import settings
from app.services.http_client import ServiceClient


class UgcClient(ServiceClient):
    """Async интеграция FastAPI с UGC-сервисом (отзывы, комментарии, рейтинги)"""

    def __init__(self) -> None:
        super().__init__(
            name="UGC",
            base_url=settings.UGC_API_URL,
            timeout=settings.UGC_API_TIMEOUT,
            retries=settings.UGC_API_RETRIES,
            backoff_base=settings.DJANGO_API_BACKOFF_BASE,
        )
