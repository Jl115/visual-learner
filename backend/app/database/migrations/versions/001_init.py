"""Initial migration: create all tables.

Revision ID: 001_init
Revises: 
Create Date: 2026-04-26

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001_init"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("path", sa.String(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )
    op.create_table(
        "nodes",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "doc_id", sa.Integer(), sa.ForeignKey("documents.id"), nullable=False
        ),
        sa.Column("label", sa.String(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("position_x", sa.Float(), nullable=True),
        sa.Column("position_y", sa.Float(), nullable=True),
        sa.Column("weight", sa.Float(), nullable=True),
    )
    op.create_table(
        "edges",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "source_node_id", sa.Integer(), sa.ForeignKey("nodes.id"), nullable=False
        ),
        sa.Column(
            "target_node_id", sa.Integer(), sa.ForeignKey("nodes.id"), nullable=False
        ),
        sa.Column(
            "doc_id", sa.Integer(), sa.ForeignKey("documents.id"), nullable=False
        ),
    )
    op.create_table(
        "quizzes",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "doc_id", sa.Integer(), sa.ForeignKey("documents.id"), nullable=False
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )
    op.create_table(
        "quiz_questions",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("quiz_id", sa.Integer(), sa.ForeignKey("quizzes.id"), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("options_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("correct_index", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_table("quiz_questions")
    op.drop_table("quizzes")
    op.drop_table("edges")
    op.drop_table("nodes")
    op.drop_table("documents")
