from __future__ import annotations

import logging

from models.client import Client
from models.job_order import JobOrder
from models.organization import Organization, OrganizationStatus
from services.applicant_service import ApplicantService
from services.interview_scheduler_service import InterviewSchedulerService
from tests.helpers import build_test_session


class StubCalendarProvider:
    def __init__(self, should_fail: bool = False) -> None:
        self.should_fail = should_fail
        self.calls = 0

    def create_interview_event(self, **kwargs):
        self.calls += 1
        if self.should_fail:
            raise RuntimeError("calendar unavailable")
        return "evt_123"


class CaptureHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


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


def test_schedule_interview_creates_record_and_updates_applicant_status(tmp_path) -> None:
    session = build_test_session(tmp_path / "schedule_test.db")

    applicant_service = ApplicantService(session=session)
    organization_id, client_id, job_order_id = _create_foundation(session)
    applicant = applicant_service.create(
        organization_id=organization_id,
        client_id=client_id,
        job_order_id=job_order_id,
        name="Jane Doe",
        email="jane@example.com",
    )

    scheduler = InterviewSchedulerService(session=session)
    interview = scheduler.schedule_interview(
        applicant_id=applicant.id,
        interview_date="2026-07-10",
        interview_time="14:30",
        recruiter="Alex Recruiter",
        notes="Technical screen with backend panel",
    )

    assert interview.applicant_id == applicant.id
    assert interview.interviewer_name == "Alex Recruiter"
    assert interview.interview_date is not None
    assert interview.interview_date.strftime("%Y-%m-%d %H:%M") == "2026-07-10 14:30"

    updated = applicant_service.get_applicant(applicant.id)
    assert updated is not None
    assert updated.current_status == "Interview Scheduled"


def test_schedule_interview_uses_calendar_provider_when_configured(tmp_path) -> None:
    session = build_test_session(tmp_path / "schedule_calendar_test.db")

    applicant_service = ApplicantService(session=session)
    organization_id, client_id, job_order_id = _create_foundation(session)
    applicant = applicant_service.create(
        organization_id=organization_id,
        client_id=client_id,
        job_order_id=job_order_id,
        name="John Doe",
        email="john@example.com",
    )

    provider = StubCalendarProvider()
    scheduler = InterviewSchedulerService(session=session, calendar_provider=provider)

    scheduler.schedule_interview(
        applicant_id=applicant.id,
        interview_date="2026-07-11",
        interview_time="09:00",
        recruiter="Taylor Recruiter",
    )

    assert provider.calls == 1


def test_schedule_interview_handles_calendar_failure_gracefully(tmp_path) -> None:
    session = build_test_session(tmp_path / "schedule_calendar_failure.db")

    applicant_service = ApplicantService(session=session)
    organization_id, client_id, job_order_id = _create_foundation(session)
    applicant = applicant_service.create(
        organization_id=organization_id,
        client_id=client_id,
        job_order_id=job_order_id,
        name="Chris Doe",
        email="chris@example.com",
    )

    logger = logging.getLogger("test.interview.scheduler")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    capture = CaptureHandler()
    logger.addHandler(capture)

    provider = StubCalendarProvider(should_fail=True)
    scheduler = InterviewSchedulerService(session=session, calendar_provider=provider, logger=logger)

    interview = scheduler.schedule_interview(
        applicant_id=applicant.id,
        interview_date="2026-07-12",
        interview_time="11:15",
        recruiter="Jordan Recruiter",
    )

    assert interview is not None
    assert provider.calls == 1
    assert any("Calendar integration failed" in record.getMessage() for record in capture.records)


def test_reschedule_interview_updates_time_recruiter_notes_and_status(tmp_path) -> None:
    session = build_test_session(tmp_path / "reschedule_test.db")

    applicant_service = ApplicantService(session=session)
    organization_id, client_id, job_order_id = _create_foundation(session)
    applicant = applicant_service.create(
        organization_id=organization_id,
        client_id=client_id,
        job_order_id=job_order_id,
        name="Pat Doe",
        email="pat@example.com",
    )

    scheduler = InterviewSchedulerService(session=session)
    interview = scheduler.schedule_interview(
        applicant_id=applicant.id,
        interview_date="2026-07-20",
        interview_time="13:00",
        recruiter="Riley Recruiter",
        notes="Initial screen",
    )

    updated = scheduler.reschedule_interview(
        interview_id=interview.id,
        interview_date="2026-07-21",
        interview_time="16:45",
        recruiter="Morgan Recruiter",
        notes="Moved after candidate request",
    )

    assert updated is not None
    assert updated.interviewer_name == "Morgan Recruiter"
    assert updated.notes == "Moved after candidate request"
    assert updated.interview_date is not None
    assert updated.interview_date.strftime("%Y-%m-%d %H:%M") == "2026-07-21 16:45"

    refreshed = applicant_service.get_applicant(applicant.id)
    assert refreshed is not None
    assert refreshed.current_status == "Interview Rescheduled"


def test_schedule_interview_validates_datetime_format(tmp_path) -> None:
    session = build_test_session(tmp_path / "schedule_invalid_datetime.db")

    applicant_service = ApplicantService(session=session)
    organization_id, client_id, job_order_id = _create_foundation(session)
    applicant = applicant_service.create(
        organization_id=organization_id,
        client_id=client_id,
        job_order_id=job_order_id,
        name="Jamie Doe",
        email="jamie@example.com",
    )

    scheduler = InterviewSchedulerService(session=session)

    try:
        scheduler.schedule_interview(
            applicant_id=applicant.id,
            interview_date="07-22-2026",
            interview_time="4:30 PM",
            recruiter="Avery Recruiter",
        )
    except ValueError as exc:
        assert "YYYY-MM-DD" in str(exc)
    else:
        raise AssertionError("Expected ValueError for invalid interview date/time format")
