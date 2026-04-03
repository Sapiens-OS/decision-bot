from dataclasses import dataclass
from app.config import (
    DATABASE_URI,
    BOT_TOKEN,
    WEBHOOK_URL,
    WEBHOOK_PORT,
    REDIS_URL,
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    OPENAI_MODEL,
    CELERY_BROKER_URL,
    CELERY_RESULT_BACKEND,
    FOLLOW_UP_INTERVALS,
    USE_CORE_SERVICES,
)


@dataclass
class Config:
    """Application configuration"""

    # Database
    database_uri: str = DATABASE_URI

    # Telegram
    bot_token: str = BOT_TOKEN
    webhook_url: str | None = WEBHOOK_URL
    webhook_port: int = WEBHOOK_PORT

    # Redis
    redis_url: str = REDIS_URL

    # OpenAI
    use_core_services: bool = USE_CORE_SERVICES
    openai_base_url: str = OPENAI_BASE_URL
    openai_api_key: str = OPENAI_API_KEY
    openai_model: str = OPENAI_MODEL

    # Celery
    celery_broker_url: str = CELERY_BROKER_URL
    celery_result_backend: str = CELERY_RESULT_BACKEND

    # Follow-up
    follow_up_intervals: list[int] | None = None

    def __post_init__(self):
        if self.follow_up_intervals is None:
            self.follow_up_intervals = FOLLOW_UP_INTERVALS


config = Config()
