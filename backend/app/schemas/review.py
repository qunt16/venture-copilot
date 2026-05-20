from datetime import datetime

from pydantic import BaseModel, Field


class ReviewRequest(BaseModel):
    include_export_integrity: bool = True


class ReviewScore(BaseModel):
    overall_score: int = Field(ge=0, le=100)
    dimensions: dict[str, int]
    deductions: list[dict] = []
    warnings: list[str]
    critical_conflicts: list[str]
    suggestions: list[str]


class ProjectReviewRead(ReviewScore):
    id: str
    project_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
