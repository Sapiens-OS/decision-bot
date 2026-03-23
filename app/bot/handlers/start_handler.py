from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from dependency_injector.wiring import inject, Provide

from app.bot.keyboards.main_keyboard import get_main_menu
from app.infrastructure.repositories.user_repository import UserRepository
from app.core.container import Container

router = Router()


@router.message(Command("start"))
@inject
async def cmd_start(
    message: Message,
    user_repository: UserRepository = Provide[Container.user_repository],
):
    """Handle /start command"""
    if not message.from_user:
        return

    # Get or create user
    await user_repository.get_or_create(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
    )

    await message.answer(
        "👋 Привет! Я — Decision Assistant в Sapiens OS.\n\n"
        "Я помогу вам принимать осознанные решения, структурировать мышление "
        "и отслеживать результаты ваших решений.\n\n"
        "Что я умею:\n"
        "📝 Помогать анализировать решения\n"
        "📚 Сохранять историю решений\n"
        "🔔 Напоминать о результатах через время\n\n"
        "Используйте команды:\n"
        "/new — создать новое решение\n"
        "/history — посмотреть историю решений\n\n"
        "Или используйте кнопки меню ниже.",
        reply_markup=get_main_menu(),
    )


@router.message(F.text == "ℹ️ О боте")
async def about_bot(message: Message):
    """About bot"""
    await message.answer(
        "🤖 Sapiens OS — Decision Assistant\n\n"
        "Это система, которая помогает принимать осознанные решения.\n\n"
        "Принципы работы:\n"
        "• Структурирование мышления\n"
        "• Анализ вариантов и последствий\n"
        "• Выявление когнитивных искажений\n"
        "• Отслеживание результатов\n\n"
        "Я не решаю за вас — я помогаю вам думать.",
        reply_markup=get_main_menu(),
    )
