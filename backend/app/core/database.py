"""
Database engine and session management for local SQLite and cloud PostgreSQL.
Railway usually injects postgresql://... in DATABASE_URL; SQLAlchemy async endpoints
need the asyncpg driver, while Alembic's sync engine needs a sync PostgreSQL URL.
"""
import os
from typing import AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.logging import logger
from app.models.db_models import Base


def _async_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        return "postgresql+asyncpg://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        return "postgresql+asyncpg://" + url[len("postgresql://"):]
    return url


def _sync_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        return "postgresql+psycopg2://" + url[len("postgres://"):]
    if url.startswith("postgresql+asyncpg://"):
        return "postgresql+psycopg2://" + url[len("postgresql+asyncpg://"):]
    if url.startswith("postgresql+psycopg://"):
        return "postgresql+psycopg2://" + url[len("postgresql+psycopg://"):]
    if url.startswith("postgresql://"):
        return "postgresql+psycopg2://" + url[len("postgresql://"):]
    return url


ASYNC_DATABASE_URL = _async_database_url(settings.DATABASE_URL)
SYNC_DATABASE_URL = _sync_database_url(settings.SYNC_DATABASE_URL or settings.DATABASE_URL)

# Ensure a local SQLite parent directory exists.
parsed_url = make_url(ASYNC_DATABASE_URL)
if parsed_url.get_backend_name() == "sqlite" and parsed_url.database not in (None, ":memory:"):
    os.makedirs(os.path.dirname(os.path.abspath(parsed_url.database)), exist_ok=True)

async_engine = create_async_engine(
    ASYNC_DATABASE_URL, echo=False, future=True, pool_pre_ping=True
)
async_session_factory = async_sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False,
    autocommit=False, autoflush=False
)
sync_engine = create_engine(SYNC_DATABASE_URL, echo=False, pool_pre_ping=True)
sync_session_factory = sessionmaker(
    bind=sync_engine, expire_on_commit=False, autocommit=False, autoflush=False
)


async def init_db() -> None:
    """Create tables on startup; use Alembic for controlled schema upgrades."""
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized successfully.")
    except Exception:
        # Avoid echoing connection strings/secrets from driver exceptions in logs.
        logger.exception("Database initialization failed. Check DATABASE_URL and database logs.")
        raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding an async SQLAlchemy session."""
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
