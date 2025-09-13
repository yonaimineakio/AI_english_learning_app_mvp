"""
Database base configuration
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create database engine
if settings.ENVIRONMENT == "development":
    # Use SQLite for development
    engine = create_engine(
        settings.DATABASE_URL_SQLITE,
        connect_args={"check_same_thread": False}
    )
else:
    # Use PostgreSQL for production
    engine = create_engine(settings.DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
