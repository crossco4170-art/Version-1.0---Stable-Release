from __future__ import annotations

from dataclasses import dataclass

from models.job_order import JobOrder
from services.ai.candidate_matcher import CandidateMatcher
from services.ai.models import MatchResult
from services.ai.recommendation_engine import RecommendationEngine
from services.ai.recruiter_summary import RecruiterSummary, RecruiterSummaryGenerator
from services.ai.resume_parser import ResumeParser, ResumeProfile
from services.ai.scoring_engine import ScoringEngine, ScoringProfile
from utils.exceptions import BlackcrestInputError


@dataclass(slots=True)
class EvaluationResult:
    """Aggregated deterministic AI evaluation output for one candidate and job."""

    resume_profile: ResumeProfile
    match_result: MatchResult
    recruiter_summary: RecruiterSummary


class RecruitingAIService:
    """Orchestrates deterministic parsing, matching, scoring, recommendation, and summary generation."""

    def __init__(
        self,
        *,
        resume_parser: ResumeParser | None = None,
        candidate_matcher: CandidateMatcher | None = None,
        scoring_engine: ScoringEngine | None = None,
        recommendation_engine: RecommendationEngine | None = None,
        recruiter_summary_generator: RecruiterSummaryGenerator | None = None,
    ) -> None:
        self.resume_parser = resume_parser or ResumeParser()
        self.candidate_matcher = candidate_matcher or CandidateMatcher()
        self.scoring_engine = scoring_engine or ScoringEngine()
        self.recommendation_engine = recommendation_engine or RecommendationEngine()
        self.recruiter_summary_generator = recruiter_summary_generator or RecruiterSummaryGenerator()

    def evaluate_candidate(
        self,
        resume_text: str,
        job_order: JobOrder,
        scoring_profile: ScoringProfile,
    ) -> EvaluationResult:
        if not isinstance(resume_text, str) or not resume_text.strip():
            raise BlackcrestInputError("Resume text is required")
        if not isinstance(job_order, JobOrder):
            raise BlackcrestInputError("Job order is invalid")
        if not isinstance(scoring_profile, ScoringProfile):
            raise BlackcrestInputError("Scoring profile is invalid")

        resume_profile = self.resume_parser.parse(resume_text)
        match_result = self.candidate_matcher.compare(resume_profile, job_order)
        match_result = self.scoring_engine.score(match_result, scoring_profile)
        match_result = self.recommendation_engine.recommend(match_result)
        recruiter_summary = self.recruiter_summary_generator.generate(match_result)

        return EvaluationResult(
            resume_profile=resume_profile,
            match_result=match_result,
            recruiter_summary=recruiter_summary,
        )
