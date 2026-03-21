from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Dict, Any, Awaitable
from app.core.logger import logger


class ErrorHandlerMiddleware(BaseMiddleware):
    """Middleware for handling errors"""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception as e:
            logger.error(f"Error handling update: {e}", exc_info=True)
            if "message" in data:
                message = data["message"]
                await message.reply("Произошла ошибка. Попробуйте позже!")
            raise
