from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    idea_summary: Optional[str] = None
    stage: Optional[str] = "idea"
    industry: Optional[str] = Field(default=None, max_length=120)
    competition_type: Optional[str] = Field(default=None, max_length=120)
    business_model: Optional[str] = Field(default=None, max_length=120)
    planning_horizon: Optional[int] = Field(default=None, ge=1, le=120)


class ProjectRead(BaseModel):
    id: str
    user_id: str
    title: str
    idea_summary: Optional[str]
    stage: str
    industry: Optional[str]
    competition_type: Optional[str]
    business_model: Optional[str]
    planning_horizon: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectListItem(BaseModel):
    id: str
    title: str
    stage: str
    industry: Optional[str] = None
    competition_type: Optional[str] = None
    business_model: Optional[str] = None
    planning_horizon: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
