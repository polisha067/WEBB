from datetime import datetime
from pydantic import BaseModel, Field


class ProfileResponse(BaseModel):
    id: int = Field(..., examples=[1])
    username: str = Field(..., examples=["dev_user"])
    email: str = Field(..., examples=["dev@example.com"])

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "username": "dev_user",
                "email": "dev@example.com",
            }
        }
    }


class RecommendationItem(BaseModel):
    id: int = Field(..., examples=[102])
    title: str = Field(..., examples=["Interstellar"])
    rating: float | None = Field(default=None, examples=[8.6])


class RecommendationsResponse(BaseModel):
    recommendations: list[RecommendationItem]

    model_config = {
        "json_schema_extra": {
            "example": {
                "recommendations": [
                    {"id": 102, "title": "Interstellar", "rating": 8.6},
                    {"id": 98, "title": "Dune", "rating": 8.0},
                ]
            }
        }
    }


class ProgressReportRequest(BaseModel):
    period_days: int = Field(default=7, ge=1, le=90, examples=[7])
    include_recommendations: bool = Field(default=True, examples=[True])

    model_config = {
        "json_schema_extra": {
            "example": {
                "period_days": 7,
                "include_recommendations": True,
            }
        }
    }


class ProgressReportAcceptedResponse(BaseModel):
    status: str = Field(default="accepted", examples=["accepted"])
    request_id: str = Field(..., examples=["f1f30fd0-0dd0-4720-a1ca-f6ef216f58ca"])
    queued_at: datetime
