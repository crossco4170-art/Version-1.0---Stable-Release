from __future__ import annotations

from services.ai.models import MatchResult, RequirementMatch
from services.ai.scoring_engine import ScoringEngine, ScoringProfile


def _profile() -> ScoringProfile:
    return ScoringProfile(
        hard_requirements=0.35,
        delivery_experience=0.15,
        education=0.1,
        certifications=0.1,
        licenses=0.1,
        skills=0.1,
        management_experience=0.05,
        military_experience=0.03,
        soft_skills=0.02,
        factor_by_requirement={
            "CDL Requirement": "hard_requirements",
            "Background Check": "hard_requirements",
            "Drug Test": "hard_requirements",
            "Delivery Experience": "delivery_experience",
            "Education Requirement": "education",
            "Certification Requirement": "certifications",
            "Driver License": "licenses",
            "Skill Match": "skills",
            "Management Experience": "management_experience",
            "Military Experience": "military_experience",
            "Communication": "soft_skills",
        },
        hard_requirement_names={
            "CDL Requirement",
            "Driver License",
            "High School Diploma",
            "Minimum Age",
            "Drug Test",
            "Background Check",
            "Delivery Experience",
        },
        confidence_evidence_weight=0.4,
        confidence_match_weight=0.4,
        confidence_known_weight=0.2,
    )


def _base_result() -> MatchResult:
    return MatchResult(
        requirement_matches=[
            RequirementMatch(
                requirement_name="CDL Requirement",
                required=True,
                candidate_value=True,
                expected_value=True,
                matched=True,
                confidence=1.0,
            ),
            RequirementMatch(
                requirement_name="Delivery Experience",
                required=True,
                candidate_value=True,
                expected_value=True,
                matched=True,
                confidence=1.0,
            ),
            RequirementMatch(
                requirement_name="Skill Match",
                required=False,
                candidate_value=["Route Planning"],
                expected_value=["Route Planning"],
                matched=True,
                confidence=1.0,
            ),
            RequirementMatch(
                requirement_name="Management Experience",
                required=False,
                candidate_value=False,
                expected_value=True,
                matched=False,
                confidence=1.0,
            ),
        ]
    )


def test_scoring_profile_creation() -> None:
    profile = _profile()

    assert profile.hard_requirements == 0.35
    assert profile.factor_by_requirement["CDL Requirement"] == "hard_requirements"
    assert "Minimum Age" in profile.hard_requirement_names


def test_score_calculation() -> None:
    engine = ScoringEngine()
    profile = _profile()
    result = _base_result()

    scored = engine.score(result, profile)

    assert scored.overall_match_percentage > 0.0
    assert scored.overall_match_percentage <= 100.0
    assert "CDL Requirement" in scored.strengths
    assert "Management Experience" in scored.preferred_requirements


def test_hard_requirement_failures() -> None:
    engine = ScoringEngine()
    profile = _profile()
    result = MatchResult(
        requirement_matches=[
            RequirementMatch(
                requirement_name="Background Check",
                required=True,
                candidate_value=False,
                expected_value=True,
                matched=False,
                confidence=1.0,
            ),
            RequirementMatch(
                requirement_name="Drug Test",
                required=True,
                candidate_value=False,
                expected_value=True,
                matched=False,
                confidence=1.0,
            ),
        ]
    )

    scored = engine.score(result, profile)

    assert scored.hard_requirement_passed is False
    assert "Background Check" in scored.hard_requirement_failures
    assert "Drug Test" in scored.hard_requirement_failures


def test_preferred_requirement_scoring() -> None:
    engine = ScoringEngine()
    profile = _profile()
    result = MatchResult(
        requirement_matches=[
            RequirementMatch(
                requirement_name="Communication",
                required=False,
                candidate_value=True,
                expected_value=True,
                matched=True,
                confidence=1.0,
            ),
            RequirementMatch(
                requirement_name="Management Experience",
                required=False,
                candidate_value=False,
                expected_value=True,
                matched=False,
                confidence=1.0,
            ),
        ]
    )

    scored = engine.score(result, profile)

    assert "Communication" in scored.preferred_matches
    assert "Management Experience" in scored.preferred_requirements


def test_confidence_calculation() -> None:
    engine = ScoringEngine()
    profile = _profile()
    result = _base_result()

    scored = engine.score(result, profile)

    assert 0.0 <= scored.confidence <= 1.0
    assert scored.confidence > 0.0


def test_unknown_requirement_handling() -> None:
    engine = ScoringEngine()
    profile = _profile()
    result = MatchResult(
        requirement_matches=[
            RequirementMatch(
                requirement_name="Unmapped Requirement",
                required=False,
                candidate_value="some data",
                expected_value="expected",
                matched=False,
                confidence=1.0,
            )
        ]
    )

    scored = engine.score(result, profile)

    assert "Unmapped Requirement" in scored.unknown_requirements
    assert scored.overall_match_percentage == 0.0


def test_empty_match_result() -> None:
    engine = ScoringEngine()
    profile = _profile()

    scored = engine.score(MatchResult(), profile)

    assert scored.overall_match_percentage == 0.0
    assert scored.confidence == 0.0
    assert scored.hard_requirement_passed is True


def test_zero_weight_profile() -> None:
    engine = ScoringEngine()
    profile = ScoringProfile(
        factor_by_requirement={"CDL Requirement": "hard_requirements"},
        hard_requirement_names={"CDL Requirement"},
        confidence_evidence_weight=0.0,
        confidence_match_weight=0.0,
        confidence_known_weight=0.0,
    )
    result = MatchResult(
        requirement_matches=[
            RequirementMatch(
                requirement_name="CDL Requirement",
                required=True,
                candidate_value=True,
                expected_value=True,
                matched=True,
                confidence=1.0,
            )
        ]
    )

    scored = engine.score(result, profile)

    assert scored.overall_match_percentage == 0.0
    assert scored.confidence == 0.0


def test_deterministic_repeated_scoring() -> None:
    engine = ScoringEngine()
    profile = _profile()

    first = engine.score(_base_result(), profile)
    second = engine.score(_base_result(), profile)

    assert first.overall_match_percentage == second.overall_match_percentage
    assert first.confidence == second.confidence
    assert first.hard_requirement_passed == second.hard_requirement_passed
    assert first.hard_requirement_failures == second.hard_requirement_failures
    assert first.strengths == second.strengths
    assert first.preferred_matches == second.preferred_matches
    assert first.preferred_requirements == second.preferred_requirements
    assert first.missing_requirements == second.missing_requirements
    assert first.unknown_requirements == second.unknown_requirements
