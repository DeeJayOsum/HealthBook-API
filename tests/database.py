from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool


test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:", poolclass=StaticPool
)
session_factory = async_sessionmaker(test_engine, expire_on_commit=False)
