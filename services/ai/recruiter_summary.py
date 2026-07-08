from __future__ import annotations

from dataclasses import dataclass, field

from services.ai.models import MatchResult


@dataclass(slots=True)
class RecruiterSummary:
    """Deterministic recruiter-facing summary generated from MatchResult."""

    headline: str
    summary: str
    strengths: list[str] = field(default_factory=list)
    concerns: list[str] = field(default_factory=list)
    missing_requirements: list[str] = field(default_factory=list)
    recommendation: str = "HOLD"
    confidence: float = 0.0


class RecruiterSummaryGenerator:
    """Builds deterministic natural-language summaries without AI or randomness."""

    def generate(self, match_result: MatchResult) -> RecruiterSummary:
        recommendation = match_result.recommendation or "HOLD"
        confidence = round(float(match_result.confidence or 0.0), 4)
        score = round(float(match_result.overall_match_percentage or 0.0), 2)

        missing_requirements = self._unique(match_result.missing_requirements)
        strengths = self._unique(match_result.strengths)
        concerns = self._build_concerns(match_result)

        headline = self._build_headline(match_result, recommendation)
        summary = self._build_summary(
            recommendation=recommendation,
            score=score,
            confidence=confidence,
            strengths=strengths,
            concerns=concerns,
            missing_requirements=missing_requirements,
            hard_failures=self._unique(match_result.hard_requirement_failures),
        )

        return RecruiterSummary(
            headline=headline,
            summary=summary,
            strengths=strengths,
            concerns=concerns,
            missing_requirements=missing_requirements,
            recommendation=recommendation,
            confidence=confidence,
        )

    def _build_headline(self, match_result: MatchResult, recommendation: str) -> str:
        if match_result.hard_requirement_failures:
            return "Hard requirement failure blocks advancement"

        mapping = {
            "ADVANCE_TO_CLIENT": "Excellent fit ready for client submission",
            "ADVANCE_TO_PHONE_SCREEN": "Strong fit ready for phone screen",
            "RECRUITER_REVIEW": "Borderline fit requires recruiter review",
            "HOLD": "Candidate on hold pending additional validation",
            "DO_NOT_ADVANCE": "Candidate does not meet advancement threshold",
        }
        return mapping.get(recommendation, "Candidate requires recruiter evaluation")

    def _build_summary(
        self,
        *,
        recommendation: str,
        score: float,
        confidence: float,
        strengths: list[str],
        concerns: list[str],
        missing_requirements: list[str],
        hard_failures: list[str],
    ) -> str:
        parts: list[str] = [
            f"Recommendation: {recommendation}.",
            f"Match score: {score:.2f}%.",
            f"Confidence: {confidence:.4f}.",
        ]

        if strengths:
            top_strengths = ", ".join(strengths[:3])
            parts.append(f"Primary match reasons: {top_strengths}.")
        else:
            parts.append("No positive match strengths were recorded.")

        if hard_failures:
            parts.append(f"Hard requirement failures: {', '.join(hard_failures)}.")

        if missing_requirements:
            parts.append(f"Missing requirements: {', '.join(missing_requirements)}.")

        unknown = [item for item in concerns if item.startswith("Unknown requirement:")]
        if unknown:
            parts.append("Unknown requirements reduced certainty but did not auto-reject the candidate.")

        if concerns:
            parts.append(f"Key concerns: {', '.join(concerns[:4])}.")

        return " ".join(parts)

    def _build_concerns(self, match_result: MatchResult) -> list[str]:
        concerns: list[str] = []

        for failure in self._unique(match_result.hard_requirement_failures):
            concerns.append(f"Hard requirement failure: {failure}")

        for requirement in self._unique(match_result.missing_requirements):
            concerns.append(f"Missing requirement: {requirement}")

        for requirement in self._unique(match_result.unknown_requirements):
            concerns.append(f"Unknown requirement: {requirement}")

        for warning in self._unique(match_result.warnings):
            concerns.append(f"Warning: {warning}")

        return concerns

    def _unique(self, items: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for item in items:
            cleaned = item.strip()
            if not cleaned:
                continue
            key = cleaned.lower()
            if key in seen:
                continue
            seen.add(key)
            result.append(cleaned)
        return result
