"""
FastAPI entrypoint (compat).

This module is referenced by some docker-compose commands as `uvicorn main:app`.
The canonical application lives in `app.main` (which includes all routers).
"""

from app.main import app  # noqa: F401

