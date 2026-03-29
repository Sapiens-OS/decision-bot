from abc import ABC, abstractmethod
from app.services.dto import DecisionDTO, OutcomeDTO


class IDecisionService(ABC):
    """Decision service interface"""

    @abstractmethod
    async def create_decision(
        self,
        user_id: int,
        problem: str,
        context: dict[str, str] | None = None,
    ) -> DecisionDTO:
        """Create a new decision with AI analysis"""
        pass

    @abstractmethod
    async def select_option(self, decision_id: int, selected_option: str) -> DecisionDTO:
        """Select an option for a decision"""
        pass

    @abstractmethod
    async def get_user_decisions(self, user_id: int, limit: int = 10) -> list[DecisionDTO]:
        """Get user decisions"""
        pass

    @abstractmethod
    async def get_decision(self, decision_id: int) -> DecisionDTO | None:
        """Get a decision by ID"""
        pass

    @abstractmethod
    async def add_outcome(self, decision_id: int, feedback: str, score: int) -> OutcomeDTO:
        """Add outcome to a decision"""
        pass

    @abstractmethod
    async def get_decisions_for_follow_up(self, days_ago: int) -> list[DecisionDTO]:
        """Get decisions that need follow-up"""
        pass
