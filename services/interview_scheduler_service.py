from __future__ import annotations

import logging
from datetime import datetime
from typing import Protocol

from sqlalchemy.orm import Session

from database.connection import get_session
from models.applicant import Applicant
from models.interview import Interview
from services.applicant_service import ApplicantService
from services.interview_service import InterviewService
from utils.exceptions import BlackcrestInputError, BlackcrestNotFoundError


class CalendarProvider(Protocol):
    """Contract for future calendar integrations (Google, Outlook, etc.)."""

    def create_interview_event(self, *, interview: Interview, applicant: Applicant) -> str | None:
        """Create a calendar event and return an optional external event id."""


class InterviewSchedulerService:
    """Schedules interviews and updates applicant status in one service boundary."""

    def __init__(
        self,
        *,
        session: Session | None = None,
        database_url: str | None = None,
        calendar_provider: CalendarProvider | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.session = session or get_session(database_url=database_url, ensure_schema=True)

        self.applicant_service = ApplicantService(session=self.session)
        self.interview_service = InterviewService(session=self.session)
        self.calendar_provider = calendar_provider
        self.logger = logger or logging.getLogger("blackcrest.interview_scheduler")

    def schedule_interview(
        self,
        *,
        applicant_id: int,
        interview_date: str,
        interview_time: str,
        recruiter: str,
        notes: str | None = None,
        job_order_id: int | None = None,
        interview_type: str = "scheduled",
        status_on_schedule: str = "Interview Scheduled",
    ) -> Interview:
        if applicant_id <= 0:
            raise BlackcrestInputError("Applicant ID must be greater than zero")
        if not recruiter or not recruiter.strip():
            raise BlackcrestInputError("Recruiter is required")

        scheduled_at = self._parse_datetime(interview_date=interview_date, interview_time=interview_time)
        applicant = self.applicant_service.get_applicant(applicant_id)
        if applicant is None:
            raise BlackcrestNotFoundError(f"Applicant not found: {applicant_id}")

        interview = self.interview_service.create(
            applicant_id=applicant_id,
            job_order_id=job_order_id,
            interview_type=interview_type.strip() if interview_type and interview_type.strip() else None,
            interview_date=scheduled_at,
            interviewer_name=recruiter.strip(),
            notes=notes.strip() if notes and notes.strip() else None,
        )

        self.applicant_service.edit_applicant(applicant_id, current_status=status_on_schedule)
        self._try_calendar_integration(interview=interview, applicant=applicant)
        return interview

    def reschedule_interview(
        self,
        *,
        interview_id: int,
        interview_date: str,
        interview_time: str,
        recruiter: str,
        notes: str | None = None,
        status_on_reschedule: str = "Interview Rescheduled",
    ) -> Interview | None:
        if interview_id <= 0:
            raise BlackcrestInputError("Interview ID must be greater than zero")
        if not recruiter or not recruiter.strip():
            raise BlackcrestInputError("Recruiter is required")

        scheduled_at = self._parse_datetime(interview_date=interview_date, interview_time=interview_time)
        interview = self.interview_service.update(
            interview_id,
            interview_date=scheduled_at,
            interviewer_name=recruiter.strip(),
            notes=notes.strip() if notes and notes.strip() else None,
        )
        if interview is None:
            return None

        self.applicant_service.edit_applicant(interview.applicant_id, current_status=status_on_reschedule)
        applicant = self.applicant_service.get_applicant(interview.applicant_id)
        if applicant is not None:
            self._try_calendar_integration(interview=interview, applicant=applicant)
        return interview

    def _parse_datetime(self, *, interview_date: str, interview_time: str) -> datetime:
        try:
            combined = f"{interview_date.strip()} {interview_time.strip()}"
            return datetime.strptime(combined, "%Y-%m-%d %H:%M")
        except Exception as exc:
            raise BlackcrestInputError("Interview date/time must use YYYY-MM-DD and HH:MM (24-hour) format") from exc

    def _try_calendar_integration(self, *, interview: Interview, applicant: Applicant) -> None:
        if self.calendar_provider is None:
            return
        try:
            self.calendar_provider.create_interview_event(interview=interview, applicant=applicant)
        except Exception as exc:  # pragma: no cover - behavior validated via tests
            self.logger.warning(
                "Calendar integration failed for interview %s and applicant %s: %s",
                interview.id,
                applicant.id,
                exc,
            )
