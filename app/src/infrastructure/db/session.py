from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from src.core.config.settings import get_settings

settings = get_settings()

# SQLite requires special configuration
if "sqlite" in settings.DATABASE_URL:
    engine: AsyncEngine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG and not settings.is_production,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    engine: AsyncEngine = create_async_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        echo=settings.DEBUG and not settings.is_production,
    )

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding a request-scoped session.

    Commits on clean exit, rolls back on exception, always closes - callers
    (use cases) should not manage transactions themselves.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
