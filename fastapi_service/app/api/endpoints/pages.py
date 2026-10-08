from fastapi import APIRouter, Depends, Path

from app.api.deps import get_movie_page_service
from app.schemas.pages import MoviePageResponse
from app.services.movie_page import MoviePageService

router = APIRouter()


@router.get(
    "/movies/{movie_id}",
    response_model=MoviePageResponse,
    summary="Movie page data (Django + UGC)",
)
async def movie_page(
    movie_id: int = Path(..., ge=1),
    service: MoviePageService = Depends(get_movie_page_service),
) -> MoviePageResponse:
    """Данные страницы фильма одним запросом, уже подготовленные под фронт"""
    return await service.get_movie_page(movie_id)
