from abc import ABC, abstractmethod
from app.services.dto import OutcomeDTO


class IOutcomeRepository(ABC):
    """Outcome repository interface"""

    @abstractmethod
    async def create(self, decision_id: int, feedback: str, score: int) -> OutcomeDTO:
        """Create a new outcome"""
        pass

    @abstractmethod
    async def get_by_decision_id(self, decision_id: int) -> list[OutcomeDTO]:
        """Get outcomes by decision ID"""
        pass
