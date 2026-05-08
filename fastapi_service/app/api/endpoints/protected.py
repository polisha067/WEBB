from datetime import datetime, UTC
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, Header, Query, Request

from app.api.deps import get_current_user
from app.schemas.protected import (
    ProfileResponse,
    ProgressReportAcceptedResponse,
    ProgressReportRequest,
    RecommendationItem,
    RecommendationsResponse,
)
from app.services.django_client import DjangoClient
from app.services.protected import ProtectedService
from app.tasks.notifications import send_progress_report

router = APIRouter()


def _protected_service() -> ProtectedService:
    return ProtectedService(DjangoClient())


@router.get(
    "/profile",
    response_model=ProfileResponse,
    summary="Get current profile",
)
async def profile(
    current_user: dict = Depends(get_current_user),
    authorization: str = Header(..., alias="Authorization"),
    service: ProtectedService = Depends(_protected_service),
) -> ProfileResponse:

    user_profile = await service.get_profile(authorization=authorization)
    return ProfileResponse(
        id=user_profile.get("id", current_user.get("id")),
        username=user_profile.get("username", current_user.get("username", "")),
        email=user_profile.get("email", current_user.get("email", "")),
    )


@router.get(
    "/recommendations",
    response_model=RecommendationsResponse,
    summary="Get async recommendations",
)
async def recommendations(
    _: dict = Depends(get_current_user),
    authorization: str = Header(..., alias="Authorization"),
    limit: int = Query(default=5, ge=1, le=20),
    service: ProtectedService = Depends(_protected_service),
) -> RecommendationsResponse:

    data = await service.get_recommendations(authorization=authorization, limit=limit)
    items = [RecommendationItem(**item) for item in data if item.get("id") is not None]
    return RecommendationsResponse(recommendations=items)


@router.post(
    "/progress/report",
    response_model=ProgressReportAcceptedResponse,
    status_code=202,
    summary="Queue progress report generation",
)
async def queue_progress_report(
    body: ProgressReportRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    current_user: dict = Depends(get_current_user),
) -> ProgressReportAcceptedResponse:

    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    background_tasks.add_task(
        send_progress_report,
        request_id=request_id,
        user_id=int(current_user.get("id", 0)),
        period_days=body.period_days,
        include_recommendations=body.include_recommendations,
    )
    return ProgressReportAcceptedResponse(
        status="accepted",
        request_id=request_id,
        queued_at=datetime.now(UTC),
    )
