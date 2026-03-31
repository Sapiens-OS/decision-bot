from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import async_sessionmaker
from datetime import datetime, timedelta, UTC
from sqlalchemy.orm import joinedload
from app.infrastructure.models.decision import Decision, DecisionStatus as ModelDecisionStatus
from app.services.dto import DecisionDTO, DecisionStatus
from app.services.interfaces.i_decision_repository import IDecisionRepository


class DecisionRepository(IDecisionRepository):
    """Decision repository implementation"""

    def __init__(self, session_factory: async_sessionmaker):
        self.session_factory = session_factory

    async def create(
        self,
        user_id: int,
        problem: str,
        analysis: str | None = None,
        selected_option: str | None = None,
        status: DecisionStatus = DecisionStatus.NEW,
    ) -> DecisionDTO:
        """Create a new decision"""
        async with self.session_factory() as session:
            decision = Decision(
                user_id=user_id,
                problem=problem,
                analysis=analysis,
                selected_option=selected_option,
                status=ModelDecisionStatus(status.value),
            )
            session.add(decision)
            await session.commit()
            await session.refresh(decision)
            return self._to_dto(decision)

    async def get_by_id(self, decision_id: int) -> DecisionDTO | None:
        """Get decision by ID"""
        async with self.session_factory() as session:
            result = await session.execute(select(Decision).where(Decision.id == decision_id))
            decision = result.scalar_one_or_none()
            return self._to_dto(decision) if decision else None

    async def get_user_decisions(self, user_id: int, limit: int = 10) -> list[DecisionDTO]:
        """Get user decisions"""
        async with self.session_factory() as session:
            result = await session.execute(
                select(Decision).where(Decision.user_id == user_id).order_by(Decision.created_at.desc()).limit(limit)
            )
            return [self._to_dto(d) for d in result.scalars().all()]

    async def update_status(self, decision_id: int, status: DecisionStatus) -> DecisionDTO:
        """Update decision status"""
        async with self.session_factory() as session:
            result = await session.execute(select(Decision).where(Decision.id == decision_id))
            decision = result.scalar_one()
            decision.status = ModelDecisionStatus(status.value)
            await session.commit()
            await session.refresh(decision)
            return self._to_dto(decision)

    async def update_selected_option(self, decision_id: int, selected_option: str) -> DecisionDTO:
        """Update selected option"""
        async with self.session_factory() as session:
            result = await session.execute(select(Decision).where(Decision.id == decision_id))
            decision = result.scalar_one()
            decision.selected_option = selected_option
            decision.status = ModelDecisionStatus.DECIDED
            await session.commit()
            await session.refresh(decision)
            return self._to_dto(decision)

    async def get_decisions_for_follow_up(self, days_ago: int) -> list[DecisionDTO]:
        """Get decisions that need follow-up"""
        async with self.session_factory() as session:
            target_date = datetime.now(UTC) - timedelta(days=days_ago)
            # Get decisions created around the target date (±12 hours)
            start_date = target_date - timedelta(hours=12)
            end_date = target_date + timedelta(hours=12)

            result = await session.execute(
                select(Decision)
                .options(joinedload(Decision.user))
                .where(
                    and_(
                        Decision.status == ModelDecisionStatus.DECIDED,
                        Decision.created_at >= start_date,
                        Decision.created_at <= end_date,
                    )
                )
            )
            return [self._to_dto(d) for d in result.scalars().all()]

    async def count_user_decisions(self, user_id: int) -> int:
        """Count user decisions"""
        async with self.session_factory() as session:
            result = await session.execute(select(func.count()).where(Decision.user_id == user_id))
            return result.scalar_one()

    def _to_dto(self, decision: Decision) -> DecisionDTO:
        """Convert SQLAlchemy model to DTO"""
        user_telegram_id = None
        try:
            # Check if user relationship is loaded
            if hasattr(decision, "user") and decision.user:
                user_telegram_id = decision.user.telegram_id
        except Exception:
            pass

        return DecisionDTO(
            id=decision.id,
            user_id=decision.user_id,
            problem=decision.problem,
            analysis=decision.analysis,
            selected_option=decision.selected_option,
            status=DecisionStatus(decision.status.value),
            created_at=decision.created_at,
            user_telegram_id=user_telegram_id,
        )
