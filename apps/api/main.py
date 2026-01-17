"""
FastAPI entrypoint (compat).

This module is referenced by some docker-compose commands as `uvicorn main:app`.
The canonical application lives in `app.main` (which includes all routers).
"""

from __future__ import annotations

# NOTE:
# `uvicorn main:app` is sometimes executed from the repository root (not `apps/api`).
# In that case, Python cannot resolve the local `app/` package unless `apps/api`
# is on sys.path. We harden the entrypoint to work regardless of the working dir.
import sys
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from app.main import app  # noqa: F401
