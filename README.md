# Sapiens OS - Decision Assistant Bot

Decision Assistant telegram bot that helps users make conscious decisions.

## Описание (Features)

- 📝 Create and analyze decisions with AI
- 📚 Store decision history
- 🔔 Follow-up notifications (7, 30, 90 days)
- 🎯 Track decision outcomes
- 🧠 Structured decision analysis

### Architecture

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

#### Кто за что отвечает

**bot**
Телеграм бот, роутеры, юз-кейсы для команд бота, бизнес-логика формирования сообщений

**celery**
Крон-задачи и периодические задания (follow-up уведомления)

**services**
Интерфейсы и бизнес-логика работы с сущностями. Работает независимо от клиента (бот/REST/Celery)

**infrastructure**
Взаимодействие с БД, модели, CRUD операции

## Стек (Tech Stack)

- Python 3.12+
- aiogram 3.x (Telegram Bot API)
- PostgreSQL (Database)
- SQLAlchemy 2.0+ (Async ORM)
- OpenAI API (GPT-4o-mini)
- Celery + Redis (Background tasks)
- Docker + Docker Compose

## Как запускать (различные варианты)

### Подготовка
1. Clone repository:
```bash
git clone <repository-url>
cd decision-bot
```
2. Create `.env` file and set your credentials:
```bash
cp .env.example .env
```
- `BOT_TOKEN` - Telegram bot token from @BotFather
- `OPENAI_API_KEY` - OpenAI API key
- `DATABASE_URI` - PostgreSQL connection string

### 1. Через Docker (самый простой способ)
```bash
docker-compose build
docker-compose up -d
```
Это запустит: PostgreSQL, Redis, Bot, Celery worker и Celery beat.

### 2. Локально (Development)

#### Шаг 1: Установка зависимостей
```bash
poetry install
```

#### Шаг 2: Запуск базы данных и Redis
```bash
docker-compose up -d postgres redis
```

#### Шаг 3: Миграции
```bash
poetry run alembic upgrade head
```

#### Шаг 4: Запуск проекта (Bot)
```bash
export PYTHONPATH=$(pwd)
poetry run python -m app.main
```

#### Шаг 5: Запуск Celery
```bash
# Run worker
poetry run celery -A app.tasks.celery_app worker --loglevel=info

# Run worker with beat (or separate)
poetry run celery -A app.tasks.celery_app beat --loglevel=info

# Или запустить все вместе в одном процессе
poetry run celery -A app.tasks.celery_app worker --beat --loglevel=info
```

## Миграции (Alembic)
```bash
# Создать начальную миграцию
poetry run alembic revision --autogenerate -m "Initial"

# Создать новую миграцию после изменений в моделях
poetry run alembic revision --autogenerate -m "Description"

# Применить миграции
poetry run alembic upgrade head

# Откатить миграцию
poetry run alembic downgrade -1
```

## Тесты и линтеры

### Тесты
```bash
poetry run pytest
```

### Линтеры
```bash
# Black (formatting)
poetry run black ./

# Flake8 (style guide)
poetry run flake8

# Mypy (type checking)
poetry run mypy --ignore-missing-import --explicit-package-bases --check-untyped-defs ./
```

## Остальная информация

### Usage & Commands
- `/start` - Start bot
- `/new` - Create new decision
- `/history` - View decision history

**Создание решения:**
1. Отправьте `/new`.
2. Опишите ситуацию.
3. Добавьте контекст (опционально).
4. Ознакомьтесь с анализом AI.
5. Выберите вариант.
6. Решение сохранено.

**Follow-up:**
Бот отправит уведомления через 7, 30 и 90 дней, чтобы узнать результат принятого решения.

### PyCharm Setup
1. Получите путь к интерпретатору: `poetry env info --path`
2. В PyCharm: **File** → **Settings** → **Project** → **Python Interpreter**
3. Нажмите шестеренку → **Add...** → **Existing environment**
4. Укажите путь к интерпретатору из poetry.

### Webhook Setup (Production)
Для работы через webhook локально можно использовать ngrok:
```bash
ngrok http 8443
```

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URI | PostgreSQL connection string | postgresql+asyncpg://user:password@localhost:5432/sapiens_os |
| BOT_TOKEN | Telegram bot token | - |
| BOT_WEBHOOK_URL | Webhook URL (optional) | - |
| BOT_WEBHOOK_PORT | Webhook port | 8443 |
| REDIS_URL | Redis connection string | redis://localhost:6379/0 |
| OPENAI_BASE_URL | Optional OpenAI Base Url | - |
| OPENAI_API_KEY | OpenAI API key | - |
| OPENAI_MODEL | OpenAI model | gpt-4o-mini |
| CELERY_BROKER_URL | Celery broker URL | redis://localhost:6379/1 |
| CELERY_RESULT_BACKEND | Celery result backend | redis://localhost:6379/2 |

### License
Apache License Version 2.0
