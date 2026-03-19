import os
import pytest
import uuid
import pytest_asyncio

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import ProgrammingError
from alembic.config import Config
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from alembic import command
from public.app.infrastructure import BaseModel
from public.app.infrastructure.utils.create_postgresql_database import create_if_not_exist_database
from dotenv import load_dotenv


os.environ["TEST_ENV"] = "true"
assert os.getenv("TEST_ENV") == "true"
dotenv_path = os.path.join(os.path.dirname(__file__), ".env.test")
load_dotenv(dotenv_path)

current_dir = os.path.dirname(os.path.abspath(__file__))
alembic_ini_path = os.path.join(current_dir, "alembic.ini")
current_dir = os.path.dirname(os.path.abspath(__file__))
migrations_path = os.path.join(current_dir, "public/migrations")


def create_test_database(database_url):
    create_if_not_exist_database(database_url)


def drop_test_database(database_url):
    """Удаляем тестовую базу данных."""
    engine = create_engine(database_url.rsplit("/", 1)[0] + "/postgres", isolation_level="AUTOCOMMIT")
    with engine.connect() as connection:
        # Принудительно завершаем все соединения с базой тестов
        connection.execute(text("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='test_monitor'"))
        try:
            connection.execute(text("DROP DATABASE test_monitor"))
        except ProgrammingError:
            # Если база уже удалена или возникла иная ошибка, игнорируем её
            pass


@pytest_asyncio.fixture(scope="function")
async def test_db(sinc_test_db):
    """Async fixture for database setup."""
    # Convert sync URL to async URL
    _, _, sync_database_url = sinc_test_db
    async_database_url = sync_database_url.replace("postgresql+psycopg2", "postgresql+asyncpg")

    async_engine = create_async_engine(async_database_url, pool_pre_ping=True, pool_recycle=3600)
    AsyncSession = async_sessionmaker(
        bind=async_engine,
        expire_on_commit=False,
        # class_=AsyncSession
    )

    try:
        yield AsyncSession, async_engine
    finally:
        await async_engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def session(test_db):
    AsyncSession, async_engine = test_db
    async_session = AsyncSession()

    try:
        yield async_session
        await async_session.commit()
    except Exception:
        await async_session.rollback()
        raise
    finally:
        await async_session.close()
        await async_engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def storage_factory(session):
    def _create_storage(storage_class):
        storage = storage_class()

        def session_factory(**kwargs):
            if "bind" in kwargs:
                return session
            return session

        storage._BaseStorage__Session = session_factory
        return storage

    try:
        yield _create_storage
    finally:
        pass


@pytest.fixture(scope="session")
def sinc_test_db():
    """Фикстура для настройки базы данных на уровне всего сеанса тестов."""
    database_url = "postgresql+psycopg2://gorod:123qwe@localhost:5432/test_monitor"

    # Создаем базу, если еще не существует.
    create_test_database(database_url)

    # Применение миграций
    alembic_cfg = Config(alembic_ini_path)
    alembic_cfg.set_main_option("sqlalchemy.url", database_url)
    alembic_cfg.set_main_option("script_location", migrations_path)  # при необходимости скорректируйте путь
    command.upgrade(alembic_cfg, "head")

    # Настраиваем подключение и создаем схемы
    engine = create_engine(database_url)
    BaseModel.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    yield Session, engine, database_url  # возвращаем сессию и двигатель для тестов

    # Очистка после завершения всех тестов
    engine.dispose()
    drop_test_database(database_url)


@pytest.fixture(scope="function")
def sinc_session(sinc_test_db):
    """Фикстура для отдельной сессии в каждом тесте."""
    Session, _, _ = sinc_test_db
    session = Session()
    # Применяем все изменения к базе
    connection = session.bind.connect()
    transaction = connection.begin()

    yield session  # Откатываем транзакцию только вручную после yield

    transaction.rollback()
    connection.close()
    session.close()

    # yield session
    # session.rollback()
    # session.close()


@pytest.fixture(scope="function")
def sinc_storage_factory(sinc_session):
    def _create_storage(storage_class):
        storage = storage_class()
        storage.engine = sinc_session.bind  # Привязываем движок базы из сессии
        storage.Session = lambda: sinc_session  # Привязываем сессию
        return storage

    return _create_storage


@pytest.fixture(scope="function")
def owner_id():
    return uuid.uuid4()
