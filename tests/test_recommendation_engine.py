from __future__ import annotations

from services.ai.models import MatchResult
from services.ai.recommendation_engine import RecommendationEngine, RecommendationLevel


def test_excellent_candidate() -> None:
    engine = RecommendationEngine()
    result = MatchResult(
        overall_match_percentage=95.0,
        confidence=0.92,
        hard_requirement_failures=[],
        missing_requirements=[],
        unknown_requirements=[],
    )

    recommended = engine.recommend(result)

    assert recommended.recommendation == RecommendationLevel.ADVANCE_TO_CLIENT.value


def test_strong_candidate() -> None:
    engine = RecommendationEngine()
    result = MatchResult(
        overall_match_percentage=84.0,
        confidence=0.78,
        hard_requirement_failures=[],
        missing_requirements=[],
        unknown_requirements=[],
    )

    recommended = engine.recommend(result)

    assert recommended.recommendation == RecommendationLevel.ADVANCE_TO_PHONE_SCREEN.value


def test_borderline_candidate() -> None:
    engine = RecommendationEngine()
    result = MatchResult(
        overall_match_percentage=69.0,
        confidence=0.62,
        hard_requirement_failures=[],
        missing_requirements=["Management Experience"],
        unknown_requirements=[],
    )

    recommended = engine.recommend(result)

    assert recommended.recommendation == RecommendationLevel.RECRUITER_REVIEW.value


def test_hard_requirement_failure() -> None:
    engine = RecommendationEngine()
    result = MatchResult(
        overall_match_percentage=96.0,
        confidence=0.95,
        hard_requirement_failures=["CDL Requirement"],
        missing_requirements=["CDL Requirement"],
        unknown_requirements=[],
    )

    recommended = engine.recommend(result)

    assert recommended.recommendation == RecommendationLevel.DO_NOT_ADVANCE.value


def test_unknown_requirement_handling() -> None:
    engine = RecommendationEngine()
    result = MatchResult(
        overall_match_percentage=82.0,
        confidence=0.80,
        hard_requirement_failures=[],
        missing_requirements=[],
        unknown_requirements=["Unmapped Requirement A", "Unmapped Requirement B"],
    )

    recommended = engine.recommend(result)

    assert recommended.recommendation == RecommendationLevel.ADVANCE_TO_PHONE_SCREEN.value


def test_low_confidence() -> None:
    engine = RecommendationEngine()
    result = MatchResult(
        overall_match_percentage=82.0,
        confidence=0.30,
        hard_requirement_failures=[],
        missing_requirements=[],
        unknown_requirements=[],
    )

    recommended = engine.recommend(result)

    assert recommended.recommendation == RecommendationLevel.DO_NOT_ADVANCE.value


def test_deterministic_repeated_recommendations() -> None:
    engine = RecommendationEngine()

    first = engine.recommend(
        MatchResult(
            overall_match_percentage=77.0,
            confidence=0.67,
            hard_requirement_failures=[],
            missing_requirements=["Education Requirement"],
            unknown_requirements=["Unmapped Requirement"],
        )
    )
    second = engine.recommend(
        MatchResult(
            overall_match_percentage=77.0,
            confidence=0.67,
            hard_requirement_failures=[],
            missing_requirements=["Education Requirement"],
            unknown_requirements=["Unmapped Requirement"],
        )
    )

    assert first.recommendation == second.recommendation
    assert first.recommendation == RecommendationLevel.RECRUITER_REVIEW.value
