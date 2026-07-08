from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class RequirementMatch:
    """Represents one deterministic requirement-to-candidate comparison."""

    requirement_name: str
    required: bool
    candidate_value: object
    expected_value: object
    matched: bool
    confidence: float
    notes: str | None = None


@dataclass(slots=True)
class MatchResult:
    """Framework result for candidate matching without scoring or recommendation logic."""

    overall_match_percentage: float = 0.0
    strengths: list[str] = field(default_factory=list)
    missing_requirements: list[str] = field(default_factory=list)
    preferred_requirements: list[str] = field(default_factory=list)
    preferred_matches: list[str] = field(default_factory=list)
    unknown_requirements: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    hard_requirement_passed: bool = True
    hard_requirement_failures: list[str] = field(default_factory=list)
    confidence: float = 0.0
    recommendation: str | None = None
    requirement_matches: list[RequirementMatch] = field(default_factory=list)
