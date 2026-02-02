"""create custom_scenarios table

Revision ID: h10000000001
Revises: g10000000001
Create Date: 2026-02-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "h10000000001"
down_revision: Union[str, None] = "g10000000001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create custom_scenarios table
    op.create_table(
        "custom_scenarios",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("user_role", sa.Text(), nullable=False),
        sa.Column("ai_role", sa.Text(), nullable=False),
        sa.Column("difficulty", sa.String(20), nullable=False, server_default="intermediate"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_custom_scenarios_id"), "custom_scenarios", ["id"], unique=False)
    op.create_index(op.f("ix_custom_scenarios_user_id"), "custom_scenarios", ["user_id"], unique=False)

    # Add custom_scenario_id column to sessions table
    op.add_column(
        "sessions",
        sa.Column("custom_scenario_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_sessions_custom_scenario_id",
        "sessions",
        "custom_scenarios",
        ["custom_scenario_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # Make scenario_id nullable (for custom scenarios)
    # PostgreSQL: ALTER COLUMN scenario_id DROP NOT NULL
    # This allows sessions to be created with only custom_scenario_id
    from sqlalchemy import inspect
    bind = op.get_bind()
    inspector = inspect(bind)
    dialect_name = bind.dialect.name
    
    if dialect_name == "postgresql":
        op.alter_column(
            "sessions",
            "scenario_id",
            existing_type=sa.Integer(),
            nullable=True,
        )
    # Note: SQLite doesn't support ALTER COLUMN, skip for development


def downgrade() -> None:
    # Remove foreign key and column from sessions
    op.drop_constraint("fk_sessions_custom_scenario_id", "sessions", type_="foreignkey")
    op.drop_column("sessions", "custom_scenario_id")

    # Drop custom_scenarios table
    op.drop_index(op.f("ix_custom_scenarios_user_id"), table_name="custom_scenarios")
    op.drop_index(op.f("ix_custom_scenarios_id"), table_name="custom_scenarios")
    op.drop_table("custom_scenarios")
