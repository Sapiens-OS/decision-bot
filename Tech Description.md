# 📄 Техническое описание Sapiens OS (Telegram MVP)

## **1. Общая идея проекта**
Sapiens OS — это система, помогающая пользователю принимать осознанные решения (Decision Assistant). Она структурирует мышление, сохраняет историю решений и отслеживает их результаты через время.

---

## **2. Стек технологий**
*   **Язык:** Python 3.12+
*   **Telegram API:** `aiogram 3.x`
*   **База данных:** PostgreSQL
*   **ORM:** SQLAlchemy 2.0+ (Async)
*   **Миграции:** Alembic
*   **LLM API:** OpenAI (GPT-4o / GPT-4o-mini)
*   **Dependency Injection:** `python-dependency-injector`
*   **Фоновые задачи:** Celery + Redis (для follow-up уведомлений)
*   **Контейнеризация:** Docker + Docker Compose

---

## **3. Архитектура и структура папок**
Проект следует слоистой архитектуре, обеспечивающей прозрачность и легкость поддержки (на основе паттернов из `/public`):

```text
app/
├── bot/                # Интерфейс Telegram
│   ├── handlers/       # Обработчики команд (/start, /new, /history)
│   ├── use_cases/      # Бизнес-сценарии взаимодействия (диалоговая логика)
│   ├── keyboards/      # Меню и кнопки
│   └── states.py       # Состояния FSM
├── services/           # Бизнес-логика (не зависящая от бота)
│   ├── interfaces/     # Интерфейсы (ABC) для сервисов
│   ├── llm_service.py  # Реализация интеграции с OpenAI
│   └── decision_service.py # Реализация управления решениями
├── tasks/              # Фоновые задачи (Celery)
│   └── follow_up.py    # Отправка вопросов о результатах через 7/30/90 дней
├── infrastructure/     # Работа с внешними системами
│   ├── db/             # Подключение к БД
│   ├── models/         # SQLAlchemy модели (User, Decision, Outcome)
│   └── repositories/   # Реализация CRUD операций
│       └── interfaces/ # Интерфейсы (ABC) для репозиториев
├── core/               # Ядро
│   ├── container.py    # Dependency Injection Container
│   ├── config.py       # Конфигурация через env
│   └── logger.py       # Конфигурация логирования
└── main.py             # Точка входа (инициализация контейнера и запуск)
```

---

## **4. Взаимодействие сервисов**

1.  **Создание решения (User Journey):**
    `User` → `Bot Handler` (команда `/new`) → `Use Case` (пошаговый опрос) → `LLM Service Interface` → `OpenAI Implementation` → `Repository Interface` → `PostgreSQL Implementation`.
2.  **Follow-up (отложенный контроль):**
    `Celery Beat` (планировщик) → `Follow-up Task` → `Repository` (поиск решений, требующих оценки) → `Bot` (отправка сообщения пользователю через Telegram API).
3.  **История:**
    `User` → `Bot Handler` (`/history`) → `Repository` (выборка данных) → `Bot` (отрисовка списка).

---

## **5. Схема данных (Основные сущности)**

*   **Users:** `id`, `telegram_id`, `username`, `created_at`.
*   **Decisions:** `id`, `user_id`, `problem`, `analysis` (структурированный ответ от AI), `selected_option`, `status` (new/decided/completed), `created_at`.
*   **Outcomes:** `id`, `decision_id`, `feedback`, `score` (-2 to +2), `created_at`.

---

## **6. Принципы реализации (Упрощение и Прозрачность)**
*   **Разделение ответственности:** Логика "о чем говорить" вынесена в `use_cases`, логика "как говорить" — в `handlers`, логика "где хранить" — в `repositories`.
*   **Асинхронность:** Все операции ввода-вывода (БД, API Telegram, API OpenAI) выполняются асинхронно для высокой отзывчивости бота.
*   **Масштабируемость:** Добавление новых типов анализа или уведомлений не затрагивает основной код бота, а добавляется в `services` или `tasks`.
*   **Скрытие реализации:** Использование `dependency-injector` позволяет коду зависеть от абстрактных интерфейсов, а не от конкретных классов. Это облегчает тестирование (через моки) и замену компонентов (например, переход с OpenAI на Anthropic или локальную модель).
