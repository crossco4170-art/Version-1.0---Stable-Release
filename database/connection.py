from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from database.base import Base
from config.settings import get_settings


def normalize_database_url(database_url: str) -> str:
    """Convert a plain file path or existing URL into a valid SQLite URL."""
    if database_url.startswith("sqlite://"):
        return database_url

    path = Path(database_url)
    return f"sqlite:///{path.as_posix()}"


def get_engine(database_url: str | None = None) -> Engine:
    """Create a SQLAlchemy engine for the configured database URL."""
    resolved_url = database_url or get_settings().database_url
    return create_engine(normalize_database_url(resolved_url), future=True)


def get_session(database_url: str | None = None, ensure_schema: bool = False) -> Session:
    """Create a database session for the configured engine."""
    engine = get_engine(database_url)
    if ensure_schema:
        Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    return session_factory()
