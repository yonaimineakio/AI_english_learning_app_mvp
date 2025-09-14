from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from app.core.config import settings

# Create database engine
if settings.ENVIRONMENT == "development":
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
    )
else:
    engine = create_engine(settings.DATABASE_URL)

# Create declarative base
Base = declarative_base()
