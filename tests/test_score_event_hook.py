from __future__ import annotations

from types import SimpleNamespace

from services.gmail_notification_service import GmailNotificationService
from services.score_event_hook import CandidateScoredEvent, CandidateScoreEventHook


class StubListener:
    def __init__(self) -> None:
        self.events: list[CandidateScoredEvent] = []

    def handle_candidate_scored(self, event: CandidateScoredEvent) -> bool:
        self.events.append(event)
        return True


def test_event_hook_register_emit_unregister() -> None:
    hook = CandidateScoreEventHook()
    listener = StubListener()

    hook.register(listener)
    event = CandidateScoredEvent(applicant_id=42, score=92.0, threshold=85.0)

    outcomes = hook.emit(event)

    assert outcomes == [True]
    assert len(listener.events) == 1
    assert listener.events[0].applicant_id == 42

    hook.unregister(listener)
    assert hook.emit(event) == []


def test_gmail_service_supports_event_hook_adapter() -> None:
    settings = SimpleNamespace(
        score_notification_threshold=85.0,
        gmail_retry_attempts=1,
        gmail_retry_delay_seconds=0.0,
        gmail_username="bot@example.com",
        gmail_password="secret",
        recruiter_notification_emails="recruiter@example.com",
    )

    service = GmailNotificationService(settings=settings)
    calls: list[int] = []

    def fake_notify_by_applicant_id(applicant_id: int, *, database_url: str | None = None) -> bool:
        calls.append(applicant_id)
        return True

    service.notify_by_applicant_id = fake_notify_by_applicant_id  # type: ignore[method-assign]

    low_event = CandidateScoredEvent(applicant_id=3, score=70.0, threshold=85.0)
    high_event = CandidateScoredEvent(applicant_id=9, score=91.0, threshold=85.0)

    assert service.handle_candidate_scored(low_event) is False
    assert service.handle_candidate_scored(high_event) is True
    assert calls == [9]
