from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from src.core.logging.logger import get_logger
from src.infrastructure.db.session import engine

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("database_connection_ok")
    except Exception as exc:
        # Non-fatal: lets the API boot (and health/docs work) before Postgres
        # exists yet - the database schema itself lands in a later step.
        logger.warning("database_connection_failed", extra={"error": str(exc)})

    yield

    await engine.dispose()
    logger.info("database_engine_disposed")
