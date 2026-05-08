import asyncio
import logging
from typing import Any

import httpx

from app.core.config import settings
from app.core.exceptions import AppException

logger = logging.getLogger(__name__)


class DjangoClient:
    """Async интеграция FastAPI с Django"""

    def __init__(self) -> None:
        self._base_url = settings.DJANGO_API_URL.rstrip("/")
        self._timeout = settings.DJANGO_API_TIMEOUT
        self._retries = settings.DJANGO_API_RETRIES
        self._backoff_base = settings.DJANGO_API_BACKOFF_BASE

    async def request(
        self,
        method: str,
        endpoint: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> Any:
        url = f"{self._base_url}/{endpoint.lstrip('/')}"
        last_error: Exception | None = None

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            for attempt in range(self._retries + 1):
                try:
                    response = await client.request(
                        method=method,
                        url=url,
                        headers=headers,
                        params=params,
                        json=json_body,
                    )

                    if response.status_code >= 500 and attempt < self._retries:
                        await asyncio.sleep(self._backoff_base * (2**attempt))
                        continue

                    if response.status_code >= 400:
                        self._raise_mapped_error(response)

                    return response.json()
                except httpx.RequestError as exc:
                    last_error = exc
                    if attempt < self._retries:
                        await asyncio.sleep(self._backoff_base * (2**attempt))
                        continue
                    break

        logger.error("Django service unavailable", extra={"error": str(last_error)})
        raise AppException(
            code="DJANGO_API_UNAVAILABLE",
            message="Django API is unavailable",
            status_code=503,
        )

    @staticmethod
    def _raise_mapped_error(response: httpx.Response) -> None:
        try:
            data = response.json()
        except ValueError:
            data = {}

        django_detail = data.get("detail", "Django API error")
        django_code = data.get("code")
        status_map = {
            400: ("VALIDATION_ERROR", 400),
            401: ("UNAUTHORIZED", 401),
            403: ("FORBIDDEN", 403),
            404: ("NOT_FOUND", 404),
            409: ("CONFLICT", 409),
        }
        default_code, default_status = status_map.get(
            response.status_code, ("DJANGO_API_ERROR", 503)
        )

        raise AppException(
            code=django_code or default_code,
            message=str(django_detail),
            status_code=default_status,
        )
