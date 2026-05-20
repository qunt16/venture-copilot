from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from app.ai.base import AIConfig


class FrameworkAnalysisRequest(BaseModel):
    language: Literal["zh-CN", "en-US"] = "zh-CN"
    frameworks: list[str] | None = None
    ai_config: AIConfig | None = None


class FrameworkAnalysisRead(BaseModel):
    id: str
    project_id: str
    language: str
    frameworks: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
