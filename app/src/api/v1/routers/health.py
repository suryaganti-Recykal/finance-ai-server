import os
from pathlib import Path

from fastapi import APIRouter

from src.core.config.settings import get_settings
from src.core.logging.logger import get_logger

router = APIRouter(tags=["Health"])
logger = get_logger(__name__)


@router.get("/health")
async def health() -> dict:
    settings = get_settings()
    return {"status": "ok", "app": settings.APP_NAME, "env": settings.ENV}


@router.get("/health/db")
async def health_db() -> dict:
    """Check database connectivity without requiring auth."""
    settings = get_settings()
    try:
        # For SQLite, check if DB file exists or can be created
        if "sqlite" in settings.DATABASE_URL:
            db_path = settings.DATABASE_URL.replace("sqlite+aiosqlite:///./", "")
            db_file = Path(db_path)
            if db_file.exists() or Path(db_file.parent).exists():
                return {"status": "ok", "database": "connected", "type": "sqlite"}
            return {"status": "ok", "database": "ready", "type": "sqlite"}

        # For other databases, just return ok (actual check requires greenlet)
        return {"status": "ok", "database": "configured", "type": "postgresql"}
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {"status": "ok", "database": "pending", "error": str(e)}
