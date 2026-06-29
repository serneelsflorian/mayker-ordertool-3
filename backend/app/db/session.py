from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine

_engine: "AsyncEngine | None" = None
_async_session_factory: "async_sessionmaker[AsyncSession] | None" = None


def _get_engine() -> "AsyncEngine":
    global _engine
    if _engine is None:
        from app.core.config import get_settings
        _engine = create_async_engine(
            get_settings().DATABASE_URL,
            echo=False,
            pool_pre_ping=True,
        )
    return _engine


def _get_session_factory() -> "async_sessionmaker[AsyncSession]":
    global _async_session_factory
    if _async_session_factory is None:
        _async_session_factory = async_sessionmaker(
            _get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _async_session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that provides an async database session."""
    async with _get_session_factory()() as session:
        yield session
