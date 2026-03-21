from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.bot.states import NewDecisionStates
from app.bot.use_cases.new_decision_use_case import process_context, process_problem, process_selection


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


class DummyLoadingMessage:
    def __init__(self):
        self.delete = AsyncMock()


class DummyMessage:
    def __init__(self, text=None, user_id=1, username="user"):
        self.text = text
        self.from_user = SimpleNamespace(id=user_id, username=username)
        self.answer = AsyncMock()


async def test_process_problem_stores_problem_and_user_and_moves_to_context_state():
    message = DummyMessage(text="Новая задача", user_id=100, username="bob")
    state = DummyState()
    user_repository = SimpleNamespace(get_or_create=AsyncMock(return_value=SimpleNamespace(id=55)))
    decision_service = SimpleNamespace()

    await process_problem(
        message=message,
        state=state,
        user_repository=user_repository,
        decision_service=decision_service,
    )

    user_repository.get_or_create.assert_awaited_once_with(telegram_id=100, username="bob")
    assert state.data["problem"] == "Новая задача"
    assert state.data["user_id"] == 55
    assert state.current_state == NewDecisionStates.waiting_for_context


async def test_process_context_success_with_skip_creates_decision_and_sets_selection_state():
    message = DummyMessage(text="⏭️ Пропустить")
    loading_msg = DummyLoadingMessage()
    decision = SimpleNamespace(id=77, analysis="analysis")
    message.answer = AsyncMock(side_effect=[loading_msg, None])

    state = DummyState(data={"problem": "p", "user_id": 10})
    decision_service = SimpleNamespace(create_decision=AsyncMock(return_value=decision))

    await process_context(message=message, state=state, decision_service=decision_service)

    decision_service.create_decision.assert_awaited_once_with(user_id=10, problem="p", context=None)
    loading_msg.delete.assert_awaited_once()
    assert state.data["decision_id"] == 77
    assert state.current_state == NewDecisionStates.waiting_for_selection


async def test_process_context_failure_clears_state_and_sends_error():
    message = DummyMessage(text="контекст")
    loading_msg = DummyLoadingMessage()
    message.answer = AsyncMock(side_effect=[loading_msg, None])

    state = DummyState(data={"problem": "p", "user_id": 10})
    decision_service = SimpleNamespace(create_decision=AsyncMock(side_effect=RuntimeError("llm down")))

    await process_context(message=message, state=state, decision_service=decision_service)

    loading_msg.delete.assert_awaited_once()
    assert state.data == {}
    assert state.current_state is None


async def test_process_selection_success_updates_decision_and_clears_state():
    message = DummyMessage(text="мой выбор")
    state = DummyState(data={"decision_id": 88})
    decision_service = SimpleNamespace(select_option=AsyncMock())

    await process_selection(message=message, state=state, decision_service=decision_service)

    decision_service.select_option.assert_awaited_once_with(88, "мой выбор")
    assert state.data == {}
    assert state.current_state is None


async def test_process_selection_failure_still_clears_state():
    message = DummyMessage(text="мой выбор")
    state = DummyState(data={"decision_id": 88})
    decision_service = SimpleNamespace(select_option=AsyncMock(side_effect=RuntimeError("db err")))

    await process_selection(message=message, state=state, decision_service=decision_service)

    assert state.data == {}
    assert state.current_state is None
