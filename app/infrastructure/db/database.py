from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.logger import logger


class Database:
    """Database connection manager"""

    def __init__(self, db_url: str):
        self.engine = create_async_engine(db_url, echo=False, future=True)
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        logger.info(f"Database initialized with URL: {db_url}")

    async def create_tables(self):
        """Create all tables"""
        from app.infrastructure.models.base import Base

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created")

    async def drop_tables(self):
        """Drop all tables"""
        from app.infrastructure.models.base import Base

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.info("Database tables dropped")

    def session(self) -> async_sessionmaker:
        """Get session factory"""
        return self.session_factory
