from __future__ import annotations

import logging
import smtplib
import time
from email.message import EmailMessage
from typing import Any, Callable

from config.settings import Settings, get_settings
from models.applicant import Applicant
from services.applicant_service import ApplicantService
from services.score_event_hook import CandidateScoredEvent


class GmailNotificationService:
    """Send recruiter notifications for high-scoring candidates via Gmail."""

    def __init__(
        self,
        *,
        settings: Settings | None = None,
        logger: logging.Logger | None = None,
        smtp_factory: Callable[..., Any] | None = None,
        sleep_fn: Callable[[float], None] | None = None,
    ) -> None:
        self.settings = settings or get_settings(validate_required=False)
        self.logger = logger or logging.getLogger("blackcrest.gmail_notifications")
        self.smtp_factory = smtp_factory or smtplib.SMTP_SSL
        self.sleep_fn = sleep_fn or time.sleep

    def notify_if_candidate_exceeds_score(self, applicant: Applicant) -> bool:
        score = applicant.score
        threshold = self.settings.score_notification_threshold

        if score is None:
            self.logger.info("Skipping Gmail notification for applicant %s: no score", applicant.id)
            return False

        if score < threshold:
            self.logger.info(
                "Skipping Gmail notification for applicant %s: score %.2f below threshold %.2f",
                applicant.id,
                score,
                threshold,
            )
            return False

        validator = getattr(self.settings, "validate_gmail_settings", None)
        if callable(validator):
            try:
                validator(require_recipients=True)
            except ValueError as exc:
                self.logger.warning(
                    "Skipping Gmail notification for applicant %s: %s",
                    applicant.id,
                    exc,
                )
                return False

        recipients = self._get_recipients()
        if not recipients:
            self.logger.warning(
                "Skipping Gmail notification for applicant %s: no recruiter recipients configured",
                applicant.id,
            )
            return False

        if not self.settings.gmail_username.strip() or not self.settings.gmail_password.strip():
            self.logger.warning(
                "Skipping Gmail notification for applicant %s: Gmail credentials are not configured",
                applicant.id,
            )
            return False

        subject = f"Candidate Alert: {applicant.name} scored {score:.1f}"
        body = self._build_applicant_summary(applicant, threshold)

        attempts = self.settings.gmail_retry_attempts
        delay_seconds = self.settings.gmail_retry_delay_seconds

        for attempt in range(1, attempts + 1):
            try:
                self._send_email(subject=subject, body=body, recipients=recipients)
                self.logger.info(
                    "Gmail notification sent for applicant %s on attempt %s",
                    applicant.id,
                    attempt,
                )
                return True
            except Exception as exc:  # pragma: no cover - behavior asserted by tests
                self.logger.warning(
                    "Gmail send attempt %s/%s failed for applicant %s: %s",
                    attempt,
                    attempts,
                    applicant.id,
                    exc,
                )
                if attempt == attempts:
                    self.logger.error(
                        "Gmail notification failed after %s attempts for applicant %s",
                        attempts,
                        applicant.id,
                    )
                    return False
                if delay_seconds > 0:
                    self.sleep_fn(delay_seconds)

        return False

    def notify_by_applicant_id(self, applicant_id: int, *, database_url: str | None = None) -> bool:
        service = ApplicantService(database_url=database_url)
        applicant = service.get_applicant(applicant_id)
        if applicant is None:
            self.logger.warning("Applicant %s not found; no Gmail notification sent", applicant_id)
            return False
        return self.notify_if_candidate_exceeds_score(applicant)

    def handle_candidate_scored(self, event: CandidateScoredEvent) -> bool:
        """Event-hook adapter for future score-engine integration."""
        if event.score < event.threshold:
            self.logger.info(
                "Skipping Gmail notification for applicant %s: score %.2f below event threshold %.2f",
                event.applicant_id,
                event.score,
                event.threshold,
            )
            return False
        return self.notify_by_applicant_id(event.applicant_id)

    def _build_applicant_summary(self, applicant: Applicant, threshold: float) -> str:
        return "\n".join(
            [
                "A candidate exceeded the configured score threshold.",
                "",
                f"Applicant ID: {applicant.id}",
                f"Name: {applicant.name}",
                f"Email: {applicant.email or 'Not provided'}",
                f"Phone: {applicant.phone or 'Not provided'}",
                f"Score: {applicant.score if applicant.score is not None else 'N/A'}",
                f"Threshold: {threshold}",
                f"Status: {applicant.current_status or 'Not set'}",
                f"Experience: {applicant.experience or 'Not provided'}",
                f"Notes: {applicant.notes or 'Not provided'}",
            ]
        )

    def _send_email(self, *, subject: str, body: str, recipients: list[str]) -> None:
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = self.settings.gmail_username
        message["To"] = ", ".join(recipients)
        message.set_content(body)

        with self.smtp_factory("smtp.gmail.com", 465, timeout=30) as smtp:
            smtp.login(self.settings.gmail_username, self.settings.gmail_password)
            smtp.send_message(message)

    def _get_recipients(self) -> list[str]:
        raw = self.settings.recruiter_notification_emails
        parts = [entry.strip() for entry in raw.replace(";", ",").split(",")]
        return [entry for entry in parts if entry]
