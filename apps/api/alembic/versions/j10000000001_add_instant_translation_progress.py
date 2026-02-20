"""add user_instant_translation_progress table

Revision ID: j10000000001
Revises: i10000000001
Create Date: 2026-02-20 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "j10000000001"
down_revision: Union[str, None] = "i10000000001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_instant_translation_progress",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("shadowing_sentence_id", sa.Integer(), nullable=False),
        sa.Column("attempt_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("best_score", sa.Integer(), nullable=True),
        sa.Column("last_practiced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_completed", sa.Boolean(), server_default="0", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["shadowing_sentence_id"], ["shadowing_sentences.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "shadowing_sentence_id",
            name="uq_instant_translation_user_sentence",
        ),
    )
    op.create_index(
        op.f("ix_user_instant_translation_progress_id"),
        "user_instant_translation_progress",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_instant_translation_progress_user_id"),
        "user_instant_translation_progress",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_user_instant_translation_progress_user_id"),
        table_name="user_instant_translation_progress",
    )
    op.drop_index(
        op.f("ix_user_instant_translation_progress_id"),
        table_name="user_instant_translation_progress",
    )
    op.drop_table("user_instant_translation_progress")
