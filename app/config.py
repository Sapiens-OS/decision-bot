from dotenv import load_dotenv
import os

load_dotenv()

# Database
DATABASE_URI = os.getenv("DATABASE_URI", "postgresql+asyncpg://user:password@localhost:5432/sapiens_os")

# Telegram Bot
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
WEBHOOK_URL = os.getenv("BOT_WEBHOOK_URL")
WEBHOOK_PORT = int(os.getenv("BOT_WEBHOOK_PORT", "8443"))

# Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Celery
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")

# Follow-up intervals (in days)
FOLLOW_UP_INTERVALS = [7, 30, 90]
