import os
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, ANY
from app.tasks import follow_up

os.environ.setdefault("BOT_TOKEN", "123456:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")


def _make_decision(decision_id: int, telegram_id: int = 100):
    return SimpleNamespace(
        id=decision_id,
        problem="Проблема",
        selected_option="Выбор",
        user_telegram_id=telegram_id,
    )


async def test_send_follow_up_message_calls_bot_with_expected_payload(monkeypatch):
    decision = _make_decision(10, telegram_id=12345)
    send_message = AsyncMock()
    monkeypatch.setattr(follow_up, "bot", SimpleNamespace(send_message=send_message))

    await follow_up.send_follow_up_message(decision, days=7)

    send_message.assert_awaited_once_with(
        chat_id=12345,
        text=ANY,
        reply_markup=ANY,
    )
    # Get the actual call to check the content
    await_args = send_message.await_args
    assert await_args is not None
    args, kwargs = await_args
    assert "Прошло 7 дней" in kwargs["text"]
    assert "Проблема" in kwargs["text"]
    assert "Выбор" in kwargs["text"]
    keyboard = kwargs["reply_markup"]
    assert keyboard.inline_keyboard[0][0].callback_data == "outcome:10"


async def test_check_follow_up_iterates_intervals_and_sends_messages(monkeypatch):
    d1 = _make_decision(1)
    d2 = _make_decision(2)
    decision_service = AsyncMock()
    decision_service.get_decisions_for_follow_up.side_effect = [[d1], [d2]]
    container = SimpleNamespace(decision_service=lambda: decision_service)

    send_mock = AsyncMock()
    monkeypatch.setattr(follow_up, "Container", lambda: container)
    monkeypatch.setattr(follow_up.config, "follow_up_intervals", [7, 30])
    monkeypatch.setattr(follow_up, "send_follow_up_message", send_mock)

    await follow_up.check_follow_up(decision_service)

    assert decision_service.get_decisions_for_follow_up.await_count == 2
    decision_service.get_decisions_for_follow_up.assert_any_await(7)
    decision_service.get_decisions_for_follow_up.assert_any_await(30)
    assert send_mock.await_count == 2
    send_mock.assert_any_await(d1, 7)
    send_mock.assert_any_await(d2, 30)


async def test_check_follow_up_continues_when_sending_fails(monkeypatch):
    d1 = _make_decision(1)
    d2 = _make_decision(2)
    decision_service = AsyncMock()
    decision_service.get_decisions_for_follow_up.return_value = [d1, d2]
    container = SimpleNamespace(decision_service=lambda: decision_service)

    send_mock = AsyncMock(side_effect=[RuntimeError("tg fail"), None])
    monkeypatch.setattr(follow_up, "Container", lambda: container)
    monkeypatch.setattr(follow_up.config, "follow_up_intervals", [7])
    monkeypatch.setattr(follow_up, "send_follow_up_message", send_mock)

    await follow_up.check_follow_up(decision_service)

    assert send_mock.await_count == 2


def test_check_follow_up_task_runs_async_function(monkeypatch):
    def _fake_run(coro):
        coro.close()

    run_mock = MagicMock(side_effect=_fake_run)
    monkeypatch.setattr(follow_up.asyncio, "run", run_mock)

    follow_up.check_follow_up_task()

    run_mock.assert_called_once()
