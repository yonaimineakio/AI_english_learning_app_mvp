import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Initialized only when CLOUD_SQL_USE_CONNECTOR is enabled.
_cloud_sql_connector = None


def close_cloud_sql_connector() -> None:
    """Close Cloud SQL Python Connector if it was initialized."""
    global _cloud_sql_connector
    if _cloud_sql_connector is None:
        return
    try:
        _cloud_sql_connector.close()
    finally:
        _cloud_sql_connector = None


def _require(value: object, name: str) -> str:
    if not value:
        raise RuntimeError(f"Missing required setting for Cloud SQL Connector: {name}")
    return str(value)


# Cloud Run typically runs many instances; keep pool small by default in non-dev.
def _engine_kwargs(database_url: str) -> dict:
    kwargs: dict = {
        "pool_pre_ping": True,
        "echo": settings.DEBUG,
    }

    if database_url.startswith("sqlite"):
        # Needed for SQLite when accessed from multiple threads (dev/tests).
        kwargs["connect_args"] = {"check_same_thread": False}

    if settings.ENVIRONMENT != "development":
        kwargs["pool_size"] = int(os.getenv("DB_POOL_SIZE", "5"))
        kwargs["max_overflow"] = int(os.getenv("DB_MAX_OVERFLOW", "0"))
        kwargs["pool_timeout"] = int(os.getenv("DB_POOL_TIMEOUT", "30"))
        kwargs["pool_recycle"] = int(os.getenv("DB_POOL_RECYCLE", "1800"))

    return kwargs


def _create_cloud_sql_connector_engine():
    """
    Build SQLAlchemy engine using cloud-sql-python-connector.

    This is recommended for Cloud Run because it avoids manual SSL cert management
    and supports private/public IP and IAM DB auth.
    """
    global _cloud_sql_connector
    from google.cloud.sql.connector import Connector, IPTypes  # type: ignore

    # Ensure the driver is present (required by connector.connect).
    try:
        import pymysql  # type: ignore[import-not-found]  # noqa: F401
    except ImportError as e:  # pragma: no cover
        raise RuntimeError(
            "PyMySQL is required when CLOUD_SQL_USE_CONNECTOR=true"
        ) from e

    connection_name = _require(
        settings.CLOUD_SQL_CONNECTION_NAME, "CLOUD_SQL_CONNECTION_NAME"
    )
    db_name = _require(settings.DB_NAME, "DB_NAME")
    db_user = _require(settings.DB_USER, "DB_USER")

    ip_type_raw = (settings.CLOUD_SQL_IP_TYPE or "private").lower()
    ip_type = IPTypes.PRIVATE if ip_type_raw == "private" else IPTypes.PUBLIC

    _cloud_sql_connector = Connector()

    def getconn():
        return _cloud_sql_connector.connect(
            connection_name,
            "pymysql",
            user=db_user,
            password=settings.DB_PASSWORD,
            db=db_name,
            enable_iam_auth=settings.CLOUD_SQL_ENABLE_IAM_AUTH,
            ip_type=ip_type,
        )

    # URL is intentionally empty because driver+db params are provided by getconn().
    return create_engine(
        "mysql+pymysql://",
        creator=getconn,
        **_engine_kwargs("mysql+pymysql://"),
    )


# Create database engine
engine = (
    _create_cloud_sql_connector_engine()
    if settings.CLOUD_SQL_USE_CONNECTOR
    else create_engine(settings.DATABASE_URL, **_engine_kwargs(settings.DATABASE_URL))
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
