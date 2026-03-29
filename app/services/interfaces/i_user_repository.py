from abc import ABC, abstractmethod
from app.services.dto import UserDTO


class IUserRepository(ABC):
    """User repository interface"""

    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: int) -> UserDTO | None:
        """Get user by telegram ID"""
        pass

    @abstractmethod
    async def create(self, telegram_id: int, username: str | None = None) -> UserDTO:
        """Create a new user"""
        pass

    @abstractmethod
    async def get_or_create(self, telegram_id: int, username: str | None = None) -> UserDTO:
        """Get existing user or create new one"""
        pass
