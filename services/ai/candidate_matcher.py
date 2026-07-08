from __future__ import annotations

from models.job_order import JobOrder
from services.ai.models import MatchResult, RequirementMatch
from services.ai.resume_parser import ResumeProfile


class CandidateMatcher:
    """Deterministic comparison framework between a resume profile and a job order."""

    def compare(self, resume_profile: ResumeProfile, job_order: JobOrder) -> MatchResult:
        result = MatchResult(
            overall_match_percentage=0.0,
            confidence=0.0,
            recommendation=None,
        )

        if not isinstance(resume_profile, ResumeProfile):
            result.warnings.append("Resume profile input is invalid")
            return result

        if not isinstance(job_order, JobOrder):
            result.warnings.append("Job order input is invalid")
            return result

        if not (resume_profile.full_name or resume_profile.email or resume_profile.phone):
            result.warnings.append("Resume profile is missing core candidate data")

        job_title = (job_order.title or "").strip()
        job_description = (job_order.description or "").strip()
        job_location = (job_order.work_location or "").strip()
        job_text = " ".join([job_title, job_description]).strip().lower()

        if not (job_title or job_description or job_location):
            result.warnings.append("Job order is missing structured requirement details")

        self._record_contact_matches(result, resume_profile)
        self._record_title_match(result, resume_profile, job_title)
        self._record_location_match(result, resume_profile, job_location)
        self._record_delivery_match(result, resume_profile, job_text)
        self._record_management_match(result, resume_profile, job_text)
        self._record_cdl_match(result, resume_profile, job_text)

        return result

    def _append_match(self, result: MatchResult, match: RequirementMatch) -> None:
        result.requirement_matches.append(match)

        if match.matched:
            result.strengths.append(match.requirement_name)
        elif match.required:
            result.missing_requirements.append(match.requirement_name)
        else:
            result.preferred_requirements.append(match.requirement_name)

    def _record_contact_matches(self, result: MatchResult, resume_profile: ResumeProfile) -> None:
        self._append_match(
            result,
            RequirementMatch(
                requirement_name="Email Available",
                required=True,
                candidate_value=resume_profile.email,
                expected_value="present",
                matched=bool(resume_profile.email),
                confidence=1.0,
                notes="Candidate email availability check",
            ),
        )

        self._append_match(
            result,
            RequirementMatch(
                requirement_name="Phone Available",
                required=True,
                candidate_value=resume_profile.phone,
                expected_value="present",
                matched=bool(resume_profile.phone),
                confidence=1.0,
                notes="Candidate phone availability check",
            ),
        )

    def _record_title_match(self, result: MatchResult, resume_profile: ResumeProfile, job_title: str) -> None:
        if not job_title:
            return

        candidate_titles = [title.strip() for title in resume_profile.job_titles if title.strip()]
        lowered_job_title = job_title.lower()
        matched = any(lowered_job_title in title.lower() or title.lower() in lowered_job_title for title in candidate_titles)

        self._append_match(
            result,
            RequirementMatch(
                requirement_name="Job Title Alignment",
                required=True,
                candidate_value=candidate_titles,
                expected_value=job_title,
                matched=matched,
                confidence=1.0,
                notes="Compares prior titles to job title text",
            ),
        )

    def _record_location_match(self, result: MatchResult, resume_profile: ResumeProfile, job_location: str) -> None:
        if not job_location:
            return

        parts = [part.strip() for part in job_location.split(",") if part.strip()]
        expected_city = parts[0].lower() if parts else ""
        expected_state = parts[1].lower() if len(parts) > 1 else ""

        candidate_city = (resume_profile.city or "").strip().lower()
        candidate_state = (resume_profile.state or "").strip().lower()

        city_ok = bool(expected_city) and candidate_city == expected_city
        state_ok = bool(expected_state) and candidate_state == expected_state

        if expected_city and expected_state:
            matched = city_ok and state_ok
        elif expected_city:
            matched = city_ok
        elif expected_state:
            matched = state_ok
        else:
            matched = False

        self._append_match(
            result,
            RequirementMatch(
                requirement_name="Location Alignment",
                required=False,
                candidate_value={"city": resume_profile.city, "state": resume_profile.state},
                expected_value=job_location,
                matched=matched,
                confidence=1.0,
                notes="Compares candidate city/state with job location",
            ),
        )

    def _record_delivery_match(self, result: MatchResult, resume_profile: ResumeProfile, job_text: str) -> None:
        if not self._text_has_any(job_text, "delivery", "driver", "route", "logistics"):
            return

        self._append_match(
            result,
            RequirementMatch(
                requirement_name="Delivery Experience",
                required=True,
                candidate_value=resume_profile.delivery_experience,
                expected_value=True,
                matched=bool(resume_profile.delivery_experience),
                confidence=1.0,
                notes="Delivery experience required by job text",
            ),
        )

    def _record_management_match(self, result: MatchResult, resume_profile: ResumeProfile, job_text: str) -> None:
        if not self._text_has_any(job_text, "manager", "management", "supervisor", "lead"):
            return

        self._append_match(
            result,
            RequirementMatch(
                requirement_name="Management Experience",
                required=False,
                candidate_value=resume_profile.management_experience,
                expected_value=True,
                matched=bool(resume_profile.management_experience),
                confidence=1.0,
                notes="Management preference inferred from job text",
            ),
        )

    def _record_cdl_match(self, result: MatchResult, resume_profile: ResumeProfile, job_text: str) -> None:
        if not self._text_has_any(job_text, "cdl", "commercial driver license"):
            return

        self._append_match(
            result,
            RequirementMatch(
                requirement_name="CDL Requirement",
                required=True,
                candidate_value=resume_profile.cdl,
                expected_value=True,
                matched=bool(resume_profile.cdl),
                confidence=1.0,
                notes="CDL requirement inferred from job text",
            ),
        )

    def _text_has_any(self, text: str, *terms: str) -> bool:
        lowered = text.lower()
        return any(term in lowered for term in terms)
