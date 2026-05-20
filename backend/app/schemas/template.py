from typing import Literal

from pydantic import BaseModel, Field

from app.ai.base import AIConfig


Language = Literal["zh-CN", "en-US"]
TemplateType = Literal["generic_startup", "challenge_cup", "internet_plus", "custom"]


class BusinessPlanTemplateRequest(BaseModel):
    language: Language = "zh-CN"
    template_type: TemplateType = "generic_startup"
    sections: list[str] | None = Field(default=None, min_length=1)
    ai_config: AIConfig | None = None
