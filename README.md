### Кто за что отвечает
**bot**   
телграм бот, роуты, юз кейсы для команд бота
бизнес логика для формирования сообщений бота

**celery**   
крон команды и переодические задания

**services**  
Интерфейс для сохранения/получения включащий логику сохранения/получения    
Бизнес логика работы с сущностями   
Работает независимо от того кто его испольузет - бот/рест/селери

**db**   
взаимодействие с БД   
Описание моделей  
крад операции

### Запуск приложения
```
poetry run celery -A app.celery_app worker --loglevel=info
poetry run celery -A app.celery_app worker --beat --loglevel=info
poetry run celery -A app.celery_app purge


poetry run celery -A app.monitor call check_site --args='[1]'


celery -A <имя_вашего_приложения> inspect active


celery -A <имя_вашего_приложения> inspect reserved


poetry run   playwright install

export PYTHONPATH=$(pwd)
poetry run python app/bot/main.py
```



### Запуск с докером
```bash
# (С докером)
cd /Users/dimapanov/git/my/monitor/docker
docker-compose build
docker-compose up -d
docker-compose -f docker-monitor/docker-compose.yml build NAME
docker-compose -f docker-monitor/docker-compose.yml up -d NAME


docker compose -f /opt/monitor/docker-monitor/docker-compose.yml build
docker compose -f /opt/monitor/docker-monitor/docker-compose.yml up -d

docker compose -f /opt/monitor/docker-monitor/docker-compose.yml build NAME
docker compose -f /opt/monitor/docker-monitor/docker-compose.yml up -d NAME

docker compose -f /opt/monitor/docker-monitor/docker-compose.yml build celery_worker
docker compose -f /opt/monitor/docker-monitor/docker-compose.yml up -d celery_worker


docker-compose -f docker-monitor/celery-compose.yml build
docker-compose -f docker-monitor/celery-compose.yml up -d

```
### Настройка пичарм
```bash
# (С докером)
   poetry env info --path
   или
poetry config virtualenvs.in-project true
<папка проекта>/.venv/bin/python



1. Откройте `PyCharm`.
2. Перейдите в меню **File** → **Settings** (или **PyCharm** → **Preferences** на macOS).
3. Перейдите в раздел **Project** → **Python Interpreter**.
4. Нажмите значок шестерёнки рядом со списком интерпретаторов и выберите **Add...**.
5. В открывшемся окне выберите **Existing environment**.
6. Укажите путь к интерпретатору внутри виртуального окружения из шага 2, например:



   poetry show
```

### Запуск бота
```
ngrok http 8443
ngrok http --url=anteater-clear-blindly.ngrok-free.app 8443
```

### Запуск тестов
```
poetry run pytest
```

### Линтеры 
```
poetry run black ./
poetry run flake8
poetry run mypy --ignore-missing-import --explicit-package-bases --check-untyped-defs ./
```


### Миграции ДБ
```
poetry run alembic revision --autogenerate -m "Initial"
poetry run alembic revision --autogenerate -m "Описание изменений"
poetry run alembic upgrade head
poetry run alembic downgrade -1

```

   

