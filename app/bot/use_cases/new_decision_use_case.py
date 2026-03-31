from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from dependency_injector.wiring import inject, Provide

from app.bot.states import NewDecisionStates
from app.bot.keyboards.main_keyboard import get_main_menu, get_skip_keyboard
from app.bot.interfaces.i_decision_service import IDecisionService
from app.core.container import Container
from app.core.logger import logger
from app.services.interfaces.i_decision_repository import IDecisionRepository
from app.services.interfaces.i_user_repository import IUserRepository

router = Router()


@router.message(NewDecisionStates.waiting_for_problem)
@inject
async def process_problem(
    message: Message,
    state: FSMContext,
    user_repository: IUserRepository = Provide[Container.user_repository],
    decision_repository: IDecisionRepository = Provide[Container.decision_repository],
):
    """Process problem description"""
    if not message.from_user:
        return

    # Get or create user
    user = await user_repository.get_or_create(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
    )

    # Check question limit
    count = await decision_repository.count_user_decisions(user.id)
    if count >= user.max_questions:
        await message.answer("достигнут лимит сообщений", reply_markup=get_main_menu())
        await state.clear()
        return

    problem = message.text or ""

    # Save problem to state
    await state.update_data(problem=problem, user_id=user.id)

    # Ask for context
    await message.answer(
        "Что для вас важно в этой ситуации? Есть ли дополнительный контекст?\n\n" "Вы можете пропустить этот шаг.",
        reply_markup=get_skip_keyboard(),
    )
    await state.set_state(NewDecisionStates.waiting_for_context)


@router.message(NewDecisionStates.waiting_for_context)
@inject
async def process_context(
    message: Message,
    state: FSMContext,
    decision_service: IDecisionService = Provide[Container.decision_service],
):
    """Process context and create decision"""
    data = await state.get_data()
    problem = data["problem"]
    user_id = data["user_id"]

    # Get context
    context: dict[str, str] | None = None
    if message.text != "⏭️ Пропустить":
        context = {"additional_info": message.text or ""}

    # Show loading message
    loading_msg = await message.answer("🤔 Анализирую ситуацию...", reply_markup=get_main_menu())

    try:
        # Create decision with AI analysis
        decision = await decision_service.create_decision(
            user_id=user_id,
            problem=problem,
            context=context,
        )

        # Delete loading message
        await loading_msg.delete()

        # Send analysis
        await message.answer(
            f"✅ Вот мой анализ:\n\n{decision.analysis}\n\n"
            f"Какой вариант вы выбираете? Напишите его или опишите свой:",
            reply_markup=get_main_menu(),
            parse_mode="Markdown",
        )

        # Save decision ID to state
        await state.update_data(decision_id=decision.id)
        await state.set_state(NewDecisionStates.waiting_for_selection)

    except Exception as e:
        logger.error(f"Error creating decision: {e}")
        await loading_msg.delete()
        await message.answer(
            "❌ Произошла ошибка при анализе. Попробуйте позже.",
            reply_markup=get_main_menu(),
        )
        await state.clear()


@router.message(NewDecisionStates.waiting_for_selection)
@inject
async def process_selection(
    message: Message,
    state: FSMContext,
    decision_service: IDecisionService = Provide[Container.decision_service],
):
    """Process selected option"""
    data = await state.get_data()
    decision_id = data["decision_id"]
    selected_option = message.text

    try:
        # Update decision with selected option
        await decision_service.select_option(decision_id, message.text or "")

        await message.answer(
            f"✅ Отлично! Ваше решение сохранено:\n\n"
            f"🎯 {selected_option}\n\n"
            f"Я напомню вам об этом решении через 7, 30 и 90 дней, "
            f"чтобы понять, как всё сработало.",
            reply_markup=get_main_menu(),
            parse_mode="Markdown",
        )

    except Exception as e:
        logger.error(f"Error saving selected option: {e}")
        await message.answer(
            "❌ Произошла ошибка при сохранении. Попробуйте позже.",
            reply_markup=get_main_menu(),
        )

    await state.clear()
