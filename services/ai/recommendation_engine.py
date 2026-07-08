from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from services.ai.models import MatchResult


class RecommendationLevel(str, Enum):
    """Deterministic recommendation levels for candidate progression."""

    ADVANCE_TO_PHONE_SCREEN = "ADVANCE_TO_PHONE_SCREEN"
    ADVANCE_TO_CLIENT = "ADVANCE_TO_CLIENT"
    RECRUITER_REVIEW = "RECRUITER_REVIEW"
    HOLD = "HOLD"
    DO_NOT_ADVANCE = "DO_NOT_ADVANCE"


@dataclass(slots=True)
class RecommendationPolicy:
    """Threshold policy used by the deterministic recommendation engine."""

    excellent_score: float = 90.0
    strong_score: float = 80.0
    borderline_score: float = 65.0
    low_score: float = 45.0

    excellent_confidence: float = 0.85
    strong_confidence: float = 0.7
    borderline_confidence: float = 0.55
    hold_confidence: float = 0.4

    unknown_confidence_penalty: float = 0.05
    missing_confidence_penalty: float = 0.03


class RecommendationEngine:
    """Maps scored match results to deterministic recommendation outcomes."""

    def __init__(self, policy: RecommendationPolicy | None = None) -> None:
        self.policy = policy or RecommendationPolicy()

    def recommend(self, match_result: MatchResult) -> MatchResult:
        score = float(match_result.overall_match_percentage or 0.0)
        confidence = self._effective_confidence(match_result)

        has_hard_failure = bool(match_result.hard_requirement_failures)
        if has_hard_failure:
            match_result.recommendation = RecommendationLevel.DO_NOT_ADVANCE.value
            return match_result

        if score >= self.policy.excellent_score and confidence >= self.policy.excellent_confidence:
            match_result.recommendation = RecommendationLevel.ADVANCE_TO_CLIENT.value
            return match_result

        if score >= self.policy.strong_score and confidence >= self.policy.strong_confidence:
            match_result.recommendation = RecommendationLevel.ADVANCE_TO_PHONE_SCREEN.value
            return match_result

        if score >= self.policy.borderline_score and confidence >= self.policy.borderline_confidence:
            match_result.recommendation = RecommendationLevel.RECRUITER_REVIEW.value
            return match_result

        if score >= self.policy.low_score and confidence >= self.policy.hold_confidence:
            match_result.recommendation = RecommendationLevel.HOLD.value
            return match_result

        match_result.recommendation = RecommendationLevel.DO_NOT_ADVANCE.value
        return match_result

    def _effective_confidence(self, match_result: MatchResult) -> float:
        base = float(match_result.confidence or 0.0)
        unknown_penalty = len(match_result.unknown_requirements) * self.policy.unknown_confidence_penalty
        missing_penalty = len(match_result.missing_requirements) * self.policy.missing_confidence_penalty
        adjusted = base - unknown_penalty - missing_penalty
        return max(0.0, min(1.0, adjusted))
