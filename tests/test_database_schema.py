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
	    "organizations",
	    "admin_users",
        "applicants",
        "clients",
        "job_orders",
        "interviews",
        "hiring_statuses",
        "activity_logs",
	    "resume_evaluations",
    }

    assert expected_tables.issubset(set(tables))


def test_sqlite_schema_creates_expected_core_foreign_keys(tmp_path: Path) -> None:
	database_path = tmp_path / "test_blackcrest_fk.db"
	initialize_database(str(database_path))

	inspector = inspect(Base.metadata.bind)
	client_fks = inspector.get_foreign_keys("clients")
	job_order_fks = inspector.get_foreign_keys("job_orders")
	applicant_fks = inspector.get_foreign_keys("applicants")

	assert any(fk["referred_table"] == "organizations" for fk in client_fks)
	assert {fk["referred_table"] for fk in job_order_fks} == {"organizations", "clients"}
	assert {fk["referred_table"] for fk in applicant_fks} == {"organizations", "clients", "job_orders"}
