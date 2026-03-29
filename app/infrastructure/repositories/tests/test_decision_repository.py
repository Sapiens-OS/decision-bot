from datetime import datetime, timedelta, UTC

from sqlalchemy import update

from app.infrastructure.models.decision import Decision
from app.services.dto import DecisionStatus


async def _create_user(user_repository, telegram_id: int):
    return await user_repository.create(telegram_id=telegram_id, username=f"u{telegram_id}")


async def test_create_and_get_by_id_persists_decision(user_repository, decision_repository):
    user = await _create_user(user_repository, 3001)

    created = await decision_repository.create(
        user_id=user.id,
        problem="Move to another city?",
        analysis="pros/cons",
    )
    loaded = await decision_repository.get_by_id(created.id)

    assert loaded is not None
    assert loaded.id == created.id
    assert loaded.user_id == user.id
    assert loaded.problem == "Move to another city?"
    assert loaded.analysis == "pros/cons"
    assert loaded.status == DecisionStatus.NEW


async def test_update_selected_option_updates_record_and_status(user_repository, decision_repository):
    user = await _create_user(user_repository, 3002)
    decision = await decision_repository.create(user_id=user.id, problem="Choose stack")

    updated = await decision_repository.update_selected_option(decision.id, "Python")
    reloaded = await decision_repository.get_by_id(decision.id)

    assert updated.selected_option == "Python"
    assert updated.status == DecisionStatus.DECIDED
    assert reloaded is not None
    assert reloaded.selected_option == "Python"
    assert reloaded.status == DecisionStatus.DECIDED


async def test_update_status_persists_new_status(user_repository, decision_repository):
    user = await _create_user(user_repository, 3003)
    decision = await decision_repository.create(user_id=user.id, problem="Quit job?")

    updated = await decision_repository.update_status(decision.id, DecisionStatus.COMPLETED)

    assert updated.status == DecisionStatus.COMPLETED

    loaded = await decision_repository.get_by_id(decision.id)
    assert loaded is not None
    assert loaded.status == DecisionStatus.COMPLETED


async def test_get_user_decisions_returns_latest_first_with_limit(user_repository, decision_repository):
    user = await _create_user(user_repository, 3004)

    d1 = await decision_repository.create(user_id=user.id, problem="d1")
    d2 = await decision_repository.create(user_id=user.id, problem="d2")
    d3 = await decision_repository.create(user_id=user.id, problem="d3")

    items = await decision_repository.get_user_decisions(user_id=user.id, limit=2)

    assert [item.id for item in items] == [d3.id, d2.id]
    assert d1.id not in [item.id for item in items]


async def test_get_decisions_for_follow_up_filters_by_status_and_date(
    user_repository,
    decision_repository,
    session_factory,
):
    user = await _create_user(user_repository, 3005)

    target = await decision_repository.create(
        user_id=user.id,
        problem="target",
        status=DecisionStatus.DECIDED,
    )
    wrong_status = await decision_repository.create(
        user_id=user.id,
        problem="wrong status",
        status=DecisionStatus.NEW,
    )
    outside_window = await decision_repository.create(
        user_id=user.id,
        problem="outside window",
        status=DecisionStatus.DECIDED,
    )

    now = datetime.now(UTC)
    near_target = now - timedelta(days=7, hours=1)
    too_old = now - timedelta(days=9)

    async with session_factory() as session:
        await session.execute(update(Decision).where(Decision.id == target.id).values(created_at=near_target))
        await session.execute(update(Decision).where(Decision.id == wrong_status.id).values(created_at=near_target))
        await session.execute(update(Decision).where(Decision.id == outside_window.id).values(created_at=too_old))
        await session.commit()

    items = await decision_repository.get_decisions_for_follow_up(days_ago=7)

    assert [item.id for item in items] == [target.id]
