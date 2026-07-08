from __future__ import annotations

from services.ai.models import MatchResult
from services.ai.recruiter_summary import RecruiterSummaryGenerator


def test_excellent_candidate_summary() -> None:
    generator = RecruiterSummaryGenerator()
    match_result = MatchResult(
        overall_match_percentage=94.5,
        confidence=0.93,
        recommendation="ADVANCE_TO_CLIENT",
        strengths=["CDL Requirement", "Delivery Experience", "Skill Match"],
        missing_requirements=[],
        hard_requirement_failures=[],
        unknown_requirements=[],
    )

    summary = generator.generate(match_result)

    assert summary.headline == "Excellent fit ready for client submission"
    assert summary.recommendation == "ADVANCE_TO_CLIENT"
    assert "Primary match reasons" in summary.summary


def test_borderline_candidate_summary() -> None:
    generator = RecruiterSummaryGenerator()
    match_result = MatchResult(
        overall_match_percentage=66.0,
        confidence=0.58,
        recommendation="RECRUITER_REVIEW",
        strengths=["Skill Match"],
        missing_requirements=["Management Experience"],
    )

    summary = generator.generate(match_result)

    assert summary.headline == "Borderline fit requires recruiter review"
    assert "Missing requirements" in summary.summary
    assert "Management Experience" in summary.missing_requirements


def test_hard_requirement_failure_summary() -> None:
    generator = RecruiterSummaryGenerator()
    match_result = MatchResult(
        overall_match_percentage=88.0,
        confidence=0.84,
        recommendation="DO_NOT_ADVANCE",
        strengths=["Skill Match"],
        missing_requirements=["CDL Requirement"],
        hard_requirement_failures=["CDL Requirement"],
    )

    summary = generator.generate(match_result)

    assert summary.headline == "Hard requirement failure blocks advancement"
    assert "Hard requirement failures" in summary.summary
    assert any("Hard requirement failure: CDL Requirement" == item for item in summary.concerns)


def test_unknown_requirement_summary() -> None:
    generator = RecruiterSummaryGenerator()
    match_result = MatchResult(
        overall_match_percentage=79.0,
        confidence=0.69,
        recommendation="HOLD",
        strengths=["Delivery Experience"],
        unknown_requirements=["Industry-Specific Permit"],
    )

    summary = generator.generate(match_result)

    assert any(item == "Unknown requirement: Industry-Specific Permit" for item in summary.concerns)
    assert "Unknown requirements reduced certainty" in summary.summary


def test_missing_requirement_summary() -> None:
    generator = RecruiterSummaryGenerator()
    match_result = MatchResult(
        overall_match_percentage=74.0,
        confidence=0.65,
        recommendation="HOLD",
        strengths=["Communication"],
        missing_requirements=["Background Check", "Drug Test"],
    )

    summary = generator.generate(match_result)

    assert summary.missing_requirements == ["Background Check", "Drug Test"]
    assert any(item == "Missing requirement: Background Check" for item in summary.concerns)
    assert any(item == "Missing requirement: Drug Test" for item in summary.concerns)


def test_deterministic_repeated_summaries() -> None:
    generator = RecruiterSummaryGenerator()
    match_result = MatchResult(
        overall_match_percentage=82.0,
        confidence=0.72,
        recommendation="ADVANCE_TO_PHONE_SCREEN",
        strengths=["Delivery Experience", "Skill Match"],
        missing_requirements=["Certification Requirement"],
        unknown_requirements=["Unmapped Requirement"],
        warnings=["Resume profile missing optional city"],
    )

    first = generator.generate(match_result)
    second = generator.generate(match_result)

    assert first.headline == second.headline
    assert first.summary == second.summary
    assert first.strengths == second.strengths
    assert first.concerns == second.concerns
    assert first.missing_requirements == second.missing_requirements
    assert first.recommendation == second.recommendation
    assert first.confidence == second.confidence
