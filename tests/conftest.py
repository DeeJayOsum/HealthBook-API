import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from tests.database import session_factory, test_engine

from app.db.base import Base
from app.db.session import get_db
from app.main import app

async def override_get_db():
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as test_client:
        yield test_client