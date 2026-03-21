import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.infrastructure.models.base import Base
from app.infrastructure.repositories.decision_repository import DecisionRepository
from app.infrastructure.repositories.outcome_repository import OutcomeRepository
from app.infrastructure.repositories.user_repository import UserRepository


@pytest_asyncio.fixture
async def session_factory(tmp_path):
    db_path = tmp_path / "test.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}")
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    try:
        yield factory
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def user_repository(session_factory):
    return UserRepository(session_factory)


@pytest_asyncio.fixture
async def decision_repository(session_factory):
    return DecisionRepository(session_factory)


@pytest_asyncio.fixture
async def outcome_repository(session_factory):
    return OutcomeRepository(session_factory)
