from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from database import initialize_database
from services.applicant_service import ApplicantService
from services.reporting_service import ReportingService
from services.score_event_hook import CandidateScoredEvent


def test_applicant_timestamps_are_stored_as_utc_naive(tmp_path: Path) -> None:
    database_path = tmp_path / "datetime_policy.db"
    initialize_database(str(database_path))

    service = ApplicantService(database_url=str(database_path))
    created = service.create_applicant(name="UTC Candidate", email="utc@example.com")

    assert created.created_at.tzinfo is None
    assert created.updated_at.tzinfo is None
    assert created.date_added.tzinfo is None


def test_applicant_service_normalizes_aware_date_added_to_utc_naive(tmp_path: Path) -> None:
    database_path = tmp_path / "datetime_policy_normalize.db"
    initialize_database(str(database_path))

    service = ApplicantService(database_url=str(database_path))
    aware_date = datetime(2026, 1, 1, 12, 30, tzinfo=UTC)

    created = service.create_applicant(
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
    service.create_applicant(name="Report Candidate", email="report@example.com")

    reporting = ReportingService(database_url=str(database_path))
    report = reporting.generate_daily_report(target_date=datetime.now().date())
    generated_at = datetime.fromisoformat(report["generated_at"])

    assert generated_at.tzinfo is None

    event = CandidateScoredEvent(applicant_id=1, score=90, threshold=85)
    assert event.occurred_at.tzinfo is None
