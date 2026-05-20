from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    idea_summary: Optional[str] = None
    stage: Optional[str] = "idea"


class ProjectRead(BaseModel):
    id: str
    user_id: str
    title: str
    idea_summary: Optional[str]
    stage: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectListItem(BaseModel):
    id: str
    title: str
    stage: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}