from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.bot.handlers.history_handler import cmd_history, show_decision
from app.bot.handlers.new_decision_handler import cmd_new_decision
from app.bot.handlers.outcome_handler import (
    process_outcome_feedback,
    process_outcome_score,
    start_outcome_feedback,
)
from app.bot.handlers.start_handler import about_bot, cmd_start
from app.bot.states import NewDecisionStates, OutcomeStates


class DummyState:
    def __init__(self, data=None):
        self.data = data or {}
        self.current_state = None

    async def update_data(self, **kwargs):
        self.data.update(kwargs)

    async def get_data(self):
        return self.data

    async def set_state(self, state):
        self.current_state = state

    async def clear(self):
        self.data.clear()
        self.current_state = None


class DummyMessage:
    def __init__(self, text=None, user_id=1, username="user"):
        self.text = text
        self.from_user = SimpleNamespace(id=user_id, username=username)
        self.answer = AsyncMock()


class DummyCallback:
    def __init__(self, data):
        self.data = data
        self.answer = AsyncMock()
        self.message = DummyMessage()


async def test_cmd_start_creates_user_and_sends_welcome():
    message = DummyMessage(user_id=10, username="alice")
    user_repository = SimpleNamespace(get_or_create=AsyncMock())

    await cmd_start(message=message, user_repository=user_repository)

    user_repository.get_or_create.assert_awaited_once_with(telegram_id=10, username="alice")
    message.answer.assert_awaited_once()


async def test_about_bot_sends_info_message():
    message = DummyMessage()

    await about_bot(message)

    message.answer.assert_awaited_once()


async def test_cmd_new_decision_sets_waiting_for_problem_state():
    message = DummyMessage()
    state = DummyState()

    await cmd_new_decision(message=message, state=state)

    message.answer.assert_awaited_once()
    assert state.current_state == NewDecisionStates.waiting_for_problem


async def test_cmd_history_when_user_absent_sends_empty_history_message():
    message = DummyMessage(user_id=11)
    user_repository = SimpleNamespace(get_by_telegram_id=AsyncMock(return_value=None))
    decision_service = SimpleNamespace(get_user_decisions=AsyncMock())

    await cmd_history(message=message, user_repository=user_repository, decision_service=decision_service)

    message.answer.assert_awaited_once()
    decision_service.get_user_decisions.assert_not_called()


async def test_cmd_history_when_decisions_exist_sends_list_keyboard():
    message = DummyMessage(user_id=12)
    user = SimpleNamespace(id=7)
    decisions = [SimpleNamespace(id=1, problem="p1"), SimpleNamespace(id=2, problem="p2")]
    user_repository = SimpleNamespace(get_by_telegram_id=AsyncMock(return_value=user))
    decision_service = SimpleNamespace(get_user_decisions=AsyncMock(return_value=decisions))

    await cmd_history(message=message, user_repository=user_repository, decision_service=decision_service)

    decision_service.get_user_decisions.assert_awaited_once_with(7, limit=10)
    message.answer.assert_awaited_once()


async def test_show_decision_not_found_returns_alert():
    callback = DummyCallback(data="decision:42")
    decision_service = SimpleNamespace(get_decision=AsyncMock(return_value=None))

    await show_decision(callback=callback, decision_service=decision_service)

    callback.answer.assert_awaited_once_with("Решение не найдено", show_alert=True)


async def test_show_decision_success_sends_details():
    callback = DummyCallback(data="decision:15")
    decision = SimpleNamespace(
        id=15,
        status=SimpleNamespace(value="decided"),
        created_at=datetime(2026, 1, 1, 12, 0),
        problem="Проблема",
        analysis="Анализ",
        selected_option="Вариант",
    )
    decision_service = SimpleNamespace(get_decision=AsyncMock(return_value=decision))

    await show_decision(callback=callback, decision_service=decision_service)

    callback.message.answer.assert_awaited_once()
    callback.answer.assert_awaited_once_with()


async def test_start_outcome_feedback_updates_state_and_prompts_user():
    callback = DummyCallback(data="outcome:99")
    state = DummyState()

    await start_outcome_feedback(callback=callback, state=state)

    assert state.data["decision_id"] == 99
    assert state.current_state == OutcomeStates.waiting_for_feedback
    callback.message.answer.assert_awaited_once()
    callback.answer.assert_awaited_once_with()


async def test_process_outcome_feedback_saves_feedback_and_sets_score_state():
    message = DummyMessage(text="Сработало")
    state = DummyState()

    await process_outcome_feedback(message=message, state=state)

    assert state.data["feedback"] == "Сработало"
    assert state.current_state == OutcomeStates.waiting_for_score
    message.answer.assert_awaited_once()


async def test_process_outcome_score_success_saves_outcome_and_clears_state():
    callback = DummyCallback(data="score:2")
    state = DummyState(data={"decision_id": 5, "feedback": "ok"})
    decision_service = SimpleNamespace(add_outcome=AsyncMock())

    await process_outcome_score(callback=callback, state=state, decision_service=decision_service)

    decision_service.add_outcome.assert_awaited_once_with(decision_id=5, feedback="ok", score=2)
    callback.message.answer.assert_awaited_once()
    assert state.data == {}
    assert state.current_state is None


async def test_process_outcome_score_failure_sends_error_and_clears_state():
    callback = DummyCallback(data="score:-1")
    state = DummyState(data={"decision_id": 7, "feedback": "bad"})
    decision_service = SimpleNamespace(add_outcome=AsyncMock(side_effect=RuntimeError("boom")))

    await process_outcome_score(callback=callback, state=state, decision_service=decision_service)

    callback.message.answer.assert_awaited_once()
    assert state.data == {}
    assert state.current_state is None
