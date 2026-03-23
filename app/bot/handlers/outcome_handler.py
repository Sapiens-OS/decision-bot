from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from dependency_injector.wiring import inject, Provide

from app.bot.states import OutcomeStates
from app.bot.keyboards.main_keyboard import get_main_menu, get_outcome_score_keyboard
from app.services.interfaces.i_decision_service import IDecisionService
from app.core.container import Container
from app.core.logger import logger

router = Router()


@router.callback_query(F.data.startswith("outcome:"))
async def start_outcome_feedback(callback: CallbackQuery, state: FSMContext):
    """Start outcome feedback process"""
    decision_id = int(callback.data.split(":")[1])

    await state.update_data(decision_id=decision_id)
    await callback.message.answer(
        "Расскажите, как сработало ваше решение?\n\n" "Что произошло? Что изменилось?",
        reply_markup=get_main_menu(),
    )
    await state.set_state(OutcomeStates.waiting_for_feedback)
    await callback.answer()


@router.message(OutcomeStates.waiting_for_feedback)
async def process_outcome_feedback(message: Message, state: FSMContext):
    """Process outcome feedback"""
    feedback = message.text
    await state.update_data(feedback=feedback)

    await message.answer(
        "Оцените результат вашего решения:",
        reply_markup=get_outcome_score_keyboard(),
    )
    await state.set_state(OutcomeStates.waiting_for_score)


@router.callback_query(F.data.startswith("score:"), OutcomeStates.waiting_for_score)
@inject
async def process_outcome_score(
    callback: CallbackQuery,
    state: FSMContext,
    decision_service: IDecisionService = Provide[Container.decision_service],
):
    """Process outcome score"""
    score = int(callback.data.split(":")[1])
    data = await state.get_data()
    decision_id = data["decision_id"]
    feedback = data["feedback"]

    try:
        # Save outcome
        await decision_service.add_outcome(
            decision_id=decision_id,
            feedback=feedback,
            score=score,
        )

        await callback.message.answer(
            "✅ Спасибо за обратную связь!\n\n" "Ваш опыт помогает делать решения более осознанными.",
            reply_markup=get_main_menu(),
        )

    except Exception as e:
        logger.error(f"Error saving outcome: {e}")
        await callback.message.answer(
            "❌ Произошла ошибка при сохранении. Попробуйте позже.",
            reply_markup=get_main_menu(),
        )

    await state.clear()
    await callback.answer()
