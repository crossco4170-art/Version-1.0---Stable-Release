from __future__ import annotations

import pytest

from models.job_order import JobOrder
from services.ai.recruiting_ai_service import EvaluationResult, RecruitingAIService
from services.ai.scoring_engine import ScoringProfile
from utils.exceptions import BlackcrestInputError


def _build_job_order() -> JobOrder:
    return JobOrder(
        organization_id=1,
        client_id=1,
        job_code="JOB-2026-DET-001",
        title="Delivery Driver",
        description="CDL required for regional delivery routes",
        work_location="Milwaukee, WI",
    )


def _build_scoring_profile() -> ScoringProfile:
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
            "Delivery Experience": "delivery_experience",
            "Skill Match": "skills",
            "Management Experience": "management_experience",
            "Location Alignment": "soft_skills",
            "Email Available": "hard_requirements",
            "Phone Available": "hard_requirements",
            "Job Title Alignment": "skills",
        },
        hard_requirement_names={
            "CDL Requirement",
            "Delivery Experience",
            "Email Available",
            "Phone Available",
        },
        confidence_evidence_weight=0.4,
        confidence_match_weight=0.4,
        confidence_known_weight=0.2,
    )


def _build_resume_text() -> str:
    return """
    Jane Doe
    Milwaukee, WI
    Email: jane.doe@example.com
    Phone: (414) 555-0101
    Skills: Logistics, Route Planning, Customer Service
    Senior Delivery Driver - Acme Logistics (2019-Present)
    Licenses: CDL Class A
    6 years experience in delivery operations
    """


def test_successful_end_to_end_evaluation() -> None:
    service = RecruitingAIService()

    evaluation = service.evaluate_candidate(
        resume_text=_build_resume_text(),
        job_order=_build_job_order(),
        scoring_profile=_build_scoring_profile(),
    )

    assert isinstance(evaluation, EvaluationResult)
    assert evaluation.resume_profile.email == "jane.doe@example.com"
    assert evaluation.match_result.overall_match_percentage >= 0.0
    assert evaluation.recruiter_summary.recommendation == evaluation.match_result.recommendation


def test_empty_resume_handling() -> None:
    service = RecruitingAIService()

    with pytest.raises(BlackcrestInputError):
        service.evaluate_candidate(
            resume_text="   ",
            job_order=_build_job_order(),
            scoring_profile=_build_scoring_profile(),
        )


def test_invalid_job_order_handling() -> None:
    service = RecruitingAIService()

    with pytest.raises(BlackcrestInputError):
        service.evaluate_candidate(
            resume_text=_build_resume_text(),
            job_order=None,  # type: ignore[arg-type]
            scoring_profile=_build_scoring_profile(),
        )


def test_deterministic_repeated_evaluations() -> None:
    service = RecruitingAIService()
    job_order = _build_job_order()
    scoring_profile = _build_scoring_profile()
    resume_text = _build_resume_text()

    first = service.evaluate_candidate(resume_text, job_order, scoring_profile)
    second = service.evaluate_candidate(resume_text, job_order, scoring_profile)

    assert first.resume_profile == second.resume_profile
    assert first.match_result == second.match_result
    assert first.recruiter_summary == second.recruiter_summary


def test_summary_matches_recommendation() -> None:
    service = RecruitingAIService()

    evaluation = service.evaluate_candidate(
        resume_text=_build_resume_text(),
        job_order=_build_job_order(),
        scoring_profile=_build_scoring_profile(),
    )

    assert evaluation.recruiter_summary.recommendation == evaluation.match_result.recommendation


def test_match_result_preserved() -> None:
    service = RecruitingAIService()

    evaluation = service.evaluate_candidate(
        resume_text=_build_resume_text(),
        job_order=_build_job_order(),
        scoring_profile=_build_scoring_profile(),
    )

    assert len(evaluation.match_result.requirement_matches) > 0
    assert isinstance(evaluation.match_result.hard_requirement_passed, bool)
    assert isinstance(evaluation.match_result.overall_match_percentage, float)


def test_resume_profile_preserved() -> None:
    service = RecruitingAIService()

    evaluation = service.evaluate_candidate(
        resume_text=_build_resume_text(),
        job_order=_build_job_order(),
        scoring_profile=_build_scoring_profile(),
    )

    assert evaluation.resume_profile.full_name == "Jane Doe"
    assert evaluation.resume_profile.cdl is True
    assert evaluation.resume_profile.delivery_experience is True
