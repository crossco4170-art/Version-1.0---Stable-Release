from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol

from utils.datetime_policy import utc_now_naive


@dataclass(frozen=True)
class CandidateScoredEvent:
    """Represents a scoring outcome emitted by an independent scoring engine."""

    applicant_id: int
    score: float
    threshold: float
    source: str = "applicant_scoring_engine"
    occurred_at: datetime = field(default_factory=utc_now_naive)


class CandidateScoreListener(Protocol):
    """Contract for modules that consume score events."""

    def handle_candidate_scored(self, event: CandidateScoredEvent) -> bool:
        ...


class CandidateScoreEventHook:
    """In-memory hook for decoupled score event publication and subscription."""

    def __init__(self) -> None:
        self._listeners: list[CandidateScoreListener] = []

    def register(self, listener: CandidateScoreListener) -> None:
        if listener in self._listeners:
            return
        self._listeners.append(listener)

    def unregister(self, listener: CandidateScoreListener) -> None:
        self._listeners = [item for item in self._listeners if item is not listener]

    def emit(self, event: CandidateScoredEvent) -> list[bool]:
        outcomes: list[bool] = []
        for listener in self._listeners:
            outcomes.append(listener.handle_candidate_scored(event))
        return outcomes
