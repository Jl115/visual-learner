"""Migration: add user_node_states + quiz_attempts + scores tables.

Revision ID: 002_add_user_node_states
Revises: 001_init
Create Date: 2026-04-27
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002_add_user_node_states"
down_revision: Union[str, None] = "001_init"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- user_node_states ------------------------------------------------
    op.create_table(
        "user_node_states",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "node_id", sa.Integer(), sa.ForeignKey("nodes.id"), nullable=False
        ),
        sa.Column(
            "state",
            sa.String(),
            nullable=False,
            server_default="new",
        ),
        sa.Column("last_reviewed", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "review_count", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_user_node_states_node_id",
        "user_node_states",
        ["node_id"],
        unique=False,
    )

    # --- quiz_attempts ---------------------------------------------------
    op.create_table(
        "quiz_attempts",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "quiz_id", sa.Integer(), sa.ForeignKey("quizzes.id"), nullable=False
        ),
        sa.Column(
            "score", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "total", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("answers_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # --- scores ----------------------------------------------------------
    op.create_table(
        "scores",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "document_id",
            sa.Integer(),
            sa.ForeignKey("documents.id"),
            nullable=False,
        ),
        sa.Column(
            "quiz_id", sa.Integer(), sa.ForeignKey("quizzes.id"), nullable=False
        ),
        sa.Column(
            "correct_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "total_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # --- alter existing tables (phase-2 schema additions) ----------------
    op.add_column(
        "documents",
        sa.Column("source_path", sa.String(), nullable=True),
    )
    op.add_column(
        "documents",
        sa.Column("raw_text", sa.Text(), nullable=True),
    )
    op.add_column(
        "documents",
        sa.Column("status", sa.String(), nullable=False, server_default="pending"),
    )
    op.add_column(
        "documents",
        sa.Column("error_msg", sa.Text(), nullable=True),
    )

    op.add_column(
        "nodes",
        sa.Column("color", sa.String(), nullable=False, server_default="#4ECDC4"),
    )
    op.add_column(
        "nodes",
        sa.Column("theme_category", sa.String(), nullable=True),
    )
    op.add_column(
        "nodes",
        sa.Column("full_text", sa.Text(), nullable=True),
    )

    op.add_column(
        "edges",
        sa.Column("relation_type", sa.String(), nullable=True),
    )
    op.add_column(
        "edges",
        sa.Column("strength", sa.Float(), nullable=True),
    )

    op.add_column(
        "quizzes",
        sa.Column("node_id", sa.Integer(), sa.ForeignKey("nodes.id"), nullable=True),
    )
    op.add_column(
        "quizzes",
        sa.Column("total_questions", sa.Integer(), nullable=False, server_default="0"),
    )

    op.add_column(
        "quiz_questions",
        sa.Column("explanation", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("quiz_questions", "explanation")

    op.drop_column("quizzes", "total_questions")
    op.drop_column("quizzes", "node_id")

    op.drop_column("edges", "strength")
    op.drop_column("edges", "relation_type")

    op.drop_column("nodes", "full_text")
    op.drop_column("nodes", "theme_category")
    op.drop_column("nodes", "color")

    op.drop_column("documents", "error_msg")
    op.drop_column("documents", "status")
    op.drop_column("documents", "raw_text")
    op.drop_column("documents", "source_path")

    op.drop_table("scores")
    op.drop_table("quiz_attempts")
    op.drop_table("user_node_states")
