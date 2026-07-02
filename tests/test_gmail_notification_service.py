from __future__ import annotations

import logging
from types import SimpleNamespace

from models.applicant import Applicant
from services.gmail_notification_service import GmailNotificationService


class FakeSMTP:
    def __init__(self, failures_before_success: int = 0) -> None:
        self.failures_before_success = failures_before_success
        self.calls = 0
        self.messages = []

    def __call__(self, host: str, port: int, timeout: int = 30) -> "FakeSMTP":
        return self

    def __enter__(self) -> "FakeSMTP":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False

    def login(self, username: str, password: str) -> None:
        return None

    def send_message(self, message) -> None:
        self.calls += 1
        if self.calls <= self.failures_before_success:
            raise RuntimeError("transient smtp error")
        self.messages.append(message)


class CaptureHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


def build_settings(**overrides):
    base = {
        "score_notification_threshold": 85.0,
        "gmail_retry_attempts": 3,
        "gmail_retry_delay_seconds": 0.0,
        "gmail_username": "bot@example.com",
        "gmail_password": "app-password",
        "recruiter_notification_emails": "recruiter@example.com",
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def build_applicant(score: float | None) -> Applicant:
    applicant = Applicant(
        id=1,
        name="Jane Doe",
        email="jane@example.com",
        phone="555-1234",
        current_status="screened",
        experience="5 years",
        notes="Strong backend profile",
        score=score,
    )
    return applicant


def test_notification_sent_with_retry_and_summary() -> None:
    smtp = FakeSMTP(failures_before_success=1)
    sleep_calls = []

    logger = logging.getLogger("test.gmail.retry")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    capture = CaptureHandler()
    logger.addHandler(capture)

    service = GmailNotificationService(
        settings=build_settings(),
        logger=logger,
        smtp_factory=smtp,
        sleep_fn=lambda seconds: sleep_calls.append(seconds),
    )

    sent = service.notify_if_candidate_exceeds_score(build_applicant(91.5))

    assert sent is True
    assert smtp.calls == 2
    assert len(smtp.messages) == 1
    assert "Jane Doe" in smtp.messages[0].get_content()
    assert "Threshold: 85.0" in smtp.messages[0].get_content()
    assert sleep_calls == [0.0] or sleep_calls == []
    assert any("attempt 1/3 failed" in record.getMessage() for record in capture.records)
    assert any("notification sent" in record.getMessage() for record in capture.records)


def test_notification_skipped_when_below_threshold() -> None:
    smtp = FakeSMTP()
    service = GmailNotificationService(
        settings=build_settings(score_notification_threshold=90.0),
        smtp_factory=smtp,
    )

    sent = service.notify_if_candidate_exceeds_score(build_applicant(72.0))

    assert sent is False
    assert smtp.calls == 0


def test_notification_gracefully_handles_missing_credentials() -> None:
    smtp = FakeSMTP()
    service = GmailNotificationService(
        settings=build_settings(gmail_username="", gmail_password=""),
        smtp_factory=smtp,
    )

    sent = service.notify_if_candidate_exceeds_score(build_applicant(95.0))

    assert sent is False
    assert smtp.calls == 0
