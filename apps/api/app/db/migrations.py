from __future__ import annotations

import os
from pathlib import Path

from alembic import command
from alembic.config import Config

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


def upgrade_head() -> None:
    """
    Run Alembic migrations up to head.

    Why:
    - `Base.metadata.create_all()` does NOT add missing columns to existing tables.
    - We rely on Alembic for schema evolution (e.g. users.is_pro).
    """

    # migrations.py is at .../apps/api/app/db/migrations.py
    # parents[2] => .../apps/api
    repo_api_dir = Path(__file__).resolve().parents[2]
    alembic_ini = repo_api_dir / "alembic.ini"

    if not alembic_ini.exists():
        raise RuntimeError(f"alembic.ini not found at {alembic_ini}")

    # Keep Alembic env.py behavior consistent with runtime settings.
    if settings.CLOUD_SQL_USE_CONNECTOR:
        os.environ.setdefault("CLOUD_SQL_USE_CONNECTOR", "true")
        if settings.CLOUD_SQL_CONNECTION_NAME:
            os.environ.setdefault(
                "CLOUD_SQL_CONNECTION_NAME", settings.CLOUD_SQL_CONNECTION_NAME
            )
        if settings.CLOUD_SQL_IP_TYPE:
            os.environ.setdefault("CLOUD_SQL_IP_TYPE", settings.CLOUD_SQL_IP_TYPE)
        os.environ.setdefault(
            "CLOUD_SQL_ENABLE_IAM_AUTH",
            "true" if settings.CLOUD_SQL_ENABLE_IAM_AUTH else "false",
        )
        if settings.DB_NAME:
            os.environ.setdefault("DB_NAME", settings.DB_NAME)
        if settings.DB_USER:
            os.environ.setdefault("DB_USER", settings.DB_USER)
        if settings.DB_PASSWORD:
            os.environ.setdefault("DB_PASSWORD", settings.DB_PASSWORD)
    else:
        os.environ.setdefault("CLOUD_SQL_USE_CONNECTOR", "false")
        # Alembic env.py prefers DATABASE_URL from environment.
        if settings.DATABASE_URL:
            os.environ.setdefault("DATABASE_URL", settings.DATABASE_URL)

    cfg = Config(str(alembic_ini))
    # Hard-set script location to be robust regardless of working directory.
    cfg.set_main_option("script_location", str(repo_api_dir / "alembic"))

    logger.info("Running Alembic migrations: upgrade head")
    command.upgrade(cfg, "head")
    logger.info("Alembic migrations completed")


def main() -> None:
    upgrade_head()


if __name__ == "__main__":
    main()
