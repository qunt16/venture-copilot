import uuid

from sqlalchemy import ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class DocumentBlock(Base, TimestampMixin):
    __tablename__ = "document_blocks"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    section_key: Mapped[str] = mapped_column(String, nullable=False, index=True)
    heading: Mapped[str] = mapped_column(String, nullable=False)
    block_type: Mapped[str] = mapped_column(String, default="text", nullable=False)
    content: Mapped[str] = mapped_column(Text, default="", nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSON, nullable=True)

    project: Mapped["Project"] = relationship("Project")
