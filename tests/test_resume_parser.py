from __future__ import annotations

import pytest

from services.ai.resume_parser import ResumeParser
from utils.exceptions import BlackcrestInputError


@pytest.fixture
def parser() -> ResumeParser:
    return ResumeParser()


def test_extracts_contact_information(parser: ResumeParser) -> None:
    resume = """
    Jane Doe
    Milwaukee, WI
    Email: Jane.Doe@Example.com
    Phone: (414) 555-0101
    """

    profile = parser.parse(resume)

    assert profile.full_name == "Jane Doe"
    assert profile.email == "jane.doe@example.com"
    assert profile.phone == "(414) 555-0101"
    assert profile.city == "Milwaukee"
    assert profile.state == "WI"


def test_extracts_skills(parser: ResumeParser) -> None:
    resume = """
    Jane Doe
    Skills: Python, SQL, Leadership, Logistics
    """

    profile = parser.parse(resume)

    assert "Python" in profile.skills
    assert "SQL" in profile.skills
    assert "Leadership" in profile.skills
    assert "Logistics" in profile.skills


def test_extracts_employers_titles_and_dates(parser: ResumeParser) -> None:
    resume = """
    Jane Doe
    Senior Delivery Driver - Acme Logistics (2018-2022)
    Operations Supervisor - Blue Route Transport (2022-Present)
    """

    profile = parser.parse(resume)

    assert "Acme Logistics" in profile.employers
    assert "Blue Route Transport" in profile.employers
    assert "Senior Delivery Driver" in profile.job_titles
    assert "Operations Supervisor" in profile.job_titles
    assert "2018-2022" in profile.employment_dates
    assert "2022-Present" in profile.employment_dates


def test_extracts_education(parser: ResumeParser) -> None:
    resume = """
    Jane Doe
    Education: B.S. Business Administration, University of Wisconsin
    """

    profile = parser.parse(resume)

    assert any("University of Wisconsin" in item for item in profile.education)


def test_extracts_certifications(parser: ResumeParser) -> None:
    resume = """
    Jane Doe
    Certifications: OSHA 30, Lean Six Sigma Green Belt
    """

    profile = parser.parse(resume)

    assert "OSHA 30" in profile.certifications
    assert "Lean Six Sigma Green Belt" in profile.certifications


def test_extracts_licenses_and_cdl(parser: ResumeParser) -> None:
    resume = """
    Jane Doe
    Licenses: CDL Class A, Forklift Operator License
    """

    profile = parser.parse(resume)

    assert "CDL Class A" in profile.licenses
    assert profile.cdl is True


def test_detects_military_experience(parser: ResumeParser) -> None:
    resume = """
    Jane Doe
    U.S. Army Veteran with logistics coordination experience.
    """

    profile = parser.parse(resume)

    assert profile.military is True


def test_calculates_years_experience(parser: ResumeParser) -> None:
    resume = """
    Jane Doe
    8 years experience in logistics and delivery operations.
    """

    profile = parser.parse(resume)

    assert profile.years_experience == 8


def test_detects_delivery_and_management_experience(parser: ResumeParser) -> None:
    resume = """
    Jane Doe
    Managed a team of 12 drivers for regional package delivery routes.
    """

    profile = parser.parse(resume)

    assert profile.delivery_experience is True
    assert profile.management_experience is True


def test_handles_empty_resume(parser: ResumeParser) -> None:
    profile = parser.parse("   \n\n")

    assert profile.full_name is None
    assert profile.email is None
    assert profile.phone is None
    assert profile.skills == []
    assert profile.years_experience == 0
    assert profile.cdl is False
    assert profile.military is False


def test_rejects_invalid_resume_input(parser: ResumeParser) -> None:
    with pytest.raises(BlackcrestInputError):
        parser.parse(None)  # type: ignore[arg-type]
