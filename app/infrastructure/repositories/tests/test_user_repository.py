from sqlalchemy import func, select

from app.infrastructure.models.user import User


async def test_create_and_get_by_telegram_id_persists_user(user_repository):
    user = await user_repository.create(telegram_id=1001, username="alice")

    loaded = await user_repository.get_by_telegram_id(telegram_id=1001)

    assert loaded is not None
    assert loaded.id == user.id
    assert loaded.telegram_id == 1001
    assert loaded.username == "alice"


async def test_get_or_create_returns_existing_user_without_duplicates(user_repository, session_factory):
    first = await user_repository.get_or_create(telegram_id=2002, username="first")
    second = await user_repository.get_or_create(telegram_id=2002, username="second")

    assert second.id == first.id
    assert second.username == "first"

    async with session_factory() as session:
        users_count = await session.scalar(select(func.count(User.id)))

    assert users_count == 1
