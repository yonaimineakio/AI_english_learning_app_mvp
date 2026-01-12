"""migrate_user_id_to_uuid

Revision ID: f20000000001
Revises: ef1a2b3c4d5e
Create Date: 2026-01-12 00:00:00.000000

This migration converts users.id from Integer to UUID (String(36)).
It also updates all foreign key references in related tables.

Steps:
1. Add new UUID column to users table
2. Generate UUIDs for existing users
3. Add new UUID-based user_id columns to related tables
4. Copy FK references using the mapping
5. Drop old columns and rename new ones
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
import uuid


# revision identifiers, used by Alembic.
revision = "f20000000001"
down_revision = "ef1a2b3c4d5e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    dialect = conn.dialect.name  # 'sqlite' or 'mysql'
    
    # Step 1: Add new UUID column to users (temporary name)
    op.add_column("users", sa.Column("uuid_id", sa.String(36), nullable=True))
    
    # Step 2: Generate UUIDs for existing users
    users = conn.execute(text("SELECT id FROM users")).fetchall()
    for (old_id,) in users:
        new_uuid = str(uuid.uuid4())
        conn.execute(
            text("UPDATE users SET uuid_id = :new_uuid WHERE id = :old_id"),
            {"new_uuid": new_uuid, "old_id": old_id}
        )
    
    # Step 3: Add new UUID-based user_id columns to related tables
    op.add_column("sessions", sa.Column("new_user_id", sa.String(36), nullable=True))
    op.add_column("review_items", sa.Column("new_user_id", sa.String(36), nullable=True))
    op.add_column("saved_phrases", sa.Column("new_user_id", sa.String(36), nullable=True))
    
    # Step 4: Copy FK references using the mapping (old_id -> uuid_id)
    conn.execute(text("""
        UPDATE sessions 
        SET new_user_id = (SELECT uuid_id FROM users WHERE users.id = sessions.user_id)
    """))
    conn.execute(text("""
        UPDATE review_items 
        SET new_user_id = (SELECT uuid_id FROM users WHERE users.id = review_items.user_id)
    """))
    conn.execute(text("""
        UPDATE saved_phrases 
        SET new_user_id = (SELECT uuid_id FROM users WHERE users.id = saved_phrases.user_id)
    """))
    
    if dialect == "sqlite":
        # SQLite requires table recreation for column changes
        _upgrade_sqlite(conn)
    else:
        # MySQL can do ALTER TABLE operations
        _upgrade_mysql(conn)


def _upgrade_sqlite(conn) -> None:
    """SQLite-specific upgrade using table recreation."""
    
    # For SQLite, we need to recreate tables with new schema
    # This is a simplified approach - in production, consider using batch_alter_table
    
    # Recreate users table
    conn.execute(text("""
        CREATE TABLE users_new (
            id VARCHAR(36) PRIMARY KEY,
            sub VARCHAR(255) NOT NULL UNIQUE,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME,
            placement_level VARCHAR(20),
            placement_score INTEGER,
            placement_completed_at DATETIME,
            current_streak INTEGER DEFAULT 0,
            longest_streak INTEGER DEFAULT 0,
            last_activity_date DATE,
            total_points INTEGER DEFAULT 0,
            is_pro BOOLEAN NOT NULL DEFAULT 0
        )
    """))
    
    conn.execute(text("""
        INSERT INTO users_new (id, sub, name, email, created_at, updated_at, 
                               placement_level, placement_score, placement_completed_at,
                               current_streak, longest_streak, last_activity_date, 
                               total_points, is_pro)
        SELECT uuid_id, sub, name, email, created_at, updated_at,
               placement_level, placement_score, placement_completed_at,
               current_streak, longest_streak, last_activity_date,
               total_points, is_pro
        FROM users
    """))
    
    conn.execute(text("DROP TABLE users"))
    conn.execute(text("ALTER TABLE users_new RENAME TO users"))
    
    # Create indexes for users
    conn.execute(text("CREATE INDEX ix_users_id ON users (id)"))
    conn.execute(text("CREATE UNIQUE INDEX ix_users_sub ON users (sub)"))
    conn.execute(text("CREATE UNIQUE INDEX ix_users_email ON users (email)"))
    
    # Recreate sessions table
    conn.execute(text("""
        CREATE TABLE sessions_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id VARCHAR(36) NOT NULL REFERENCES users(id),
            scenario_id INTEGER NOT NULL REFERENCES scenarios(id),
            round_target INTEGER NOT NULL,
            completed_rounds INTEGER DEFAULT 0,
            difficulty VARCHAR(20) NOT NULL,
            mode VARCHAR(20) NOT NULL,
            extension_count INTEGER DEFAULT 0,
            started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            ended_at DATETIME
        )
    """))
    
    conn.execute(text("""
        INSERT INTO sessions_new (id, user_id, scenario_id, round_target, completed_rounds,
                                  difficulty, mode, extension_count, started_at, ended_at)
        SELECT id, new_user_id, scenario_id, round_target, completed_rounds,
               difficulty, mode, extension_count, started_at, ended_at
        FROM sessions
    """))
    
    conn.execute(text("DROP TABLE sessions"))
    conn.execute(text("ALTER TABLE sessions_new RENAME TO sessions"))
    conn.execute(text("CREATE INDEX ix_sessions_id ON sessions (id)"))
    
    # Recreate review_items table
    conn.execute(text("""
        CREATE TABLE review_items_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id VARCHAR(36) NOT NULL REFERENCES users(id),
            phrase TEXT NOT NULL,
            explanation TEXT NOT NULL,
            due_at DATETIME NOT NULL,
            is_completed BOOLEAN DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            completed_at DATETIME
        )
    """))
    
    conn.execute(text("""
        INSERT INTO review_items_new (id, user_id, phrase, explanation, due_at, 
                                      is_completed, created_at, completed_at)
        SELECT id, new_user_id, phrase, explanation, due_at,
               is_completed, created_at, completed_at
        FROM review_items
    """))
    
    conn.execute(text("DROP TABLE review_items"))
    conn.execute(text("ALTER TABLE review_items_new RENAME TO review_items"))
    conn.execute(text("CREATE INDEX ix_review_items_id ON review_items (id)"))
    
    # Recreate saved_phrases table
    conn.execute(text("""
        CREATE TABLE saved_phrases_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id VARCHAR(36) NOT NULL REFERENCES users(id),
            phrase TEXT NOT NULL,
            explanation TEXT NOT NULL,
            original_input TEXT,
            session_id INTEGER REFERENCES sessions(id),
            round_index INTEGER,
            converted_to_review_id INTEGER REFERENCES review_items(id),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """))
    
    conn.execute(text("""
        INSERT INTO saved_phrases_new (id, user_id, phrase, explanation, original_input,
                                       session_id, round_index, converted_to_review_id, created_at)
        SELECT id, new_user_id, phrase, explanation, original_input,
               session_id, round_index, converted_to_review_id, created_at
        FROM saved_phrases
    """))
    
    conn.execute(text("DROP TABLE saved_phrases"))
    conn.execute(text("ALTER TABLE saved_phrases_new RENAME TO saved_phrases"))
    conn.execute(text("CREATE INDEX ix_saved_phrases_id ON saved_phrases (id)"))


def _drop_all_fk_constraints_for_column(conn, table_name: str, column_name: str) -> None:
    """Drop all foreign key constraints that reference a specific column in MySQL."""
    # Query to find all FK constraints on this column
    result = conn.execute(text("""
        SELECT CONSTRAINT_NAME 
        FROM information_schema.KEY_COLUMN_USAGE 
        WHERE TABLE_SCHEMA = DATABASE() 
          AND TABLE_NAME = :table_name 
          AND COLUMN_NAME = :column_name 
          AND REFERENCED_TABLE_NAME IS NOT NULL
    """), {"table_name": table_name, "column_name": column_name})
    
    for row in result:
        constraint_name = row[0]
        try:
            conn.execute(text(f"ALTER TABLE {table_name} DROP FOREIGN KEY {constraint_name}"))
            print(f"Dropped FK constraint: {table_name}.{constraint_name}")
        except Exception as e:
            print(f"Warning: Failed to drop FK {constraint_name}: {e}")


def _upgrade_mysql(conn) -> None:
    """MySQL-specific upgrade using ALTER TABLE."""
    
    # Drop all foreign key constraints on user_id columns
    _drop_all_fk_constraints_for_column(conn, "sessions", "user_id")
    _drop_all_fk_constraints_for_column(conn, "review_items", "user_id")
    _drop_all_fk_constraints_for_column(conn, "saved_phrases", "user_id")
    
    # Drop old user_id columns and rename new ones
    conn.execute(text("ALTER TABLE sessions DROP COLUMN user_id"))
    conn.execute(text("ALTER TABLE sessions CHANGE new_user_id user_id VARCHAR(36) NOT NULL"))
    
    conn.execute(text("ALTER TABLE review_items DROP COLUMN user_id"))
    conn.execute(text("ALTER TABLE review_items CHANGE new_user_id user_id VARCHAR(36) NOT NULL"))
    
    conn.execute(text("ALTER TABLE saved_phrases DROP COLUMN user_id"))
    conn.execute(text("ALTER TABLE saved_phrases CHANGE new_user_id user_id VARCHAR(36) NOT NULL"))
    
    # Modify users table: drop old id, rename uuid_id to id
    # First remove auto_increment and primary key
    conn.execute(text("ALTER TABLE users DROP PRIMARY KEY"))
    conn.execute(text("ALTER TABLE users DROP COLUMN id"))
    conn.execute(text("ALTER TABLE users CHANGE uuid_id id VARCHAR(36) NOT NULL"))
    conn.execute(text("ALTER TABLE users ADD PRIMARY KEY (id)"))
    
    # Add foreign key constraints back
    conn.execute(text("""
        ALTER TABLE sessions 
        ADD CONSTRAINT sessions_user_id_fk FOREIGN KEY (user_id) REFERENCES users(id)
    """))
    conn.execute(text("""
        ALTER TABLE review_items 
        ADD CONSTRAINT review_items_user_id_fk FOREIGN KEY (user_id) REFERENCES users(id)
    """))
    conn.execute(text("""
        ALTER TABLE saved_phrases 
        ADD CONSTRAINT saved_phrases_user_id_fk FOREIGN KEY (user_id) REFERENCES users(id)
    """))


def downgrade() -> None:
    """Downgrade is complex and risky - not recommended for production."""
    raise NotImplementedError(
        "Downgrade from UUID to Integer ID is not supported. "
        "Please restore from backup if needed."
    )

