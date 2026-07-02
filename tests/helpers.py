from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from database.connection import normalize_database_url
from database.init_db import initialize_database


def build_test_session(database_path: Path) -> Session:
    """Initialize a SQLite test database and return an open SQLAlchemy session."""
    initialize_database(str(database_path))
    engine = create_engine(normalize_database_url(str(database_path)), future=True)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    return session_factory()
