from __future__ import annotations

from dataclasses import dataclass, field

from services.ai.models import MatchResult


@dataclass(slots=True)
class ScoringProfile:
    """Configurable deterministic scoring profile for candidate matching."""

    hard_requirements: float = 0.0
    delivery_experience: float = 0.0
    education: float = 0.0
    certifications: float = 0.0
    licenses: float = 0.0
    skills: float = 0.0
    management_experience: float = 0.0
    military_experience: float = 0.0
    soft_skills: float = 0.0

    factor_by_requirement: dict[str, str] = field(default_factory=dict)
    hard_requirement_names: set[str] = field(default_factory=set)

    confidence_evidence_weight: float = 0.0
    confidence_match_weight: float = 0.0
    confidence_known_weight: float = 0.0

    def factor_weights(self) -> dict[str, float]:
        return {
            "hard_requirements": self.hard_requirements,
            "delivery_experience": self.delivery_experience,
            "education": self.education,
            "certifications": self.certifications,
            "licenses": self.licenses,
            "skills": self.skills,
            "management_experience": self.management_experience,
            "military_experience": self.military_experience,
            "soft_skills": self.soft_skills,
        }


class ScoringEngine:
    """Deterministic scoring engine for completed match results."""

    def score(self, match_result: MatchResult, scoring_profile: ScoringProfile) -> MatchResult:
        if not match_result.requirement_matches:
            match_result.overall_match_percentage = 0.0
            match_result.confidence = 0.0
            match_result.hard_requirement_passed = True
            match_result.hard_requirement_failures = []
            match_result.strengths = []
            match_result.preferred_matches = []
            match_result.preferred_requirements = []
            match_result.missing_requirements = []
            match_result.unknown_requirements = []
            return match_result

        factor_weights = scoring_profile.factor_weights()
        total_weight = 0.0
        matched_weight = 0.0

        strengths: list[str] = []
        preferred_matches: list[str] = []
        preferred_requirements: list[str] = []
        missing_requirements: list[str] = []
        unknown_requirements: list[str] = []
        hard_requirement_failures: list[str] = []

        known_requirement_count = 0
        matched_requirement_count = 0
        evidence_count = 0

        for requirement in match_result.requirement_matches:
            requirement_name = requirement.requirement_name
            factor_name = scoring_profile.factor_by_requirement.get(requirement_name)
            factor_weight = factor_weights.get(factor_name, 0.0) if factor_name else 0.0

            candidate_has_evidence = self._has_evidence(requirement.candidate_value)
            if candidate_has_evidence:
                evidence_count += 1

            if factor_name is None:
                unknown_requirements.append(requirement_name)
            else:
                known_requirement_count += 1
                total_weight += factor_weight
                if requirement.matched:
                    matched_requirement_count += 1
                    matched_weight += factor_weight

            if requirement.matched:
                strengths.append(requirement_name)
                if not requirement.required:
                    preferred_matches.append(requirement_name)
            else:
                if requirement.required:
                    missing_requirements.append(requirement_name)
                else:
                    preferred_requirements.append(requirement_name)

            is_hard_requirement = requirement.required or (requirement_name in scoring_profile.hard_requirement_names)
            if is_hard_requirement and not requirement.matched:
                hard_requirement_failures.append(requirement_name)

        score_percentage = 0.0
        if total_weight > 0.0:
            score_percentage = (matched_weight / total_weight) * 100.0

        match_result.overall_match_percentage = round(score_percentage, 2)
        match_result.hard_requirement_failures = self._unique(hard_requirement_failures)
        match_result.hard_requirement_passed = len(match_result.hard_requirement_failures) == 0
        match_result.strengths = self._unique(strengths)
        match_result.preferred_matches = self._unique(preferred_matches)
        match_result.preferred_requirements = self._unique(preferred_requirements)
        match_result.missing_requirements = self._unique(missing_requirements)
        match_result.unknown_requirements = self._unique(unknown_requirements)
        match_result.confidence = self._calculate_confidence(
            total_requirements=len(match_result.requirement_matches),
            evidence_count=evidence_count,
            known_count=known_requirement_count,
            matched_count=matched_requirement_count,
            profile=scoring_profile,
        )

        return match_result

    def _calculate_confidence(
        self,
        *,
        total_requirements: int,
        evidence_count: int,
        known_count: int,
        matched_count: int,
        profile: ScoringProfile,
    ) -> float:
        if total_requirements == 0:
            return 0.0

        evidence_ratio = evidence_count / total_requirements
        match_ratio = (matched_count / known_count) if known_count > 0 else 0.0
        known_ratio = known_count / total_requirements

        weighted_sum = (
            evidence_ratio * profile.confidence_evidence_weight
            + match_ratio * profile.confidence_match_weight
            + known_ratio * profile.confidence_known_weight
        )
        total_weight = (
            profile.confidence_evidence_weight
            + profile.confidence_match_weight
            + profile.confidence_known_weight
        )
        if total_weight <= 0.0:
            return 0.0

        confidence = weighted_sum / total_weight
        return round(max(0.0, min(1.0, confidence)), 4)

    def _has_evidence(self, value: object) -> bool:
        if value is None:
            return False
        if isinstance(value, str):
            return bool(value.strip())
        if isinstance(value, (list, tuple, set, dict)):
            return len(value) > 0
        return True

    def _unique(self, items: list[str]) -> list[str]:
        seen: set[str] = set()
        output: list[str] = []
        for item in items:
            key = item.lower()
            if key in seen:
                continue
            seen.add(key)
            output.append(item)
        return output
