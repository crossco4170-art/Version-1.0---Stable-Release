from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from database.connection import get_session
from models.resume_evaluation import ResumeEvaluation
from utils.exceptions import BlackcrestInputError, BlackcrestIntegrationError


class ResumeEvaluator:
    """Generate and store AI-based resume evaluations using the OpenAI API."""

    def __init__(
        self,
        *,
        session: Session | None = None,
        database_url: str | None = None,
        client: Any | None = None,
        settings: Any | None = None,
    ) -> None:
        self.session = session or get_session(database_url=database_url, ensure_schema=True)

        self.client = client
        self.settings = settings

    def evaluate_resume(
        self,
        *,
        applicant_id: int | None = None,
        resume_text: str,
        candidate_name: str | None = None,
    ) -> dict[str, Any]:
        if not resume_text or not str(resume_text).strip():
            raise BlackcrestInputError("Resume text is required")

        try:
            response_payload = self._request_ai_evaluation(resume_text=resume_text, candidate_name=candidate_name)
            result = self._normalize_result(response_payload)
            status = "completed"
            error_message = None
        except Exception as exc:  # pragma: no cover - exercised via tests
            result = self._failure_result(str(exc))
            status = "failed"
            error_message = str(exc)

        self._store_result(
            applicant_id=applicant_id,
            result=result,
            status=status,
            error_message=error_message,
        )
        return result

    def list_evaluations(self, applicant_id: int | None = None) -> list[ResumeEvaluation]:
        query = self.session.query(ResumeEvaluation)
        if applicant_id is not None:
            query = query.filter(ResumeEvaluation.applicant_id == applicant_id)
        return list(query.order_by(ResumeEvaluation.created_at.desc()).all())

    def _request_ai_evaluation(self, *, resume_text: str, candidate_name: str | None = None) -> dict[str, Any]:
        client = self.client or self._build_client()
        if client is None:
            raise BlackcrestIntegrationError("OpenAI API key is not configured.")

        settings = self.settings or self._load_settings()
        model = getattr(settings, "openai_model", "gpt-4o-mini") or "gpt-4o-mini"
        prompt = self._build_prompt(resume_text=resume_text, candidate_name=candidate_name)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a recruiting assistant. Return concise, structured JSON only.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        if not content:
            raise BlackcrestIntegrationError("OpenAI returned an empty response.")
        parsed = json.loads(content)
        return parsed

    def _build_client(self) -> Any | None:
        settings = self.settings or self._load_settings()
        validator = getattr(settings, "validate_openai_settings", None)
        if callable(validator):
            validator()

        api_key = getattr(settings, "openai_api_key", "") or ""
        if not api_key:
            return None

        from openai import OpenAI

        return OpenAI(api_key=api_key)

    def _load_settings(self) -> Any:
        if self.settings is not None:
            return self.settings
        from config.settings import get_settings

        return get_settings(validate_required=False)

    def _build_prompt(self, *, resume_text: str, candidate_name: str | None = None) -> str:
        candidate_label = f" for {candidate_name}" if candidate_name else ""
        return (
            f"Evaluate the following resume{candidate_label}. "
            "Return valid JSON with the fields summary, strengths, weaknesses, "
            "recommended_interview_questions, and suggested_hiring_decision. "
            "The summary should be a brief paragraph. Strengths, weaknesses, and "
            "recommended_interview_questions should be arrays of short strings. "
            "Suggested hiring decision should be one of: Hire, Interview, Hold, Reject.\n\n"
            f"Resume text:\n{resume_text}"
        )

    def _normalize_result(self, payload: dict[str, Any]) -> dict[str, Any]:
        summary = str(payload.get("summary", "").strip() or "Resume evaluation completed.")
        strengths = self._to_string_list(payload.get("strengths", []))
        weaknesses = self._to_string_list(payload.get("weaknesses", []))
        questions = self._to_string_list(payload.get("recommended_interview_questions", []))
        decision = str(payload.get("suggested_hiring_decision", "Hold")).strip() or "Hold"

        return {
            "summary": summary,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommended_interview_questions": questions,
            "suggested_hiring_decision": decision,
            "status": "completed",
        }

    def _failure_result(self, error: str) -> dict[str, Any]:
        return {
            "summary": "Evaluation unavailable due to an API error.",
            "strengths": [],
            "weaknesses": [],
            "recommended_interview_questions": [],
            "suggested_hiring_decision": "Hold",
            "status": "failed",
            "error": error,
        }

    def _to_string_list(self, value: Any) -> list[str]:
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str):
            return [value.strip()] if value.strip() else []
        return []

    def _store_result(
        self,
        *,
        applicant_id: int | None,
        result: dict[str, Any],
        status: str,
        error_message: str | None,
    ) -> ResumeEvaluation:
        evaluation = ResumeEvaluation(
            applicant_id=applicant_id,
            summary=result.get("summary", ""),
            strengths=json.dumps(result.get("strengths", [])),
            weaknesses=json.dumps(result.get("weaknesses", [])),
            interview_questions=json.dumps(result.get("recommended_interview_questions", [])),
            hiring_decision=result.get("suggested_hiring_decision", "Hold"),
            status=status,
            error_message=error_message,
        )
        self.session.add(evaluation)
        self.session.commit()
        self.session.refresh(evaluation)
        return evaluation
