import uuid

from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class FinanceForecast(Base, TimestampMixin):
    __tablename__ = "finance_forecasts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    inputs: Mapped[dict] = mapped_column(JSON, nullable=True)    # raw inputs from user
    monthly_rows: Mapped[list] = mapped_column(JSON, nullable=True)  # 36 month rows
    summary: Mapped[dict] = mapped_column(JSON, nullable=True)   # summary metrics

    project: Mapped["Project"] = relationship("Project", back_populates="finance_forecasts")
