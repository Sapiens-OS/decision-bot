from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.bot.states import NewDecisionStates
from app.bot.keyboards.main_keyboard import get_main_menu

router = Router()


@router.message(Command("new"))
@router.message(F.text == "📝 Новое решение")
async def cmd_new_decision(message: Message, state: FSMContext):
    """Handle /new command"""
    await message.answer(
        "📝 Создание нового решения\n\n"
        "Опишите ситуацию, в которой вам нужно принять решение.\n\n"
        "Чем подробнее, тем лучше я смогу помочь.",
        reply_markup=get_main_menu(),
    )
    await state.set_state(NewDecisionStates.waiting_for_problem)
