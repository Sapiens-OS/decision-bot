from app.services.interfaces.i_decision_repository import IDecisionRepository
from app.services.interfaces.i_outcome_repository import IOutcomeRepository
from app.bot.interfaces.i_llm_service import ILLMService
from app.bot.interfaces.i_decision_service import IDecisionService
from app.services.dto import DecisionDTO, OutcomeDTO, DecisionStatus
from app.core.logger import logger


class DecisionService(IDecisionService):
    """Decision service for business logic"""

    def __init__(
        self,
        decision_repository: IDecisionRepository,
        outcome_repository: IOutcomeRepository,
        llm_service: ILLMService,
    ):
        self.decision_repository = decision_repository
        self.outcome_repository = outcome_repository
        self.llm_service = llm_service

    async def create_decision(
        self,
        user_id: int,
        problem: str,
        context: dict[str, str] | None = None,
    ) -> DecisionDTO:
        """Create a new decision with AI analysis"""
        logger.info(f"Creating decision for user {user_id}")

        # Get AI analysis
        analysis = await self.llm_service.analyze_decision(problem, context)

        # Create decision
        decision = await self.decision_repository.create(
            user_id=user_id,
            problem=problem,
            analysis=analysis,
            status=DecisionStatus.NEW,
        )

        logger.info(f"Decision created: {decision.id}")
        return decision

    async def select_option(self, decision_id: int, selected_option: str) -> DecisionDTO:
        """Select an option for a decision"""
        logger.info(f"Selecting option for decision {decision_id}")
        return await self.decision_repository.update_selected_option(decision_id, selected_option)

    async def get_user_decisions(self, user_id: int, limit: int = 10) -> list[DecisionDTO]:
        """Get user decisions"""
        return await self.decision_repository.get_user_decisions(user_id, limit)

    async def get_decision(self, decision_id: int) -> DecisionDTO | None:
        """Get a decision by ID"""
        return await self.decision_repository.get_by_id(decision_id)

    async def add_outcome(self, decision_id: int, feedback: str, score: int) -> OutcomeDTO:
        """Add outcome to a decision"""
        logger.info(f"Adding outcome to decision {decision_id}")

        # Create outcome
        outcome = await self.outcome_repository.create(
            decision_id=decision_id,
            feedback=feedback,
            score=score,
        )

        # Update decision status
        await self.decision_repository.update_status(decision_id, DecisionStatus.COMPLETED)

        logger.info(f"Outcome created: {outcome.id}")
        return outcome

    async def get_decisions_for_follow_up(self, days_ago: int) -> list[DecisionDTO]:
        """Get decisions that need follow-up"""
        return await self.decision_repository.get_decisions_for_follow_up(days_ago)
