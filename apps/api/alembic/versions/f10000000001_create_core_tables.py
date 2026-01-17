"""create_core_tables

Revision ID: f10000000001
Revises:
Create Date: 2025-12-31 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f10000000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    scenario_category_enum = sa.Enum(
        "travel",
        "business",
        "daily",
        name="scenario_category_enum",
    )
    difficulty_level_enum = sa.Enum(
        "beginner",
        "intermediate",
        "advanced",
        name="difficulty_level_enum",
    )
    session_mode_enum = sa.Enum(
        "quick",
        "standard",
        "deep",
        "custom",
        name="session_mode_enum",
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sub", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("placement_level", difficulty_level_enum, nullable=True),
        sa.Column("placement_score", sa.Integer(), nullable=True),
        sa.Column("placement_completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sub", name="uq_users_sub"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_sub"), "users", ["sub"], unique=True)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "scenarios",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", scenario_category_enum, nullable=False),
        sa.Column("difficulty", difficulty_level_enum, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_scenarios_id"), "scenarios", ["id"], unique=False)

    op.create_table(
        "sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("scenario_id", sa.Integer(), nullable=False),
        sa.Column("round_target", sa.Integer(), nullable=False),
        sa.Column("completed_rounds", sa.Integer(), server_default="0", nullable=True),
        sa.Column("difficulty", difficulty_level_enum, nullable=False),
        sa.Column("mode", session_mode_enum, nullable=False),
        sa.Column("extension_count", sa.Integer(), server_default="0", nullable=True),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["scenario_id"], ["scenarios.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sessions_id"), "sessions", ["id"], unique=False)

    op.create_table(
        "session_rounds",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("round_index", sa.Integer(), nullable=False),
        sa.Column("user_input", sa.Text(), nullable=False),
        sa.Column("ai_reply", sa.Text(), nullable=False),
        sa.Column("feedback_short", sa.String(length=120), nullable=False),
        sa.Column("improved_sentence", sa.Text(), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("score_pronunciation", sa.Integer(), nullable=True),
        sa.Column("score_grammar", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "session_id",
            "round_index",
            name="uq_session_rounds_session_id_round_index",
        ),
    )
    op.create_index(
        op.f("ix_session_rounds_id"), "session_rounds", ["id"], unique=False
    )

    op.create_table(
        "review_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("phrase", sa.Text(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_completed", sa.Boolean(), server_default="0", nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_review_items_id"), "review_items", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_review_items_id"), table_name="review_items")
    op.drop_table("review_items")

    op.drop_index(op.f("ix_session_rounds_id"), table_name="session_rounds")
    op.drop_table("session_rounds")

    op.drop_index(op.f("ix_sessions_id"), table_name="sessions")
    op.drop_table("sessions")

    op.drop_index(op.f("ix_scenarios_id"), table_name="scenarios")
    op.drop_table("scenarios")

    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_index(op.f("ix_users_sub"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")
