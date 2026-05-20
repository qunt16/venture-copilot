from typing import Literal

from pydantic import BaseModel, Field


PolishMode = Literal[
    "polish",
    "expand",
    "shorten",
    "challenge_cup_style",
    "internet_plus_style",
    "fix_language_mixing",
]


class SectionPolishRequest(BaseModel):
    language: Literal["zh-CN", "en-US"] = "zh-CN"
    section_key: str
    text: str = Field(min_length=1)
    mode: PolishMode = "polish"


class SectionPolishResult(BaseModel):
    section_key: str
    mode: PolishMode
    original_text: str
    revised_text: str
    warnings: list[str] = []
