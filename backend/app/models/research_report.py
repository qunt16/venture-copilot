import uuid

from sqlalchemy import String, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class ResearchReport(Base, TimestampMixin):
    __tablename__ = "research_reports"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    provider_used: Mapped[str] = mapped_column(String(50), nullable=True)
    summary: Mapped[str] = mapped_column(Text, nullable=True)
    market_size: Mapped[str] = mapped_column(Text, nullable=True)
    industry_trends: Mapped[list] = mapped_column(JSON, nullable=True)
    competitors: Mapped[list] = mapped_column(JSON, nullable=True)
    risks: Mapped[list] = mapped_column(JSON, nullable=True)
    opportunities: Mapped[list] = mapped_column(JSON, nullable=True)
    citations: Mapped[list] = mapped_column(JSON, nullable=True)
    # citation format: [{title, source, url, source_type}]

    project: Mapped["Project"] = relationship("Project", back_populates="research_reports")
