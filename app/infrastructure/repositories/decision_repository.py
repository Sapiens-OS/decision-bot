from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import async_sessionmaker
from datetime import datetime, timedelta, UTC
from app.infrastructure.models.decision import Decision, DecisionStatus
from app.infrastructure.repositories.interfaces.i_decision_repository import IDecisionRepository


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
    ) -> Decision:
        """Create a new decision"""
        async with self.session_factory() as session:
            decision = Decision(
                user_id=user_id,
                problem=problem,
                analysis=analysis,
                selected_option=selected_option,
                status=status,
            )
            session.add(decision)
            await session.commit()
            await session.refresh(decision)
            return decision

    async def get_by_id(self, decision_id: int) -> Decision | None:
        """Get decision by ID"""
        async with self.session_factory() as session:
            result = await session.execute(select(Decision).where(Decision.id == decision_id))
            return result.scalar_one_or_none()

    async def get_user_decisions(self, user_id: int, limit: int = 10) -> list[Decision]:
        """Get user decisions"""
        async with self.session_factory() as session:
            result = await session.execute(
                select(Decision).where(Decision.user_id == user_id).order_by(Decision.created_at.desc()).limit(limit)
            )
            return list(result.scalars().all())

    async def update_status(self, decision_id: int, status: DecisionStatus) -> Decision:
        """Update decision status"""
        async with self.session_factory() as session:
            result = await session.execute(select(Decision).where(Decision.id == decision_id))
            decision = result.scalar_one()
            decision.status = status
            await session.commit()
            await session.refresh(decision)
            return decision

    async def update_selected_option(self, decision_id: int, selected_option: str) -> Decision:
        """Update selected option"""
        async with self.session_factory() as session:
            result = await session.execute(select(Decision).where(Decision.id == decision_id))
            decision = result.scalar_one()
            decision.selected_option = selected_option
            decision.status = DecisionStatus.DECIDED
            await session.commit()
            await session.refresh(decision)
            return decision

    async def get_decisions_for_follow_up(self, days_ago: int) -> list[Decision]:
        """Get decisions that need follow-up"""
        async with self.session_factory() as session:
            target_date = datetime.now(UTC) - timedelta(days=days_ago)
            # Get decisions created around the target date (±12 hours)
            start_date = target_date - timedelta(hours=12)
            end_date = target_date + timedelta(hours=12)

            result = await session.execute(
                select(Decision).where(
                    and_(
                        Decision.status == DecisionStatus.DECIDED,
                        Decision.created_at >= start_date,
                        Decision.created_at <= end_date,
                    )
                )
            )
            return list(result.scalars().all())
