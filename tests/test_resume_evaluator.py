import json
from pathlib import Path
from types import SimpleNamespace

from services.resume_evaluator import ResumeEvaluator


class DummyClient:
    def __init__(self, payload=None, error=None) -> None:
        self.payload = payload
        self.error = error

    @property
    def chat(self) -> "DummyClient":
        return self

    @property
    def completions(self) -> "DummyClient":
        return self

    def create(self, **kwargs):
        if self.error is not None:
            raise self.error

        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(self.payload)))]
        )


class OpenAIValidationSettings:
    openai_api_key = ""
    openai_model = "gpt-4o-mini"

    def validate_openai_settings(self) -> None:
        raise ValueError("Missing required settings: openai_api_key")


def test_resume_evaluator_persists_structured_result(tmp_path: Path) -> None:
    evaluator = ResumeEvaluator(
        database_url=f"sqlite:///{tmp_path / 'evaluations.db'}",
        client=DummyClient(
            payload={
                "summary": "Strong Python background",
                "strengths": ["Python", "SQL"],
                "weaknesses": ["Limited leadership experience"],
                "recommended_interview_questions": ["Tell me about your system design experience"],
                "suggested_hiring_decision": "Proceed with interview",
            }
        ),
        settings=SimpleNamespace(openai_api_key="test-key", openai_model="gpt-4o-mini"),
    )

    result = evaluator.evaluate_resume(
        applicant_id=7,
        resume_text="Jane Doe has 5 years of Python and SQL experience.",
        candidate_name="Jane Doe",
    )

    assert result["summary"] == "Strong Python background"
    assert result["strengths"] == ["Python", "SQL"]
    assert result["weaknesses"] == ["Limited leadership experience"]
    assert result["recommended_interview_questions"] == ["Tell me about your system design experience"]
    assert result["suggested_hiring_decision"] == "Proceed with interview"
    assert len(evaluator.list_evaluations()) == 1


def test_resume_evaluator_handles_api_failure_gracefully(tmp_path: Path) -> None:
    evaluator = ResumeEvaluator(
        database_url=f"sqlite:///{tmp_path / 'evaluations.db'}",
        client=DummyClient(error=RuntimeError("API unavailable")),
        settings=SimpleNamespace(openai_api_key="", openai_model="gpt-4o-mini"),
    )

    result = evaluator.evaluate_resume(resume_text="Sample resume text")

    assert result["summary"] == "Evaluation unavailable due to an API error."
    assert result["strengths"] == []
    assert result["weaknesses"] == []
    assert result["recommended_interview_questions"] == []
    assert result["suggested_hiring_decision"] == "Hold"
    assert result["error"] == "API unavailable"
    assert len(evaluator.list_evaluations()) == 1


def test_resume_evaluator_validates_openai_settings_when_ai_is_used(tmp_path: Path) -> None:
    evaluator = ResumeEvaluator(
        database_url=f"sqlite:///{tmp_path / 'evaluations.db'}",
        settings=OpenAIValidationSettings(),
    )

    result = evaluator.evaluate_resume(resume_text="Sample resume text")

    assert result["status"] == "failed"
    assert "openai_api_key" in result["error"]
