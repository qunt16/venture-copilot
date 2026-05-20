"""finance mvp foundation

Revision ID: 0006_finance_mvp_foundation
Revises: 0005_assumptions_blocks_comments
Create Date: 2026-05-20
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0006_finance_mvp_foundation"
down_revision: Union[str, None] = "0005_assumptions_blocks_comments"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("projects", sa.Column("industry", sa.String(length=120), nullable=True))
    op.add_column("projects", sa.Column("competition_type", sa.String(length=120), nullable=True))
    op.add_column("projects", sa.Column("business_model", sa.String(length=120), nullable=True))
    op.add_column("projects", sa.Column("planning_horizon", sa.Integer(), nullable=True))

    op.create_table(
        "revenue_configs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("project_id", sa.String(), nullable=False),
        sa.Column("config", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id"),
    )
    op.create_index("ix_revenue_configs_project_id", "revenue_configs", ["project_id"])

    op.create_table(
        "cost_configs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("project_id", sa.String(), nullable=False),
        sa.Column("config", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id"),
    )
    op.create_index("ix_cost_configs_project_id", "cost_configs", ["project_id"])

    op.create_table(
        "forecast_outputs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("project_id", sa.String(), nullable=False),
        sa.Column("output", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_forecast_outputs_project_id", "forecast_outputs", ["project_id"])

    op.create_table(
        "validation_reports",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("project_id", sa.String(), nullable=False),
        sa.Column("report", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_validation_reports_project_id", "validation_reports", ["project_id"])


def downgrade() -> None:
    op.drop_index("ix_validation_reports_project_id", table_name="validation_reports")
    op.drop_table("validation_reports")
    op.drop_index("ix_forecast_outputs_project_id", table_name="forecast_outputs")
    op.drop_table("forecast_outputs")
    op.drop_index("ix_cost_configs_project_id", table_name="cost_configs")
    op.drop_table("cost_configs")
    op.drop_index("ix_revenue_configs_project_id", table_name="revenue_configs")
    op.drop_table("revenue_configs")

    op.drop_column("projects", "planning_horizon")
    op.drop_column("projects", "business_model")
    op.drop_column("projects", "competition_type")
    op.drop_column("projects", "industry")
