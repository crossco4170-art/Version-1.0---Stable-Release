from __future__ import annotations

from pathlib import Path
import sqlite3

from database.init_db import initialize_database
from services.client_service import ClientService
from services.job_order_service import JobOrderService
from services.organization_service import OrganizationService
from services.applicant_service import ApplicantService


EXPECTED_APPLICANT_COLUMNS = {
	"id",
	"organization_id",
	"client_id",
	"job_order_id",
	"first_name",
	"last_name",
	"city",
	"state",
	"resume_filename",
	"resume_path",
	"resume_score",
	"pipeline_stage",
	"applied_at",
	"last_activity_at",
	"name",
	"phone",
	"email",
	"address",
	"drivers_license_status",
	"experience",
	"resume_location",
	"current_status",
	"notes",
	"score",
	"date_added",
	"created_at",
	"updated_at",
}

EXPECTED_ORGANIZATION_COLUMNS = {
	"id",
	"name",
	"legal_name",
	"status",
	"phone",
	"email",
	"website",
	"street_address",
	"city",
	"state",
	"zip_code",
	"country",
	"created_at",
	"updated_at",
}

EXPECTED_CLIENT_COLUMNS = {
	"id",
	"organization_id",
	"company_name",
	"contact_name",
	"contact_title",
	"phone",
	"email",
	"website",
	"street_address",
	"city",
	"state",
	"zip_code",
	"country",
	"notes",
	"status",
	"created_at",
	"updated_at",
}

EXPECTED_JOB_ORDER_COLUMNS = {
	"id",
	"organization_id",
	"title",
	"job_code",
	"client_id",
	"description",
	"employment_type",
	"pay_min",
	"pay_max",
	"currency",
	"number_of_openings",
	"positions_filled",
	"work_location",
	"remote_allowed",
	"travel_required",
	"status",
	"date_opened",
	"date_closed",
	"created_at",
	"updated_at",
}


def _create_legacy_applicants_table(database_path: Path) -> None:
	conn = sqlite3.connect(database_path)
	conn.execute(
		"""
		CREATE TABLE applicants (
			id INTEGER NOT NULL PRIMARY KEY,
			name VARCHAR(255) NOT NULL,
			phone VARCHAR(50),
			email VARCHAR(255),
			address VARCHAR(500),
			drivers_license_status VARCHAR(50),
			experience TEXT,
			resume_location VARCHAR(500),
			current_status VARCHAR(100),
			notes TEXT,
			score FLOAT,
			date_added DATETIME NOT NULL,
			created_at DATETIME NOT NULL,
			updated_at DATETIME NOT NULL,
			UNIQUE (email)
		)
		"""
	)
	conn.commit()
	conn.close()


def _create_legacy_clients_table(database_path: Path) -> None:
	conn = sqlite3.connect(database_path)
	conn.execute(
		"""
		CREATE TABLE clients (
			id INTEGER NOT NULL PRIMARY KEY,
			company_name VARCHAR(255) NOT NULL,
			contact_name VARCHAR(255),
			phone VARCHAR(50),
			email VARCHAR(255),
			address VARCHAR(500),
			notes TEXT,
			created_at DATETIME NOT NULL,
			updated_at DATETIME NOT NULL
		)
		"""
	)
	conn.commit()
	conn.close()


def _create_legacy_job_orders_table(database_path: Path) -> None:
	conn = sqlite3.connect(database_path)
	conn.execute(
		"""
		CREATE TABLE job_orders (
			id INTEGER NOT NULL PRIMARY KEY,
			title VARCHAR(255) NOT NULL,
			client_id INTEGER,
			description TEXT,
			location VARCHAR(255),
			department VARCHAR(255),
			employment_type VARCHAR(100),
			salary_range VARCHAR(100),
			status VARCHAR(50),
			created_at DATETIME NOT NULL,
			updated_at DATETIME NOT NULL
		)
		"""
	)
	conn.commit()
	conn.close()



def _get_table_columns(database_path: Path, table_name: str) -> set[str]:
	conn = sqlite3.connect(database_path)
	try:
		return {row[1] for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()}
	finally:
		conn.close()


def test_fresh_database_creates_current_applicant_schema(tmp_path: Path) -> None:
	database_path = tmp_path / "fresh_applicants.db"
	initialize_database(str(database_path))

	columns = _get_table_columns(database_path, "applicants")
	assert EXPECTED_APPLICANT_COLUMNS == columns


def test_legacy_schema_upgrades_and_preserves_records(tmp_path: Path) -> None:
	database_path = tmp_path / "legacy_applicants.db"
	_create_legacy_applicants_table(database_path)
	conn = sqlite3.connect(database_path)
	conn.execute(
		"INSERT INTO applicants (id, name, email, date_added, created_at, updated_at) VALUES (1, 'Legacy Applicant', 'legacy@example.com', '2026-08-01', '2026-08-01', '2026-08-01')"
	)
	conn.commit()
	conn.close()

	initialize_database(str(database_path))

	columns = _get_table_columns(database_path, "applicants")
	assert EXPECTED_APPLICANT_COLUMNS == columns
	assert _get_table_columns(database_path, "organizations") == EXPECTED_ORGANIZATION_COLUMNS

	service = ApplicantService(database_url=str(database_path))
	applicants = service.list_applicants()
	assert len(applicants) == 1
	assert applicants[0].name == "Legacy Applicant"
	assert applicants[0].organization_id == 1
	assert applicants[0].client_id == 1
	assert applicants[0].job_order_id == 1

	organization_service = OrganizationService(database_url=str(database_path))
	client_service = ClientService(database_url=str(database_path))
	job_order_service = JobOrderService(database_url=str(database_path))
	assert organization_service.get_organization(1).name == "Legacy Organization"
	assert client_service.get_client(1).company_name == "Legacy Client"
	assert job_order_service.get_job_order(1).job_code == "LEGACY-JOB-1"


def test_applicant_upgrade_is_idempotent(tmp_path: Path) -> None:
	database_path = tmp_path / "idempotent_applicants.db"
	_create_legacy_applicants_table(database_path)
	initialize_database(str(database_path))
	first_columns = _get_table_columns(database_path, "applicants")
	initialize_database(str(database_path))
	second_columns = _get_table_columns(database_path, "applicants")

	assert first_columns == second_columns == EXPECTED_APPLICANT_COLUMNS


def test_missing_client_columns_are_added_and_legacy_columns_preserved(tmp_path: Path) -> None:
	database_path = tmp_path / "legacy_clients.db"
	_create_legacy_clients_table(database_path)
	conn = sqlite3.connect(database_path)
	conn.execute(
		"INSERT INTO clients (id, company_name, contact_name, phone, email, address, notes, created_at, updated_at) VALUES (7, 'USPS', 'Hiring Lead', '555-0200', 'usps@example.com', '475 L Enfant Plaza', 'legacy note', '2026-08-01', '2026-08-01')"
	)
	conn.commit()
	conn.close()

	initialize_database(str(database_path))

	columns = _get_table_columns(database_path, "clients")
	assert EXPECTED_CLIENT_COLUMNS.issubset(columns)
	assert "address" in columns

	service = ClientService(database_url=str(database_path))
	client = service.get_client(7)
	assert client.company_name == "USPS"
	assert client.organization_id == 1
	assert client.contact_name == "Hiring Lead"
	assert client.street_address == "475 L Enfant Plaza"


def test_missing_job_order_columns_are_added_and_legacy_columns_preserved(tmp_path: Path) -> None:
	database_path = tmp_path / "legacy_job_orders.db"
	_create_legacy_job_orders_table(database_path)
	conn = sqlite3.connect(database_path)
	conn.execute(
		"INSERT INTO job_orders (id, title, client_id, description, location, department, employment_type, salary_range, status, created_at, updated_at) VALUES (9, 'Rural Carrier Associate', 1, 'Legacy description', 'Milwaukee', 'Operations', 'Full-Time', '$20-$24', 'OPEN', '2026-08-01', '2026-08-01')"
	)
	conn.commit()
	conn.close()

	initialize_database(str(database_path))

	columns = _get_table_columns(database_path, "job_orders")
	assert EXPECTED_JOB_ORDER_COLUMNS.issubset(columns)
	assert "location" in columns
	assert "department" in columns
	assert "salary_range" in columns

	service = JobOrderService(database_url=str(database_path))
	job_order = service.get_job_order(9)
	assert job_order.organization_id == 1
	assert job_order.client_id == 1
	assert job_order.job_code == "LEGACY-JOB-9"
	assert job_order.work_location == "Milwaukee"


def test_second_upgrade_keeps_client_and_job_order_shape_stable(tmp_path: Path) -> None:
	database_path = tmp_path / "idempotent_multi_table.db"
	_create_legacy_clients_table(database_path)
	_create_legacy_job_orders_table(database_path)

	initialize_database(str(database_path))
	first_clients = _get_table_columns(database_path, "clients")
	first_job_orders = _get_table_columns(database_path, "job_orders")
	initialize_database(str(database_path))
	second_clients = _get_table_columns(database_path, "clients")
	second_job_orders = _get_table_columns(database_path, "job_orders")

	assert first_clients == second_clients
	assert first_job_orders == second_job_orders