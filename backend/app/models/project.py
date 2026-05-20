import uuid

from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    idea_summary: Mapped[str] = mapped_column(Text, nullable=True)
    stage: Mapped[str] = mapped_column(String(50), nullable=False, default="idea")
    # stage values: idea | validation | mvp | scaling
    industry: Mapped[str | None] = mapped_column(String(120), nullable=True)
    competition_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    business_model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    planning_horizon: Mapped[int | None] = mapped_column(nullable=True)

    owner: Mapped["User"] = relationship("User", back_populates="projects")
    team_members: Mapped[list["TeamMember"]] = relationship("TeamMember", back_populates="project", lazy="select")
    finance_forecasts: Mapped[list["FinanceForecast"]] = relationship("FinanceForecast", back_populates="project", lazy="select")
    revenue_config: Mapped["RevenueConfig | None"] = relationship("RevenueConfig", back_populates="project", uselist=False, lazy="select")
    cost_config: Mapped["CostConfig | None"] = relationship("CostConfig", back_populates="project", uselist=False, lazy="select")
    forecast_outputs: Mapped[list["ForecastOutput"]] = relationship("ForecastOutput", back_populates="project", lazy="select")
    validation_reports: Mapped[list["ValidationReport"]] = relationship("ValidationReport", back_populates="project", lazy="select")
    research_reports: Mapped[list["ResearchReport"]] = relationship("ResearchReport", back_populates="project", lazy="select")
    business_plans: Mapped[list["BusinessPlan"]] = relationship("BusinessPlan", back_populates="project", lazy="select")
