from app.infrastructure.utils.create_postgresql_database import create_if_not_exist_database
from app.core.config import config as app_config


if __name__ == "__main__":
    # init_db()
    create_if_not_exist_database(app_config.database_uri)
    print("Таблицы созданы!")
