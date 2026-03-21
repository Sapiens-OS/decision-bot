from dependency_injector import containers, providers
from app.core.config import config
from app.infrastructure.db.database import Database


class Container(containers.DeclarativeContainer):
    """Dependency Injection Container"""

    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.bot.handlers.start_handler",
            "app.bot.handlers.new_decision_handler",
            "app.bot.handlers.history_handler",
            "app.bot.use_cases.new_decision_use_case",
            "app.tasks.follow_up",
        ]
    )

    # Config
    config_provider = providers.Singleton(lambda: config)

    # Database
    db = providers.Singleton(
        Database,
        db_url=config.database_uri,
    )

    # Repositories
    from app.infrastructure.repositories.user_repository import UserRepository
    from app.infrastructure.repositories.decision_repository import DecisionRepository
    from app.infrastructure.repositories.outcome_repository import OutcomeRepository

    user_repository = providers.Factory(
        UserRepository,
        session_factory=db.provided.session_factory,
    )

    decision_repository = providers.Factory(
        DecisionRepository,
        session_factory=db.provided.session_factory,
    )

    outcome_repository = providers.Factory(
        OutcomeRepository,
        session_factory=db.provided.session_factory,
    )

    # Services
    from app.services.llm_service import OpenAILLMService
    from app.services.decision_service import DecisionService

    llm_service = providers.Factory(
        OpenAILLMService,
        api_key=config.openai_api_key,
        model=config.openai_model,
    )

    decision_service = providers.Factory(
        DecisionService,
        decision_repository=decision_repository,
        outcome_repository=outcome_repository,
        llm_service=llm_service,
    )
