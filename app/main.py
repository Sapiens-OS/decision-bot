import asyncio
from aiogram import Dispatcher, Bot
from aiohttp import web
from aiohttp.web import middleware

from app.core.config import config
from app.core.logger import logger
from app.core.container import Container
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiohttp.web_middlewares import normalize_path_middleware

from app.bot.init import bot, storage
from app.bot.error_handler import ErrorHandlerMiddleware

# Import handlers
from app.bot.handlers import start_handler, new_decision_handler, history_handler, outcome_handler
from app.bot.use_cases import new_decision_use_case


async def set_bot_commands(bot: Bot):
    """Set bot commands"""
    from aiogram.types import BotCommand

    commands = [
        BotCommand(command="start", description="Начать работу"),
        BotCommand(command="new", description="Создать новое решение"),
        BotCommand(command="history", description="История решений"),
    ]
    await bot.set_my_commands(commands)
    logger.info("Bot commands set")


async def on_startup(_: Dispatcher, bot: Bot):
    """On startup handler"""
    if config.webhook_url is not None:
        response = await bot.set_webhook(config.webhook_url)
        logger.info(f"Webhook set: {response}")


async def on_shutdown(_: Dispatcher, bot: Bot):
    """On shutdown handler"""
    await bot.delete_webhook()
    logger.info("Webhook deleted")


@middleware
async def log_requests_middleware(request, handler):
    """Log requests middleware"""
    response = await handler(request)
    if response.status != 200:
        logger.warning(f"Error on request: {request.method} {request.path} Response: {response.status}")
    return response


async def main():
    """Main function"""
    # Initialize container
    container = Container()
    container.wire(modules=[
        "app.bot.handlers.start_handler",
        "app.bot.handlers.new_decision_handler",
        "app.bot.handlers.history_handler",
        "app.bot.handlers.outcome_handler",
        "app.bot.use_cases.new_decision_use_case",
    ])

    # Initialize database
    db = container.db()
    await db.create_tables()

    # Delete webhook
    await bot.delete_webhook()

    # Create dispatcher
    dp = Dispatcher(storage=storage)

    # Include routers
    dp.include_router(start_handler.router)
    dp.include_router(new_decision_handler.router)
    dp.include_router(new_decision_use_case.router)
    dp.include_router(history_handler.router)
    dp.include_router(outcome_handler.router)

    # Add middleware
    dp.message.middleware(ErrorHandlerMiddleware())

    # Set bot commands
    await set_bot_commands(bot)

    logger.info("Bot started and waiting for messages...")

    try:
        if config.webhook_url:
            logger.info(f"Webhook mode enabled: {config.webhook_url}")
            app = web.Application(middlewares=[normalize_path_middleware()])
            app.middlewares.append(log_requests_middleware)

            SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
            await on_startup(dp, bot)

            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, host="0.0.0.0", port=config.webhook_port)
            logger.info(f"Starting aiohttp server on {site.name}")

            await site.start()
            logger.info("Webhook server started!")
            await asyncio.Event().wait()

        else:
            logger.info("Polling mode enabled")
            try:
                await dp.start_polling(bot)
            except Exception as e:
                logger.error(f"Error starting polling: {e}")

    finally:
        if config.webhook_url:
            await on_shutdown(dp, bot)

        await bot.session.close()
        logger.info("Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())
