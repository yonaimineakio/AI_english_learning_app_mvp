"""add_saved_phrases_table

Revision ID: a1b2c3d4e5f6
Revises: cb85777a681d
Create Date: 2025-12-22 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'cb85777a681d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create saved_phrases table
    op.create_table(
        'saved_phrases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('phrase', sa.Text(), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=False),
        sa.Column('original_input', sa.Text(), nullable=True),
        sa.Column('session_id', sa.Integer(), nullable=True),
        sa.Column('round_index', sa.Integer(), nullable=True),
        sa.Column('converted_to_review_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ),
        sa.ForeignKeyConstraint(['converted_to_review_id'], ['review_items.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_saved_phrases_id'), 'saved_phrases', ['id'], unique=False)
    op.create_index(op.f('ix_saved_phrases_user_id'), 'saved_phrases', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_saved_phrases_user_id'), table_name='saved_phrases')
    op.drop_index(op.f('ix_saved_phrases_id'), table_name='saved_phrases')
    op.drop_table('saved_phrases')

