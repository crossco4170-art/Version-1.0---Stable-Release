from __future__ import annotations

from pathlib import Path

from services.ai.resume_parser import ResumeParser, ResumeProfile
from services.resume_processor import ResumeProcessor
from utils.exceptions import BlackcrestInputError


class AIResumeIntelligenceService:
    """Offline resume intelligence layer that extracts structured profile fields."""

    def __init__(self, *, parser: ResumeParser | None = None, database_url: str | None = None) -> None:
        self.parser = parser or ResumeParser()
        # Reuse existing resume extraction pipeline for file handling.
        self._resume_processor = ResumeProcessor(database_url=database_url)

    def analyze_resume_text(self, resume_text: str) -> ResumeProfile:
        """Parse resume text into a structured profile without scoring."""
        return self.parser.parse(resume_text)

    def analyze_resume_file(self, resume_path: str | Path) -> ResumeProfile:
        """Extract and parse one resume file from disk into a structured profile."""
        path = Path(resume_path)
        if not path.exists():
            raise FileNotFoundError(f"Resume file not found: {path}")

        extracted_text = self._resume_processor._extract_text(path)
        if not extracted_text.strip():
            raise BlackcrestInputError("Resume content is empty")

        return self.parser.parse(extracted_text)
