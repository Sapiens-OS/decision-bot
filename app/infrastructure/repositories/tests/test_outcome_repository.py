from datetime import datetime, timedelta, UTC

from sqlalchemy import update

from app.infrastructure.models.outcome import Outcome


async def _create_decision(user_repository, decision_repository, telegram_id: int):
    user = await user_repository.create(telegram_id=telegram_id, username=f"u{telegram_id}")
    return await decision_repository.create(user_id=user.id, problem="test problem")


async def test_create_and_get_by_decision_id_persists_outcome(
    user_repository,
    decision_repository,
    outcome_repository,
):
    decision = await _create_decision(user_repository, decision_repository, telegram_id=4001)

    created = await outcome_repository.create(
        decision_id=decision.id,
        feedback="Worked better than expected",
        score=2,
    )
    items = await outcome_repository.get_by_decision_id(decision_id=decision.id)

    assert created.id is not None
    assert len(items) == 1
    assert items[0].id == created.id
    assert items[0].feedback == "Worked better than expected"
    assert items[0].score == 2


async def test_get_by_decision_id_returns_latest_first(
    user_repository,
    decision_repository,
    outcome_repository,
    session_factory,
):
    decision = await _create_decision(user_repository, decision_repository, telegram_id=4002)

    older = await outcome_repository.create(decision_id=decision.id, feedback="older", score=0)
    newer = await outcome_repository.create(decision_id=decision.id, feedback="newer", score=1)

    now = datetime.now(UTC)
    async with session_factory() as session:
        await session.execute(update(Outcome).where(Outcome.id == older.id).values(created_at=now - timedelta(days=1)))
        await session.execute(update(Outcome).where(Outcome.id == newer.id).values(created_at=now))
        await session.commit()

    items = await outcome_repository.get_by_decision_id(decision_id=decision.id)

    assert [item.id for item in items] == [newer.id, older.id]
