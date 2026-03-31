from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.infrastructure.models.user import User
from app.services.dto import UserDTO
from app.services.interfaces.i_user_repository import IUserRepository


class UserRepository(IUserRepository):
    """User repository implementation"""

    def __init__(self, session_factory: async_sessionmaker):
        self.session_factory = session_factory

    async def get_by_telegram_id(self, telegram_id: int) -> UserDTO | None:
        """Get user by telegram ID"""
        async with self.session_factory() as session:
            result = await session.execute(select(User).where(User.telegram_id == telegram_id))
            user = result.scalar_one_or_none()
            return self._to_dto(user) if user else None

    async def create(self, telegram_id: int, username: str | None = None) -> UserDTO:
        """Create a new user"""
        async with self.session_factory() as session:
            user = User(telegram_id=telegram_id, username=username)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return self._to_dto(user)

    async def get_or_create(self, telegram_id: int, username: str | None = None) -> UserDTO:
        """Get existing user or create new one"""
        user = await self.get_by_telegram_id(telegram_id)
        if user is None:
            user = await self.create(telegram_id, username)
        return user

    async def increment_max_questions(self, telegram_id: int, increment_on: int) -> None:
        """Update max_questions"""
        async with self.session_factory() as session:
            result = await session.execute(select(User).where(User.telegram_id == telegram_id))
            user = result.scalar_one()
            user.max_questions += increment_on
            await session.commit()

    def _to_dto(self, user: User) -> UserDTO:
        """Convert SQLAlchemy model to DTO"""
        return UserDTO(
            id=user.id,
            telegram_id=user.telegram_id,
            username=user.username,
            max_questions=user.max_questions,
            created_at=user.created_at,
        )
