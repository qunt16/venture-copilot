from datetime import datetime

from pydantic import BaseModel


class BusinessPlanSection(BaseModel):
    key: str
    heading: str
    content: str


class BusinessPlanRead(BaseModel):
    id: str
    project_id: str
    provider_used: str | None
    language: str
    template_type: str
    selected_sections: list[str]
    sections: list[BusinessPlanSection]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
