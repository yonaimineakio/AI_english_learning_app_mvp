from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging_config import get_logger
from app.db.session import get_db, engine

logger = get_logger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ai-english-learning-api",
        "version": "1.0.0",
    }


@router.get("/health/db")
def db_health_check(db: Session = Depends(get_db)):
    """
    Database connectivity health check.

    Validates that the API can reach its configured database (e.g. Cloud SQL).
    """
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "ok",
            "cloud_sql_use_connector": settings.CLOUD_SQL_USE_CONNECTOR,
        }
    except Exception as exc:
        logger.exception("Database health check failed: %s", exc)
        raise HTTPException(
            status_code=503, detail="Database connectivity check failed"
        ) from exc

@router.get("/debug/pool")
async def pool_status():
    try:
        return {
            "pool_size": engine.pool.size(),
            "checked_out": engine.pool.checkedout(),  # 現在使用中の接続数
            "checked_in": engine.pool.checkedin(),     # プールに戻っている接続数
            "overflow": engine.pool.overflow(),
            "status": engine.pool.status(),
        }
    except Exception as exc:
        logger.exception("Pool status check failed: %s", exc)
        raise HTTPException(
            status_code=503, detail="Pool status check failed"
        ) from exc