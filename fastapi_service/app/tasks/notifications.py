import logging
from datetime import datetime, UTC

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


async def send_progress_report(
    *,
    request_id: str,
    user_id: int,
    period_days: int,
    include_recommendations: bool,
) -> None:
    """Отправка отчета о прогрессе в настроенный вебхук"""
    payload = {
        "event": "progress_report_requested",
        "request_id": request_id,
        "user_id": user_id,
        "period_days": period_days,
        "include_recommendations": include_recommendations,
        "created_at": datetime.now(UTC).isoformat(),
    }

    webhook_url = settings.NOTIFICATION_WEBHOOK_URL
    if not webhook_url:
        logger.info("Progress report task skipped: no webhook configured", extra=payload)
        return

    try:
        async with httpx.AsyncClient(timeout=settings.DJANGO_API_TIMEOUT) as client:
            response = await client.post(webhook_url, json=payload)
            response.raise_for_status()
        logger.info("Progress report webhook sent", extra={"request_id": request_id})
    except Exception as exc:
        logger.warning(
            "Progress report task failed",
            extra={"request_id": request_id, "error": str(exc)},
        )
