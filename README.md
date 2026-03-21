# Sapiens OS - Decision Assistant Bot

Decision Assistant telegram bot that helps users make conscious decisions.

# Создать .env файл
`cp .env.example .env`

# Запустить через Docker
`docker-compose up -d`

# Или локально
```
poetry install
docker-compose up -d postgres redis
poetry run python -m app.main
poetry run celery -A app.tasks.celery_app worker --loglevel=info
poetry run celery -A app.tasks.celery_app beat --loglevel=info
```
## Features

- 📝 Create and analyze decisions with AI
- 📚 Store decision history
- 🔔 Follow-up notifications (7, 30, 90 days)
- 🎯 Track decision outcomes
- 🧠 Structured decision analysis

## Tech Stack

- Python 3.12+
- aiogram 3.x (Telegram Bot API)
- PostgreSQL (Database)
- SQLAlchemy 2.0+ (Async ORM)
- OpenAI API (GPT-4o-mini)
- Celery + Redis (Background tasks)
- Docker + Docker Compose

## Architecture

```
app/
├── bot/                # Telegram interface
│   ├── handlers/       # Command handlers
│   ├── use_cases/      # Business scenarios
│   ├── keyboards/      # Keyboards and buttons
│   └── states.py       # FSM states
├── services/           # Business logic
│   ├── llm_service.py  # OpenAI integration
│   └── decision_service.py # Decision management
├── tasks/              # Celery tasks
│   └── follow_up.py    # Follow-up notifications
├── infrastructure/     # External systems
│   ├── db/             # Database connection
│   ├── models/         # SQLAlchemy models
│   └── repositories/   # CRUD operations
├── core/               # Core
│   ├── container.py    # DI Container
│   ├── config.py       # Configuration
│   └── logger.py       # Logging
└── main.py             # Entry point
```

### Кто за что отвечает

**bot**
Телеграм бот, роутеры, юз-кейсы для команд бота, бизнес-логика формирования сообщений

**celery**
Крон-задачи и периодические задания (follow-up уведомления)

**services**
Интерфейсы и бизнес-логика работы с сущностями. Работает независимо от клиента (бот/REST/Celery)

**infrastructure**
Взаимодействие с БД, модели, CRUD операции

## Setup

### 1. Clone repository

```bash
git clone <repository-url>
cd decision-bot
```

### 2. Create .env file

```bash
cp .env.example .env
```

Edit `.env` and set your credentials:
- `BOT_TOKEN` - Telegram bot token from @BotFather
- `OPENAI_API_KEY` - OpenAI API key
- `DATABASE_URI` - PostgreSQL connection string

### 3. Run with Docker Compose

```bash
docker-compose build
docker-compose up -d
```

This will start:
- PostgreSQL database
- Redis
- Bot (Telegram bot)
- Celery worker (background tasks)
- Celery beat (scheduler)

### 4. Check logs

```bash
docker-compose logs -f bot
```

## Local Development

### 1. Install dependencies

```bash
poetry install
```

### 2. Start PostgreSQL and Redis

```bash
docker-compose up -d postgres redis
```

### 3. Run migrations

```bash
poetry run alembic upgrade head
```

### 4. Run bot

```bash
export PYTHONPATH=$(pwd)
poetry run python -m app.main
```

### 5. Run Celery worker

```bash
poetry run celery -A app.tasks.celery_app worker --loglevel=info
```

### 6. Run Celery beat

```bash
poetry run celery -A app.tasks.celery_app beat --loglevel=info
```

## Usage

### Commands

- `/start` - Start bot
- `/new` - Create new decision
- `/history` - View decision history

### Creating a decision

1. Send `/new` command
2. Describe your situation
3. Provide additional context (optional)
4. Review AI analysis
5. Select your option
6. Decision is saved

### Follow-up

Bot will send follow-up messages after 7, 30, and 90 days asking about the outcome of your decision.

## Celery Commands

```bash
# Run worker
poetry run celery -A app.tasks.celery_app worker --loglevel=info

# Run worker with beat
poetry run celery -A app.tasks.celery_app worker --beat --loglevel=info

# Purge all tasks
poetry run celery -A app.tasks.celery_app purge

# Inspect active tasks
celery -A app.tasks.celery_app inspect active

# Inspect reserved tasks
celery -A app.tasks.celery_app inspect reserved
```

## Database Migrations

```bash
# Create initial migration
poetry run alembic revision --autogenerate -m "Initial"

# Create migration
poetry run alembic revision --autogenerate -m "Description"

# Apply migrations
poetry run alembic upgrade head

# Rollback migration
poetry run alembic downgrade -1
```

## Testing

```bash
poetry run pytest
```

## Linters

```bash
poetry run black ./
poetry run flake8
poetry run mypy --ignore-missing-import --explicit-package-bases --check-untyped-defs ./
```

## PyCharm Setup

```bash
poetry env info --path
# or
poetry config virtualenvs.in-project true
```

1. Open `PyCharm`
2. Go to **File** → **Settings** (or **PyCharm** → **Preferences** on macOS)
3. Go to **Project** → **Python Interpreter**
4. Click gear icon and select **Add...**
5. Select **Existing environment**
6. Specify path to interpreter from poetry env

## Webhook Setup (for production)

```bash
ngrok http 8443
# or with custom domain
ngrok http --url=your-domain.ngrok-free.app 8443
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URI | PostgreSQL connection string | postgresql+asyncpg://user:password@localhost:5432/sapiens_os |
| BOT_TOKEN | Telegram bot token | - |
| BOT_WEBHOOK_URL | Webhook URL (optional) | - |
| BOT_WEBHOOK_PORT | Webhook port | 8443 |
| REDIS_URL | Redis connection string | redis://localhost:6379/0 |
| OPENAI_API_KEY | OpenAI API key | - |
| OPENAI_MODEL | OpenAI model | gpt-4o-mini |
| CELERY_BROKER_URL | Celery broker URL | redis://localhost:6379/1 |
| CELERY_RESULT_BACKEND | Celery result backend | redis://localhost:6379/2 |

## License

MIT
