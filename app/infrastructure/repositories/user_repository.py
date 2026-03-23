from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.infrastructure.models.user import User
from app.infrastructure.repositories.interfaces.i_user_repository import IUserRepository


class UserRepository(IUserRepository):
    """User repository implementation"""

    def __init__(self, session_factory: async_sessionmaker):
        self.session_factory = session_factory

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        """Get user by telegram ID"""
        async with self.session_factory() as session:
            result = await session.execute(select(User).where(User.telegram_id == telegram_id))
            return result.scalar_one_or_none()

    async def create(self, telegram_id: int, username: str | None = None) -> User:
        """Create a new user"""
        async with self.session_factory() as session:
            user = User(telegram_id=telegram_id, username=username)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    async def get_or_create(self, telegram_id: int, username: str | None = None) -> User:
        """Get existing user or create new one"""
        user = await self.get_by_telegram_id(telegram_id)
        if user is None:
            user = await self.create(telegram_id, username)
        return user
