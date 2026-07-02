from __future__ import annotations

from config.settings import get_settings
from database.init_db import initialize_database
from services.seed_admin import bootstrap_admin_user
from utils.logging import configure_logging


def main() -> None:
    """Application entrypoint for the Blackcrest Recruiting AI platform."""
    settings = get_settings()
    logger = configure_logging(log_level=settings.log_level)
    initialize_database(settings.database_url)
    bootstrap_admin_user()

    logger.info("Starting %s", settings.app_name)
    logger.info("Environment: %s", settings.app_env)
    logger.info("Debug mode: %s", settings.debug)


if __name__ == "__main__":
    main()
