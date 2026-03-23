import asyncio
from dependency_injector.wiring import inject, Provide
from app.services.interfaces.i_decision_service import IDecisionService
from app.tasks.celery_app import celery_app
from app.core.logger import logger
from app.core.config import config
from app.bot.init import bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.core.container import Container


@celery_app.task(name="app.tasks.follow_up.check_follow_up_task")
@inject
def check_follow_up_task(
    decision_service: IDecisionService = Provide[Container.decision_service],
):
    """Check decisions that need follow-up (Celery task)"""
    asyncio.run(check_follow_up(decision_service))


async def check_follow_up(decision_service: IDecisionService):
    """Check decisions that need follow-up"""
    logger.info("Checking decisions for follow-up...")

    # Check each interval
    intervals = config.follow_up_intervals or []
    for days in intervals:
        logger.info(f"Checking decisions from {days} days ago...")

        # Get decisions for follow-up
        decisions = await decision_service.get_decisions_for_follow_up(days)

        logger.info(f"Found {len(decisions)} decisions for {days} days follow-up")

        # Send follow-up messages
        for decision in decisions:
            try:
                await send_follow_up_message(decision, days)
            except Exception as e:
                logger.error(f"Error sending follow-up for decision {decision.id}: {e}")

    logger.info("Follow-up check completed")


async def send_follow_up_message(decision, days: int):
    """Send follow-up message to user"""
    # Get user telegram_id
    user = decision.user

    # Prepare message
    text = (
        f"🔔 Прошло {days} дней с момента вашего решения!\n\n"
        f"📌 Проблема:\n{decision.problem}\n\n"
        f"🎯 Ваш выбор:\n{decision.selected_option}\n\n"
        f"Как это сработало?"
    )

    # Create keyboard
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📝 Поделиться результатом", callback_data=f"outcome:{decision.id}")]
        ]
    )

    # Send message
    await bot.send_message(
        chat_id=user.telegram_id,
        text=text,
        reply_markup=keyboard,
    )

    logger.info(f"Follow-up sent to user {user.telegram_id} for decision {decision.id}")
