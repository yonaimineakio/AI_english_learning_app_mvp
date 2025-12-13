"""add_streak_fields_to_users

Revision ID: de2f65f52dd9
Revises: 
Create Date: 2025-12-10 17:04:03.408927

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'de2f65f52dd9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add streak fields to users table
    op.add_column('users', sa.Column('current_streak', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('longest_streak', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('last_activity_date', sa.Date(), nullable=True))


def downgrade() -> None:
    # Remove streak fields from users table
    op.drop_column('users', 'last_activity_date')
    op.drop_column('users', 'longest_streak')
    op.drop_column('users', 'current_streak')
