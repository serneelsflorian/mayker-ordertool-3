import os
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession, async_sessionmaker, create_async_engine

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


@pytest_asyncio.fixture(scope="function")
async def db_connection(engine, run_migrations) -> AsyncGenerator[AsyncConnection, None]:
    """Function-scoped connection that wraps each test in a rolled-back transaction."""
    async with engine.connect() as connection:
        await connection.begin()
        yield connection
        await connection.rollback()


@pytest_asyncio.fixture(scope="module")
async def client(engine, run_migrations) -> AsyncGenerator[AsyncClient, None]:
    """Module-scoped HTTP test client.

    Each test gets its own rolled-back transaction via the ``db_connection``
    fixture which overrides ``get_db`` for the duration of that test.
    The module-scoped client is kept so the ASGI app does not need to be
    recreated on every test.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function", autouse=False)
async def isolated_client(
    client: AsyncClient, db_connection: AsyncConnection
) -> AsyncGenerator[AsyncClient, None]:
    """Yield the module client with ``get_db`` overridden to use the per-test
    rolled-back connection, providing transaction-level test isolation."""
    session_factory = async_sessionmaker(
        bind=db_connection, class_=AsyncSession, expire_on_commit=False
    )

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    yield client
    app.dependency_overrides.pop(get_db, None)
