"""create_shadowing_tables

Revision ID: g10000000001
Revises: ef1a2b3c4d5e
Create Date: 2026-01-25 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "g10000000001"
down_revision = "f20000000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # シャドーイング文テーブル
    op.create_table(
        "shadowing_sentences",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("scenario_id", sa.Integer(), nullable=False),
        sa.Column("key_phrase", sa.String(length=255), nullable=False),
        sa.Column("sentence_en", sa.Text(), nullable=False),
        sa.Column("sentence_ja", sa.Text(), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column(
            "difficulty",
            sa.Enum("beginner", "intermediate", "advanced", name="difficulty_level_enum", create_type=False),
            nullable=False,
        ),
        sa.Column("audio_url", sa.String(length=512), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["scenario_id"], ["scenarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "scenario_id",
            "order_index",
            name="uq_shadowing_sentences_scenario_order",
        ),
    )
    op.create_index(
        op.f("ix_shadowing_sentences_id"), "shadowing_sentences", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_shadowing_sentences_scenario_id"),
        "shadowing_sentences",
        ["scenario_id"],
        unique=False,
    )

    # ユーザーシャドーイング進捗テーブル
    op.create_table(
        "user_shadowing_progress",
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
            name="uq_user_shadowing_progress_user_sentence",
        ),
    )
    op.create_index(
        op.f("ix_user_shadowing_progress_id"),
        "user_shadowing_progress",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_shadowing_progress_user_id"),
        "user_shadowing_progress",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_user_shadowing_progress_user_id"),
        table_name="user_shadowing_progress",
    )
    op.drop_index(
        op.f("ix_user_shadowing_progress_id"), table_name="user_shadowing_progress"
    )
    op.drop_table("user_shadowing_progress")

    op.drop_index(
        op.f("ix_shadowing_sentences_scenario_id"), table_name="shadowing_sentences"
    )
    op.drop_index(op.f("ix_shadowing_sentences_id"), table_name="shadowing_sentences")
    op.drop_table("shadowing_sentences")
