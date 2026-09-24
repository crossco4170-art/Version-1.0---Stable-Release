from __future__ import annotations

from importlib import import_module

from sqlalchemy.engine import Engine

from config.settings import get_settings
from database.base import Base
from database.connection import normalize_database_url
from database.schema_upgrade import upgrade_sqlite_schema


MODEL_MODULES: tuple[str, ...] = (
    "activity_log",
    "admin_user",
    "applicant",
    "client",
    "hiring_status",
    "interview",
    "job_order",
    "organization",
    "resume_evaluation",
)


def _register_model_metadata() -> None:
    """Import model modules so SQLAlchemy metadata includes every mapped table."""
    for module_name in MODEL_MODULES:
        import_module(f"models.{module_name}")


def initialize_database(database_url: str | None = None) -> Engine:
    """Create the SQLite database and all tables defined by registered models."""
    from sqlalchemy import create_engine

    _register_model_metadata()

    settings = get_settings(validate_required=False)
    resolved_url = database_url or settings.database_url
    engine = create_engine(normalize_database_url(resolved_url), future=True)
    Base.metadata.bind = engine
    Base.metadata.create_all(bind=engine)
    upgrade_sqlite_schema(engine)
    return engine
