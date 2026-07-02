from pathlib import Path

from sqlalchemy import inspect

from database.base import Base
from database.init_db import initialize_database


def test_sqlite_schema_creates_expected_tables(tmp_path: Path) -> None:
    database_path = tmp_path / "test_blackcrest.db"
    initialize_database(str(database_path))

    inspector = inspect(Base.metadata.bind)
    tables = inspector.get_table_names()

    expected_tables = {
        "applicants",
        "clients",
        "job_orders",
        "interviews",
        "hiring_statuses",
        "activity_logs",
    }

    assert expected_tables.issubset(set(tables))
