from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from app.ai.base import AIConfig
from app.research.base import ResearchConfig


SourceType = Literal["government", "institution", "company", "report", "news"]


class ResearchReportRequest(BaseModel):
    ai_config: AIConfig | None = None
    research_config: ResearchConfig | None = None


class Citation(BaseModel):
    title: str
    source: str
    url: str
    source_type: SourceType
    snippet: str | None = None


class ResearchReportRead(BaseModel):
    id: str
    project_id: str
    provider_used: str
    summary: str
    market_size: str
    industry_trends: list[str]
    competitors: list[str]
    risks: list[str]
    opportunities: list[str]
    citations: list[Citation]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
