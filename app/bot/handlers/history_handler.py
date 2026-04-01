from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from dependency_injector.wiring import inject, Provide

from app.bot.keyboards.main_keyboard import get_main_menu, get_decision_list_keyboard
from app.bot.interfaces.i_decision_service import IDecisionService
from app.services.dto import DecisionStatus
from app.infrastructure.repositories.user_repository import UserRepository
from app.core.container import Container
from app.core.logger import logger
from app.infrastructure.utils.text_utils import split_text

router = Router()


@router.message(Command("history"))
@router.message(F.text == "📚 История решений")
@inject
async def cmd_history(
    message: Message,
    user_repository: UserRepository = Provide[Container.user_repository],
    decision_service: IDecisionService = Provide[Container.decision_service],
):
    """Handle /history command"""
    if not message.from_user:
        return

    # Get user
    user = await user_repository.get_by_telegram_id(message.from_user.id)

    if not user:
        await message.answer(
            "У вас пока нет сохраненных решений.\n\n" "Создайте первое решение с помощью команды /new",
            reply_markup=get_main_menu(),
        )
        return

    # Get user decisions
    decisions = await decision_service.get_user_decisions(user.id, limit=10)

    if not decisions:
        await message.answer(
            "У вас пока нет сохраненных решений.\n\n" "Создайте первое решение с помощью команды /new",
            reply_markup=get_main_menu(),
        )
        return

    await message.answer(
        f"📚 Ваши решения (всего: {len(decisions)}):\n\n" "Выберите решение, чтобы посмотреть подробности:",
        reply_markup=get_decision_list_keyboard(decisions),
    )


@router.callback_query(F.data.startswith("decision:"))
@inject
async def show_decision(
    callback: CallbackQuery,
    decision_service: IDecisionService = Provide[Container.decision_service],
):
    """Show decision details"""
    if not callback.data or not callback.message:
        return

    decision_id = int(callback.data.split(":")[1])

    try:
        decision = await decision_service.get_decision(decision_id)

        if not decision:
            await callback.answer("Решение не найдено", show_alert=True)
            return

        # Format decision details
        status_emoji = {
            DecisionStatus.NEW: "🆕",
            DecisionStatus.DECIDED: "✅",
            DecisionStatus.COMPLETED: "🏁",
        }

        text = (
            f"{status_emoji.get(decision.status, '❓')} Решение #{decision.id}\n\n"
            f"📅 Дата: {decision.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
            f"📌 Проблема:\n{decision.problem}\n\n"
        )

        if decision.analysis:
            text += f"🔍 Анализ:\n{decision.analysis}\n\n"

        if decision.selected_option:
            text += f"🎯 Выбранный вариант:\n{decision.selected_option}\n\n"

        chunks = split_text(text)
        for i, chunk in enumerate(chunks):
            await callback.message.answer(
                chunk,
                reply_markup=get_main_menu() if i == len(chunks) - 1 else None,
            )
        await callback.answer()

    except Exception as e:
        logger.error(f"Error showing decision: {e}")
        await callback.answer("Ошибка при загрузке решения", show_alert=True)
