from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from database import initialize_database
from models.client import Client
from models.job_order import JobOrder
from models.organization import Organization, OrganizationStatus
from services.applicant_service import ApplicantService
from services.reporting_service import ReportingService
from services.score_event_hook import CandidateScoredEvent


def _create_foundation(session) -> tuple[int, int, int]:
    organization = Organization(
        name="Greater Connections Staffing",
        legal_name="Greater Connections Staffing LLC",
        status=OrganizationStatus.ACTIVE,
    )
    session.add(organization)
    session.commit()

    client = Client(
        organization_id=organization.id,
        company_name="USPS",
    )
    session.add(client)
    session.commit()

    job_order = JobOrder(
        organization_id=organization.id,
        client_id=client.id,
        job_code="USPS-RCA-2026-001",
        title="Rural Carrier Associate",
    )
    session.add(job_order)
    session.commit()

    return organization.id, client.id, job_order.id


def test_applicant_timestamps_are_stored_as_utc_naive(tmp_path: Path) -> None:
    database_path = tmp_path / "datetime_policy.db"
    initialize_database(str(database_path))

    service = ApplicantService(database_url=str(database_path))
    organization_id, client_id, job_order_id = _create_foundation(service.session)
    created = service.create_applicant(
        organization_id=organization_id,
        client_id=client_id,
        job_order_id=job_order_id,
        name="UTC Candidate",
        email="utc@example.com",
    )

    assert created.created_at.tzinfo is None
    assert created.updated_at.tzinfo is None
    assert created.date_added.tzinfo is None


def test_applicant_service_normalizes_aware_date_added_to_utc_naive(tmp_path: Path) -> None:
    database_path = tmp_path / "datetime_policy_normalize.db"
    initialize_database(str(database_path))

    service = ApplicantService(database_url=str(database_path))
    organization_id, client_id, job_order_id = _create_foundation(service.session)
    aware_date = datetime(2026, 1, 1, 12, 30, tzinfo=UTC)

    created = service.create_applicant(
        organization_id=organization_id,
        client_id=client_id,
        job_order_id=job_order_id,
        name="Aware Candidate",
        email="aware@example.com",
        date_added=aware_date,
    )

    assert created.date_added.tzinfo is None
    assert created.date_added == datetime(2026, 1, 1, 12, 30)


def test_reporting_and_event_timestamps_are_utc_naive(tmp_path: Path) -> None:
    database_path = tmp_path / "datetime_policy_reporting.db"
    initialize_database(str(database_path))

    service = ApplicantService(database_url=str(database_path))
    organization_id, client_id, job_order_id = _create_foundation(service.session)
    service.create_applicant(
        organization_id=organization_id,
        client_id=client_id,
        job_order_id=job_order_id,
        name="Report Candidate",
        email="report@example.com",
    )

    reporting = ReportingService(database_url=str(database_path))
    report = reporting.generate_daily_report(target_date=datetime.now().date())
    generated_at = datetime.fromisoformat(report["generated_at"])

    assert generated_at.tzinfo is None

    event = CandidateScoredEvent(applicant_id=1, score=90, threshold=85)
    assert event.occurred_at.tzinfo is None
