import asyncio
import logging
from typing import Any

import httpx

from app.core.exceptions import AppException

logger = logging.getLogger(__name__)

# Повторять безопасно только идемпотентные запросы: повтор POST может, например,
# создать пользователя дважды, если первый запрос дошёл, а ответ потерялся
IDEMPOTENT_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "PUT", "DELETE"})


class ServiceClient:
    """Async HTTP-клиент к внутреннему сервису с retry и маппингом ошибок"""

    def __init__(
        self,
        *,
        name: str,
        base_url: str,
        timeout: float,
        retries: int,
        backoff_base: float,
    ) -> None:
        self._name = name
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._retries = retries
        self._backoff_base = backoff_base

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
        retries = self._retries if method.upper() in IDEMPOTENT_METHODS else 0

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            for attempt in range(retries + 1):
                try:
                    response = await client.request(
                        method=method,
                        url=url,
                        headers=headers,
                        params=params,
                        json=json_body,
                    )

                    if response.status_code >= 500 and attempt < retries:
                        await asyncio.sleep(self._backoff_base * (2**attempt))
                        continue

                    if response.status_code >= 400:
                        self._raise_mapped_error(response)

                    return response.json()
                except httpx.RequestError as exc:
                    last_error = exc
                    if attempt < retries:
                        await asyncio.sleep(self._backoff_base * (2**attempt))
                        continue
                    break

        logger.error(f"{self._name} service unavailable", extra={"error": str(last_error)})
        raise AppException(
            code=f"{self._name.upper()}_API_UNAVAILABLE",
            message=f"{self._name} API is unavailable",
            status_code=503,
        )

    def _raise_mapped_error(self, response: httpx.Response) -> None:
        try:
            data = response.json()
        except ValueError:
            data = {}
        if not isinstance(data, dict):
            data = {}

        detail = data.get("detail") or data.get("error") or f"{self._name} API error"
        if isinstance(detail, dict):
            detail = detail.get("message", detail)
        code = data.get("code")
        status_map = {
            400: ("VALIDATION_ERROR", 400),
            401: ("UNAUTHORIZED", 401),
            403: ("FORBIDDEN", 403),
            404: ("NOT_FOUND", 404),
            409: ("CONFLICT", 409),
        }
        default_code, default_status = status_map.get(
            response.status_code, (f"{self._name.upper()}_API_ERROR", 503)
        )

        raise AppException(
            code=code or default_code,
            message=str(detail),
            status_code=default_status,
        )
