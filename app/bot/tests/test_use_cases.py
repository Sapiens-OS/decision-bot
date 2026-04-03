from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.bot.states import NewDecisionStates
from app.bot.use_cases.new_decision_use_case import (
    process_context,
    process_problem,
    process_selection,
    process_confirmation,
)


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
    user_repository = SimpleNamespace(get_or_create=AsyncMock(return_value=SimpleNamespace(id=55, max_questions=10)))
    decision_repository = SimpleNamespace(count_user_decisions=AsyncMock(return_value=5))

    await process_problem(
        message=message,
        state=state,
        user_repository=user_repository,
        decision_repository=decision_repository,
    )

    user_repository.get_or_create.assert_awaited_once_with(telegram_id=100, username="bob")
    decision_repository.count_user_decisions.assert_awaited_once_with(55)
    assert state.data["problem"] == "Новая задача"
    assert state.data["user_id"] == 55
    assert state.current_state == NewDecisionStates.waiting_for_context


async def test_process_problem_limit_reached():
    message = DummyMessage(text="Новая задача", user_id=100, username="bob")
    state = DummyState()
    user_repository = SimpleNamespace(get_or_create=AsyncMock(return_value=SimpleNamespace(id=55, max_questions=5)))
    decision_repository = SimpleNamespace(count_user_decisions=AsyncMock(return_value=5))

    await process_problem(
        message=message,
        state=state,
        user_repository=user_repository,
        decision_repository=decision_repository,
    )

    message.answer.assert_called_once()
    args, kwargs = message.answer.call_args
    assert "достигнут лимит сообщений" in args[0]
    assert state.current_state is None
    assert "problem" not in state.data


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


async def test_process_selection_moves_to_confirmation_state():
    message = DummyMessage(text="мой выбор")
    state = DummyState(data={"problem": "купить машину", "decision_id": 88})

    await process_selection(message=message, state=state)

    assert state.data["selected_option"] == "мой выбор"
    assert state.current_state == NewDecisionStates.waiting_for_confirmation
    message.answer.assert_called_once()
    assert "Все верно, сохраняем?" in message.answer.call_args[0][0]


async def test_process_confirmation_yes_updates_decision_and_clears_state():
    message = DummyMessage(text="✅ Да")
    state = DummyState(data={"decision_id": 88, "selected_option": "мой выбор"})
    decision_service = SimpleNamespace(select_option=AsyncMock())

    await process_confirmation(message=message, state=state, decision_service=decision_service)

    decision_service.select_option.assert_awaited_once_with(88, "мой выбор")
    assert state.data == {}
    assert state.current_state is None


async def test_process_confirmation_change_moves_back_to_selection_state():
    message = DummyMessage(text="✏️ Поменять решение")
    state = DummyState(data={"decision_id": 88, "selected_option": "мой выбор"})
    decision_service = SimpleNamespace(select_option=AsyncMock())

    await process_confirmation(message=message, state=state, decision_service=decision_service)

    decision_service.select_option.assert_not_called()
    assert state.current_state == NewDecisionStates.waiting_for_selection
