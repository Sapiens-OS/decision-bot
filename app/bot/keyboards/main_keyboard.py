from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from app.services.dto import DecisionStatus


def get_main_menu() -> ReplyKeyboardMarkup:
    """Get main menu keyboard"""
    keyboard = [
        [KeyboardButton(text="📝 Новое решение")],
        [KeyboardButton(text="📚 История решений")],
        [KeyboardButton(text="ℹ️ О боте")],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_outcome_score_keyboard() -> InlineKeyboardMarkup:
    """Get outcome score keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(text="😢 Намного хуже", callback_data="score:-2"),
            InlineKeyboardButton(text="😟 Хуже", callback_data="score:-1"),
        ],
        [
            InlineKeyboardButton(text="😐 Без изменений", callback_data="score:0"),
        ],
        [
            InlineKeyboardButton(text="🙂 Немного лучше", callback_data="score:1"),
            InlineKeyboardButton(text="😄 Намного лучше", callback_data="score:2"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_decision_list_keyboard(decisions: list) -> InlineKeyboardMarkup:
    """Get decision list keyboard"""
    status_emoji = {
        DecisionStatus.NEW: "🆕",
        DecisionStatus.DECIDED: "✅",
        DecisionStatus.COMPLETED: "🏁",
    }

    keyboard = []
    for decision in decisions:
        emoji = status_emoji.get(decision.status, "❓")
        # Truncate problem text to 50 chars
        text = f"{emoji} {decision.problem[:50]}"
        if len(decision.problem) > 50:
            text += "..."
        keyboard.append([InlineKeyboardButton(text=text, callback_data=f"decision:{decision.id}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_skip_keyboard() -> ReplyKeyboardMarkup:
    """Get skip keyboard"""
    keyboard = [[KeyboardButton(text="⏭️ Пропустить")]]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)


def get_confirmation_keyboard() -> ReplyKeyboardMarkup:
    """Get confirmation keyboard"""
    keyboard = [
        [KeyboardButton(text="✅ Да")],
        [KeyboardButton(text="✏️ Поменять решение")],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)
