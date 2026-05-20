import uuid

from sqlalchemy import String, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class BusinessPlan(Base, TimestampMixin):
    __tablename__ = "business_plans"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    provider_used: Mapped[str] = mapped_column(String(50), nullable=True)  # mock | claude | openai
    sections: Mapped[dict] = mapped_column(JSON, nullable=True)
    # sections keys: executive_summary, problem, solution, target_market,
    #                business_model, competitive_analysis, financial_forecast,
    #                risks, funding_need, implementation_plan

    project: Mapped["Project"] = relationship("Project", back_populates="business_plans")
