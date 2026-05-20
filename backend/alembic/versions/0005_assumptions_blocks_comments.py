"""assumptions blocks comments

Revision ID: 0005_assumptions_blocks_comments
Revises: 0004
Create Date: 2026-05-19
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0005_assumptions_blocks_comments"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "project_financial_assumptions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("project_id", sa.String(), nullable=False),
        sa.Column("assumptions", sa.JSON(), nullable=False),
        sa.Column("warnings", sa.JSON(), nullable=True),
        sa.Column("confirmed", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_project_financial_assumptions_project_id", "project_financial_assumptions", ["project_id"])
    op.create_table(
        "document_blocks",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("project_id", sa.String(), nullable=False),
        sa.Column("section_key", sa.String(), nullable=False),
        sa.Column("heading", sa.String(), nullable=False),
        sa.Column("block_type", sa.String(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_document_blocks_project_id", "document_blocks", ["project_id"])
    op.create_index("ix_document_blocks_section_key", "document_blocks", ["section_key"])
    op.create_table(
        "section_comments",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("project_id", sa.String(), nullable=False),
        sa.Column("section_id", sa.String(), nullable=False),
        sa.Column("author", sa.String(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("mention", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_section_comments_project_id", "section_comments", ["project_id"])
    op.create_index("ix_section_comments_section_id", "section_comments", ["section_id"])


def downgrade() -> None:
    op.drop_index("ix_section_comments_section_id", table_name="section_comments")
    op.drop_index("ix_section_comments_project_id", table_name="section_comments")
    op.drop_table("section_comments")
    op.drop_index("ix_document_blocks_section_key", table_name="document_blocks")
    op.drop_index("ix_document_blocks_project_id", table_name="document_blocks")
    op.drop_table("document_blocks")
    op.drop_index("ix_project_financial_assumptions_project_id", table_name="project_financial_assumptions")
    op.drop_table("project_financial_assumptions")
