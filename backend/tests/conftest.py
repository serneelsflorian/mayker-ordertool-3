import os
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.main import app
from app.db.session import get_db
from app.db.base import Base
from app.models.order import Order  # noqa: F401 — registers model on Base.metadata
from app.models.menu_item import MenuItem  # noqa: F401 — registers model on Base.metadata


@pytest_asyncio.fixture(scope="session")
async def engine():
    """Session-scoped async engine; creates all tables once and drops them at teardown.

    Uses Base.metadata.create_all so that no nested asyncio.run() is triggered
    (unlike alembic.command.upgrade which calls asyncio.run() internally and
    raises RuntimeError when invoked from an already-running event loop).
    """
    url = os.environ.get("TEST_DATABASE_URL", os.environ.get("DATABASE_URL", ""))
    if not url:
        pytest.skip("No DATABASE_URL set for integration tests")
    eng = create_async_engine(url, echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest_asyncio.fixture
async def client(engine) -> AsyncGenerator[AsyncClient, None]:
    """Function-scoped HTTP test client with per-test transaction rollback isolation.

    Opens an outer transaction via the context-manager form (required by asyncpg
    when nesting savepoints) then opens a SAVEPOINT via begin_nested().  The
    service layer calls session.commit(), which in SQLAlchemy 2.x commits the
    innermost savepoint while keeping the outer transaction alive.  After the
    test the outer transaction is rolled back, discarding all changes and
    providing clean state for the next test.
    """
    async with engine.connect() as conn:
        async with conn.begin():
            await conn.begin_nested()

            session_factory = async_sessionmaker(
                bind=conn,
                class_=AsyncSession,
                expire_on_commit=False,
            )

            async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
                async with session_factory() as session:
                    yield session

            app.dependency_overrides[get_db] = override_get_db

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as ac:
                yield ac

            app.dependency_overrides.pop(get_db, None)
            await conn.rollback()
