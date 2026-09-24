from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.engine import Connection, Engine


TABLE_COLUMNS: dict[str, dict[str, str]] = {
	"organizations": {
		"name": "VARCHAR(255) NOT NULL DEFAULT 'Legacy Organization'",
		"legal_name": "VARCHAR(255) NOT NULL DEFAULT 'Legacy Organization'",
		"status": "VARCHAR(9) NOT NULL DEFAULT 'ACTIVE'",
		"phone": "VARCHAR(50)",
		"email": "VARCHAR(255)",
		"website": "VARCHAR(255)",
		"street_address": "VARCHAR(255)",
		"city": "VARCHAR(100)",
		"state": "VARCHAR(100)",
		"zip_code": "VARCHAR(20)",
		"country": "VARCHAR(100)",
		"created_at": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
		"updated_at": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
	},
	"clients": {
		"organization_id": "INTEGER NOT NULL DEFAULT 1",
		"contact_title": "VARCHAR(255)",
		"website": "VARCHAR(255)",
		"street_address": "VARCHAR(255)",
		"city": "VARCHAR(100)",
		"state": "VARCHAR(100)",
		"zip_code": "VARCHAR(20)",
		"country": "VARCHAR(100)",
		"status": "VARCHAR(9) NOT NULL DEFAULT 'ACTIVE'",
	},
	"job_orders": {
		"organization_id": "INTEGER NOT NULL DEFAULT 1",
		"job_code": "VARCHAR(100)",
		"pay_min": "NUMERIC(10, 2)",
		"pay_max": "NUMERIC(10, 2)",
		"currency": "VARCHAR(10)",
		"number_of_openings": "INTEGER",
		"positions_filled": "INTEGER",
		"work_location": "VARCHAR(255)",
		"remote_allowed": "BOOLEAN NOT NULL DEFAULT 0",
		"travel_required": "BOOLEAN NOT NULL DEFAULT 0",
		"date_opened": "DATE",
		"date_closed": "DATE",
	},
	"applicants": {
		"organization_id": "INTEGER NOT NULL DEFAULT 1",
		"client_id": "INTEGER NOT NULL DEFAULT 1",
		"job_order_id": "INTEGER NOT NULL DEFAULT 1",
		"first_name": "VARCHAR(100)",
		"last_name": "VARCHAR(100)",
		"city": "VARCHAR(100)",
		"state": "VARCHAR(100)",
		"resume_filename": "VARCHAR(255)",
		"resume_path": "VARCHAR(500)",
		"resume_score": "FLOAT",
		"pipeline_stage": "VARCHAR(20) NOT NULL DEFAULT 'NEW'",
		"applied_at": "DATETIME",
		"last_activity_at": "DATETIME",
	},
}

CREATE_INDEX_STATEMENTS: dict[str, str] = {
	"uq_applicants_email_job_order": "CREATE UNIQUE INDEX uq_applicants_email_job_order ON applicants (email, job_order_id)",
	"uq_job_orders_org_job_code": "CREATE UNIQUE INDEX uq_job_orders_org_job_code ON job_orders (organization_id, job_code)",
}


def upgrade_sqlite_schema(engine: Engine) -> None:
	"""Bring an existing SQLite database up to the current additive ORM shape."""
	if engine.dialect.name != "sqlite":
		return

	with engine.begin() as connection:
		for table_name, columns in TABLE_COLUMNS.items():
			_add_missing_columns(connection, table_name, columns)

		_sync_clients_columns(connection)
		_sync_job_order_columns(connection)
		_sync_applicant_columns(connection)
		_ensure_compatibility_foundation(connection)
		_create_indexes(connection, CREATE_INDEX_STATEMENTS)


def upgrade_sqlite_applicants_schema(engine: Engine) -> None:
	"""Backward-compatible wrapper for earlier applicant-only upgrade entrypoints."""
	upgrade_sqlite_schema(engine)


def _add_missing_columns(connection: Connection, table_name: str, columns: dict[str, str]) -> None:
	if not _table_exists(connection, table_name):
		return

	existing_columns = _existing_table_columns(connection, table_name)
	for column_name, definition in columns.items():
		if column_name not in existing_columns:
			connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}"))


def _sync_clients_columns(connection: Connection) -> None:
	if not _table_exists(connection, "clients"):
		return

	columns = _existing_table_columns(connection, "clients")
	if "organization_id" in columns:
		connection.execute(text("UPDATE clients SET organization_id = COALESCE(organization_id, 1)"))
	if "street_address" in columns and "address" in columns:
		connection.execute(text("UPDATE clients SET street_address = COALESCE(street_address, address)"))
	if "status" in columns:
		connection.execute(text("UPDATE clients SET status = COALESCE(status, 'ACTIVE')"))


def _sync_job_order_columns(connection: Connection) -> None:
	if not _table_exists(connection, "job_orders"):
		return

	columns = _existing_table_columns(connection, "job_orders")
	if "organization_id" in columns:
		connection.execute(text("UPDATE job_orders SET organization_id = COALESCE(organization_id, 1)"))
	if "work_location" in columns and "location" in columns:
		connection.execute(text("UPDATE job_orders SET work_location = COALESCE(work_location, location)"))
	if "job_code" in columns:
		connection.execute(
			text(
				"UPDATE job_orders "
				"SET job_code = printf('LEGACY-JOB-%s', id) "
				"WHERE job_code IS NULL OR TRIM(job_code) = ''"
			)
		)
	if "status" in columns:
		connection.execute(text("UPDATE job_orders SET status = COALESCE(status, 'DRAFT')"))


def _sync_applicant_columns(connection: Connection) -> None:
	if not _table_exists(connection, "applicants"):
		return

	columns = _existing_table_columns(connection, "applicants")
	for column_name in ("organization_id", "client_id", "job_order_id"):
		if column_name in columns:
			connection.execute(text(f"UPDATE applicants SET {column_name} = COALESCE({column_name}, 1)"))
	if "pipeline_stage" in columns:
		connection.execute(text("UPDATE applicants SET pipeline_stage = COALESCE(pipeline_stage, 'NEW')"))
	if "applied_at" in columns and "date_added" in columns:
		connection.execute(text("UPDATE applicants SET applied_at = COALESCE(applied_at, date_added)"))
	if "last_activity_at" in columns and "updated_at" in columns:
		connection.execute(text("UPDATE applicants SET last_activity_at = COALESCE(last_activity_at, updated_at)"))
	if "resume_score" in columns and "score" in columns:
		connection.execute(text("UPDATE applicants SET resume_score = COALESCE(resume_score, score)"))


def _ensure_compatibility_foundation(connection: Connection) -> None:
	if _table_exists(connection, "organizations") and _needs_default_organization(connection):
		connection.execute(
			text(
				"INSERT INTO organizations "
				"(id, name, legal_name, status, created_at, updated_at) "
				"VALUES (1, 'Legacy Organization', 'Legacy Organization', 'ACTIVE', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
			)
		)

	if _table_exists(connection, "clients") and _needs_default_client(connection):
		connection.execute(
			text(
				"INSERT INTO clients "
				"(id, organization_id, company_name, status, created_at, updated_at) "
				"VALUES (1, 1, 'Legacy Client', 'ACTIVE', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
			)
		)

	if _table_exists(connection, "job_orders") and _needs_default_job_order(connection):
		connection.execute(
			text(
				"INSERT INTO job_orders "
				"(id, organization_id, title, job_code, client_id, status, remote_allowed, travel_required, created_at, updated_at) "
				"VALUES (1, 1, 'Legacy Job Order', 'LEGACY-JOB-1', 1, 'DRAFT', 0, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
			)
		)


def _needs_default_organization(connection: Connection) -> bool:
	if _row_exists(connection, "organizations", 1):
		return False
	return any(_table_has_rows(connection, table_name) for table_name in ("clients", "job_orders", "applicants"))


def _needs_default_client(connection: Connection) -> bool:
	if _row_exists(connection, "clients", 1):
		return False
	return any(_table_has_rows(connection, table_name) for table_name in ("job_orders", "applicants"))


def _needs_default_job_order(connection: Connection) -> bool:
	if _row_exists(connection, "job_orders", 1):
		return False
	return _table_has_rows(connection, "applicants")


def _create_indexes(connection: Connection, statements: dict[str, str]) -> None:
	for index_name, statement in statements.items():
		if not _index_exists(connection, index_name):
			connection.execute(text(statement))


def _table_exists(connection: Connection, table_name: str) -> bool:
	result = connection.execute(
		text("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = :table_name"),
		{"table_name": table_name},
	)
	return result.first() is not None


def _index_exists(connection: Connection, index_name: str) -> bool:
	result = connection.execute(
		text("SELECT 1 FROM sqlite_master WHERE type = 'index' AND name = :index_name"),
		{"index_name": index_name},
	)
	return result.first() is not None


def _existing_table_columns(connection: Connection, table_name: str) -> set[str]:
	result = connection.execute(text(f"PRAGMA table_info({table_name})"))
	return {row[1] for row in result.fetchall()}


def _table_has_rows(connection: Connection, table_name: str) -> bool:
	if not _table_exists(connection, table_name):
		return False
	result = connection.execute(text(f"SELECT 1 FROM {table_name} LIMIT 1"))
	return result.first() is not None


def _row_exists(connection: Connection, table_name: str, row_id: int) -> bool:
	if not _table_exists(connection, table_name):
		return False
	result = connection.execute(text(f"SELECT 1 FROM {table_name} WHERE id = :row_id LIMIT 1"), {"row_id": row_id})
	return result.first() is not None