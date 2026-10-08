from app.core.config import settings
from app.services.http_client import ServiceClient


class DjangoClient(ServiceClient):
    """Async интеграция FastAPI с Django"""

    def __init__(self) -> None:
        super().__init__(
            name="Django",
            base_url=settings.DJANGO_API_URL,
            timeout=settings.DJANGO_API_TIMEOUT,
            retries=settings.DJANGO_API_RETRIES,
            backoff_base=settings.DJANGO_API_BACKOFF_BASE,
        )
