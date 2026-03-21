import redis.asyncio as redis
from aiogram import Bot
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram.fsm.storage.memory import MemoryStorage

from app.core.config import config
from app.core.logger import logger


def create_bot() -> Bot:
    """Create bot instance"""
    return Bot(token=config.bot_token)


def create_storage():
    """Create storage for FSM"""
    try:
        storage = RedisStorage.from_url(
            config.redis_url,
            key_builder=DefaultKeyBuilder(with_bot_id=True),
        )
        logger.info("Using Redis storage for FSM")
        return storage
    except Exception as e:
        logger.warning(f"Redis unavailable: {e}. Using memory storage for FSM")
        return MemoryStorage()


bot = create_bot()
storage = create_storage()
