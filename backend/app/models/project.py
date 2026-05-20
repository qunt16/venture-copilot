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

    owner: Mapped["User"] = relationship("User", back_populates="projects")
    team_members: Mapped[list["TeamMember"]] = relationship("TeamMember", back_populates="project", lazy="select")
    finance_forecasts: Mapped[list["FinanceForecast"]] = relationship("FinanceForecast", back_populates="project", lazy="select")
    research_reports: Mapped[list["ResearchReport"]] = relationship("ResearchReport", back_populates="project", lazy="select")
    business_plans: Mapped[list["BusinessPlan"]] = relationship("BusinessPlan", back_populates="project", lazy="select")
