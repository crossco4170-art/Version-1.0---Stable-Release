from __future__ import annotations

from models.job_order import JobOrder
from services.ai.candidate_matcher import CandidateMatcher
from services.ai.models import MatchResult, RequirementMatch
from services.ai.resume_parser import ResumeProfile


def _build_job_order(
    *,
    title: str = "Delivery Driver",
    description: str = "CDL required for regional delivery routes",
    work_location: str = "Milwaukee, WI",
) -> JobOrder:
    return JobOrder(
        organization_id=1,
        client_id=1,
        job_code="JOB-2026-001",
        title=title,
        description=description,
        work_location=work_location,
    )


def test_requirement_match_creation() -> None:
    requirement = RequirementMatch(
        requirement_name="CDL Requirement",
        required=True,
        candidate_value=True,
        expected_value=True,
        matched=True,
        confidence=1.0,
        notes="Candidate holds CDL",
    )

    assert requirement.requirement_name == "CDL Requirement"
    assert requirement.required is True
    assert requirement.matched is True
    assert requirement.confidence == 1.0


def test_match_result_creation() -> None:
    result = MatchResult()

    assert result.overall_match_percentage == 0.0
    assert result.confidence == 0.0
    assert result.recommendation is None
    assert result.requirement_matches == []


def test_candidate_matcher_compare_returns_match_result() -> None:
    matcher = CandidateMatcher()
    profile = ResumeProfile(
        full_name="Jane Doe",
        email="jane@example.com",
        phone="555-0101",
        city="Milwaukee",
        state="WI",
        job_titles=["Delivery Driver"],
        delivery_experience=True,
        management_experience=False,
        cdl=True,
    )
    job_order = _build_job_order()

    result = matcher.compare(profile, job_order)

    assert isinstance(result, MatchResult)
    assert result.overall_match_percentage == 0.0
    assert result.recommendation is None
    assert len(result.requirement_matches) > 0


def test_empty_resume_handling() -> None:
    matcher = CandidateMatcher()
    profile = ResumeProfile()
    job_order = _build_job_order()

    result = matcher.compare(profile, job_order)

    assert "Resume profile is missing core candidate data" in result.warnings
    assert "Email Available" in result.missing_requirements
    assert "Phone Available" in result.missing_requirements


def test_empty_job_order_handling() -> None:
    matcher = CandidateMatcher()
    profile = ResumeProfile(full_name="Jane Doe", email="jane@example.com", phone="555-0101")
    job_order = _build_job_order(title="", description="", work_location="")

    result = matcher.compare(profile, job_order)

    assert "Job order is missing structured requirement details" in result.warnings


def test_missing_requirement_recording() -> None:
    matcher = CandidateMatcher()
    profile = ResumeProfile(
        full_name="Jane Doe",
        email="jane@example.com",
        phone="555-0101",
        city="Milwaukee",
        state="WI",
        job_titles=["Warehouse Associate"],
        delivery_experience=False,
        cdl=False,
    )
    job_order = _build_job_order()

    result = matcher.compare(profile, job_order)

    assert "Job Title Alignment" in result.missing_requirements
    assert "Delivery Experience" in result.missing_requirements
    assert "CDL Requirement" in result.missing_requirements


def test_structured_comparison_output() -> None:
    matcher = CandidateMatcher()
    profile = ResumeProfile(
        full_name="Jane Doe",
        email="jane@example.com",
        phone="555-0101",
        city="Milwaukee",
        state="WI",
        job_titles=["Delivery Driver"],
        delivery_experience=True,
        management_experience=True,
        cdl=True,
    )
    job_order = _build_job_order(description="CDL required. Driver lead preferred.")

    result = matcher.compare(profile, job_order)

    assert all(isinstance(item, RequirementMatch) for item in result.requirement_matches)
    assert any(item.requirement_name == "CDL Requirement" for item in result.requirement_matches)
    assert any(item.requirement_name == "Location Alignment" for item in result.requirement_matches)
    assert result.overall_match_percentage == 0.0
