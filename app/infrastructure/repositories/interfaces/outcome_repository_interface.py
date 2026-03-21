from abc import ABC, abstractmethod
from app.infrastructure.models.outcome import Outcome


class IOutcomeRepository(ABC):
    """Outcome repository interface"""

    @abstractmethod
    async def create(self, decision_id: int, feedback: str, score: int) -> Outcome:
        """Create a new outcome"""
        pass

    @abstractmethod
    async def get_by_decision_id(self, decision_id: int) -> list[Outcome]:
        """Get outcomes by decision ID"""
        pass
