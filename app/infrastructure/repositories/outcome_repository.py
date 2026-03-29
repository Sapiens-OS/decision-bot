from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.infrastructure.models.outcome import Outcome
from app.services.dto import OutcomeDTO
from app.services.interfaces.i_outcome_repository import IOutcomeRepository


class OutcomeRepository(IOutcomeRepository):
    """Outcome repository implementation"""

    def __init__(self, session_factory: async_sessionmaker):
        self.session_factory = session_factory

    async def create(self, decision_id: int, feedback: str, score: int) -> OutcomeDTO:
        """Create a new outcome"""
        async with self.session_factory() as session:
            outcome = Outcome(decision_id=decision_id, feedback=feedback, score=score)
            session.add(outcome)
            await session.commit()
            await session.refresh(outcome)
            return self._to_dto(outcome)

    async def get_by_decision_id(self, decision_id: int) -> list[OutcomeDTO]:
        """Get outcomes by decision ID"""
        async with self.session_factory() as session:
            result = await session.execute(
                select(Outcome).where(Outcome.decision_id == decision_id).order_by(Outcome.created_at.desc())
            )
            return [self._to_dto(o) for o in result.scalars().all()]

    def _to_dto(self, outcome: Outcome) -> OutcomeDTO:
        """Convert SQLAlchemy model to DTO"""
        return OutcomeDTO(
            id=outcome.id,
            decision_id=outcome.decision_id,
            feedback=outcome.feedback,
            score=outcome.score,
            created_at=outcome.created_at,
        )
