from datetime import datetime

from pydantic import BaseModel, Field


class RevenueConfigCreate(BaseModel):
    config: dict = Field(default_factory=dict)


class RevenueConfigRead(BaseModel):
    id: str
    project_id: str
    config: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CostConfigCreate(BaseModel):
    config: dict = Field(default_factory=dict)


class CostConfigRead(BaseModel):
    id: str
    project_id: str
    config: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ForecastOutputRead(BaseModel):
    id: str
    project_id: str
    output: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ValidationReportRead(BaseModel):
    id: str
    project_id: str
    report: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
