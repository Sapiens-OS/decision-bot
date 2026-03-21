from types import SimpleNamespace

from app.bot.keyboards.main_keyboard import (
    get_decision_list_keyboard,
    get_main_menu,
    get_outcome_score_keyboard,
    get_skip_keyboard,
)


def test_get_main_menu_has_expected_buttons():
    kb = get_main_menu()
    texts = [row[0].text for row in kb.keyboard]

    assert texts == ["📝 Новое решение", "📚 История решений", "ℹ️ О боте"]


def test_get_skip_keyboard_has_skip_button():
    kb = get_skip_keyboard()

    assert kb.keyboard[0][0].text == "⏭️ Пропустить"


def test_get_outcome_score_keyboard_has_expected_callbacks():
    kb = get_outcome_score_keyboard()
    callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row]

    assert callbacks == ["score:-2", "score:-1", "score:0", "score:1", "score:2"]


def test_get_decision_list_keyboard_truncates_long_text():
    long_problem = "x" * 60
    decisions = [
        SimpleNamespace(id=1, problem=long_problem),
        SimpleNamespace(id=2, problem="short"),
    ]

    kb = get_decision_list_keyboard(decisions)

    assert kb.inline_keyboard[0][0].text == ("x" * 50 + "...")
    assert kb.inline_keyboard[0][0].callback_data == "decision:1"
    assert kb.inline_keyboard[1][0].text == "short"
    assert kb.inline_keyboard[1][0].callback_data == "decision:2"
