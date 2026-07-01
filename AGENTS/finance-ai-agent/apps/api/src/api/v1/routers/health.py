from fastapi import APIRouter
from sqlalchemy import text

from src.api.deps import DbSession
from src.core.config.settings import get_settings

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health() -> dict:
    settings = get_settings()
    return {"status": "ok", "app": settings.APP_NAME, "env": settings.ENV}


@router.get("/health/db")
async def health_db(db: DbSession) -> dict:
    await db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "reachable"}
