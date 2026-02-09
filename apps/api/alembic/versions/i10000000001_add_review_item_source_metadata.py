"""add source metadata columns to review_items

Revision ID: i10000000001
Revises: h10000000002
Create Date: 2026-02-08 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "i10000000001"
down_revision: Union[str, None] = "h10000000002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_cols = {col["name"] for col in inspector.get_columns("review_items")}

    if "source_session_id" not in existing_cols:
        op.add_column(
            "review_items",
            sa.Column("source_session_id", sa.Integer(), nullable=True),
        )
    if "source_round_index" not in existing_cols:
        op.add_column(
            "review_items",
            sa.Column("source_round_index", sa.Integer(), nullable=True),
        )
    if "selection_reason" not in existing_cols:
        op.add_column(
            "review_items",
            sa.Column("selection_reason", sa.String(length=255), nullable=True),
        )
    if "selection_score" not in existing_cols:
        op.add_column(
            "review_items",
            sa.Column("selection_score", sa.Integer(), nullable=True),
        )

    if bind.dialect.name != "sqlite":
        op.create_foreign_key(
            "fk_review_items_source_session_id",
            "review_items",
            "sessions",
            ["source_session_id"],
            ["id"],
            ondelete="SET NULL",
        )
    existing_indexes = {ix["name"] for ix in inspector.get_indexes("review_items")}
    if "ix_review_items_source_session_id" not in existing_indexes:
        op.create_index(
            "ix_review_items_source_session_id",
            "review_items",
            ["source_session_id"],
            unique=False,
        )
    if "ix_review_items_user_session" not in existing_indexes:
        op.create_index(
            "ix_review_items_user_session",
            "review_items",
            ["user_id", "source_session_id"],
            unique=False,
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "sqlite":
        op.drop_constraint(
            "fk_review_items_source_session_id",
            "review_items",
            type_="foreignkey",
        )

    op.drop_index("ix_review_items_user_session", table_name="review_items")
    op.drop_index("ix_review_items_source_session_id", table_name="review_items")

    op.drop_column("review_items", "selection_score")
    op.drop_column("review_items", "selection_reason")
    op.drop_column("review_items", "source_round_index")
    op.drop_column("review_items", "source_session_id")
