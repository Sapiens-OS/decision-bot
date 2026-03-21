from abc import ABC, abstractmethod
from app.infrastructure.models.user import User


class IUserRepository(ABC):
    """User repository interface"""

    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        """Get user by telegram ID"""
        pass

    @abstractmethod
    async def create(self, telegram_id: int, username: str | None = None) -> User:
        """Create a new user"""
        pass

    @abstractmethod
    async def get_or_create(self, telegram_id: int, username: str | None = None) -> User:
        """Get existing user or create new one"""
        pass
