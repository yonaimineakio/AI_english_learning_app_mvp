"""make sessions.scenario_id nullable

Revision ID: h10000000002
Revises: h10000000001
Create Date: 2026-02-01 10:00:00.000000

This migration ensures that scenario_id in sessions table is nullable,
allowing sessions to be created with only custom_scenario_id.
If h10000000001 already ran without this change, this migration will apply it.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "h10000000002"
down_revision: Union[str, None] = "h10000000001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Make scenario_id nullable for custom scenario support."""
    bind = op.get_bind()
    inspector = inspect(bind)
    dialect_name = bind.dialect.name

    if dialect_name == "postgresql":
        # Check if column is already nullable
        columns = {col["name"]: col for col in inspector.get_columns("sessions")}
        scenario_col = columns.get("scenario_id")
        
        if scenario_col and not scenario_col.get("nullable", True):
            # Column exists and is NOT NULL, make it nullable
            op.alter_column(
                "sessions",
                "scenario_id",
                existing_type=sa.Integer(),
                nullable=True,
            )
    # SQLite: skip as it doesn't support ALTER COLUMN


def downgrade() -> None:
    """Revert scenario_id to NOT NULL."""
    bind = op.get_bind()
    dialect_name = bind.dialect.name

    if dialect_name == "postgresql":
        op.alter_column(
            "sessions",
            "scenario_id",
            existing_type=sa.Integer(),
            nullable=False,
        )
