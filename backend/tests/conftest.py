import os
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.main import app
from app.db.session import get_db
from app.db.base import Base


DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    os.environ.get("DATABASE_URL", ""),
)


@pytest.fixture(scope="module")
def engine():
    """Module-scoped async engine connected to the test database."""
    if not DATABASE_URL:
        pytest.skip("No DATABASE_URL set for integration tests")
    return create_async_engine(DATABASE_URL, echo=False)


@pytest.fixture(scope="module")
async def run_migrations(engine):
    """Run Alembic migrations against the test database once per module."""
    import alembic.config
    import alembic.command

    alembic_cfg = alembic.config.Config(
        os.path.join(os.path.dirname(__file__), "..", "alembic.ini")
    )
    alembic_cfg.set_main_option("sqlalchemy.url", DATABASE_URL)
    alembic_cfg.set_main_option(
        "script_location",
        os.path.join(os.path.dirname(__file__), "..", "alembic"),
    )
    alembic.command.upgrade(alembic_cfg, "head")
    yield
    # Teardown: drop all tables so next module run is clean
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture(scope="module")
async def client(engine, run_migrations) -> AsyncGenerator[AsyncClient, None]:
    """Session-scoped HTTP test client using the real database."""
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
