from datetime import datetime, UTC
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, Query, Request

from app.api.deps import get_current_user_jwt, get_protected_service
from app.schemas.auth import CurrentUser
from app.schemas.protected import (
    ProfileResponse,
    ProgressReportAcceptedResponse,
    ProgressReportRequest,
    RecommendationsResponse,
)
from app.services.protected import ProtectedService
from app.tasks.notifications import send_progress_report

router = APIRouter()


@router.get(
    "/profile",
    response_model=ProfileResponse,
    summary="Get current profile",
)
async def profile(
    current_user: CurrentUser = Depends(get_current_user_jwt),
    service: ProtectedService = Depends(get_protected_service),
) -> ProfileResponse:
    return await service.get_profile(authorization=current_user.django_authorization)


@router.get(
    "/recommendations",
    response_model=RecommendationsResponse,
    summary="Get async recommendations",
)
async def recommendations(
    current_user: CurrentUser = Depends(get_current_user_jwt),
    limit: int = Query(default=5, ge=1, le=20),
    service: ProtectedService = Depends(get_protected_service),
) -> RecommendationsResponse:
    return await service.get_recommendations(authorization=current_user.django_authorization, limit=limit)


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
    current_user: CurrentUser = Depends(get_current_user_jwt),
) -> ProgressReportAcceptedResponse:

    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    background_tasks.add_task(
        send_progress_report,
        request_id=request_id,
        user_id=current_user.id,
        period_days=body.period_days,
        include_recommendations=body.include_recommendations,
    )
    return ProgressReportAcceptedResponse(
        status="accepted",
        request_id=request_id,
        queued_at=datetime.now(UTC),
    )
