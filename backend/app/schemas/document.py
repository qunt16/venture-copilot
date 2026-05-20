from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class DocumentBlockWrite(BaseModel):
    section_key: str
    heading: str
    block_type: str = "text"
    content: str = ""
    order_index: int = 0
    metadata_json: dict | None = None


class DocumentAutosaveRequest(BaseModel):
    blocks: list[DocumentBlockWrite] = Field(default_factory=list)


class DocumentBlockRead(DocumentBlockWrite):
    id: str
    project_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CommentCreate(BaseModel):
    body: str = Field(min_length=1)
    mention: str | None = None
    author: str = "demo_user"


class CommentResolve(BaseModel):
    status: Literal["open", "resolved"] = "resolved"


class CommentRead(BaseModel):
    id: str
    project_id: str
    section_id: str
    author: str
    body: str
    status: str
    mention: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
