from __future__ import annotations

from datetime import datetime

from services.applicant_service import ApplicantService
from services.interview_service import InterviewService
from services.reporting_service import ReportingService
from tests.helpers import build_test_session


def test_daily_weekly_monthly_reports_include_expected_metrics(tmp_path) -> None:
    session = build_test_session(tmp_path / "reports.db")

    applicant_service = ApplicantService(session=session)
    interview_service = InterviewService(session=session)
    reporting = ReportingService(session=session)

    alice = applicant_service.create(
        name="Alice",
        email="alice@example.com",
        score=91,
        current_status="screened",
        date_added=datetime(2026, 7, 1, 9, 0),
    )
    bob = applicant_service.create(
        name="Bob",
        email="bob@example.com",
        score=72,
        current_status="interview",
        date_added=datetime(2026, 7, 3, 11, 0),
    )
    applicant_service.create(
        name="Cara",
        email="cara@example.com",
        score=88,
        current_status="offer",
        date_added=datetime(2026, 8, 2, 10, 0),
    )

    interview_service.create(
        applicant_id=alice.id,
        interview_date=datetime(2026, 7, 1, 15, 0),
        interviewer_name="Recruiter A",
    )
    interview_service.create(
        applicant_id=bob.id,
        interview_date=datetime(2026, 7, 4, 10, 30),
        interviewer_name="Recruiter B",
    )

    daily = reporting.generate_daily_report(target_date=datetime(2026, 7, 1).date())
    assert daily["summary"]["total_new_applicants"] == 1
    assert daily["summary"]["interviews_scheduled"] == 1

    weekly = reporting.generate_weekly_report(target_date=datetime(2026, 7, 3).date())
    assert weekly["summary"]["total_new_applicants"] == 2
    assert weekly["summary"]["interviews_scheduled"] == 2

    monthly = reporting.generate_monthly_report(year=2026, month=7)
    assert monthly["summary"]["total_new_applicants"] == 2
    assert monthly["summary"]["average_score"] == 81.5


def test_pipeline_report_and_exports_create_files(tmp_path) -> None:
    session = build_test_session(tmp_path / "exports.db")

    applicant_service = ApplicantService(session=session)
    reporting = ReportingService(session=session)

    applicant_service.create(
        name="Nina",
        email="nina@example.com",
        current_status="screened",
        score=90,
        date_added=datetime(2026, 7, 2, 9, 0),
    )
    applicant_service.create(
        name="Oscar",
        email="oscar@example.com",
        current_status="rejected",
        score=55,
        date_added=datetime(2026, 7, 3, 9, 0),
    )

    report = reporting.generate_applicant_pipeline_report()
    assert report["report_type"] == "applicant_pipeline"
    assert report["summary"]["total_applicants"] == 2

    csv_path = reporting.export_report_to_csv(report, tmp_path / "pipeline.csv")
    xlsx_path = reporting.export_report_to_excel(report, tmp_path / "pipeline.xlsx")
    pdf_path = reporting.export_report_to_pdf(report, tmp_path / "pipeline.pdf")

    assert csv_path.exists()
    assert xlsx_path.exists()
    assert pdf_path.exists()
    assert csv_path.read_text(encoding="utf-8").startswith("Report Type")
    assert xlsx_path.stat().st_size > 0
    assert pdf_path.stat().st_size > 0
