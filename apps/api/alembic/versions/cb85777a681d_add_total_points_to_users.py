"""add_total_points_to_users

Revision ID: cb85777a681d
Revises: de2f65f52dd9
Create Date: 2025-12-10 17:11:17.665585

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "cb85777a681d"
down_revision = "de2f65f52dd9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add total_points column to users table
    op.add_column(
        "users",
        sa.Column("total_points", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    # Remove total_points column from users table
    op.drop_column("users", "total_points")
