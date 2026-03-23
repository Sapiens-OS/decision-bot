from abc import ABC, abstractmethod
from app.infrastructure.models.decision import Decision, DecisionStatus


class IDecisionRepository(ABC):
    """Decision repository interface"""

    @abstractmethod
    async def create(
        self,
        user_id: int,
        problem: str,
        analysis: str | None = None,
        selected_option: str | None = None,
        status: DecisionStatus = DecisionStatus.NEW,
    ) -> Decision:
        """Create a new decision"""
        pass

    @abstractmethod
    async def get_by_id(self, decision_id: int) -> Decision | None:
        """Get decision by ID"""
        pass

    @abstractmethod
    async def get_user_decisions(self, user_id: int, limit: int = 10) -> list[Decision]:
        """Get user decisions"""
        pass

    @abstractmethod
    async def update_status(self, decision_id: int, status: DecisionStatus) -> Decision:
        """Update decision status"""
        pass

    @abstractmethod
    async def update_selected_option(self, decision_id: int, selected_option: str) -> Decision:
        """Update selected option"""
        pass

    @abstractmethod
    async def get_decisions_for_follow_up(self, days_ago: int) -> list[Decision]:
        """Get decisions that need follow-up"""
        pass
