from __future__ import annotations

from pathlib import Path

import pytest

from config.settings import Settings
from database.init_db import initialize_database
from services.applicant_service import ApplicantService
from services.interview_scheduler_service import InterviewSchedulerService
from services.resume_evaluator import ResumeEvaluator
from services.seed_admin import seed_admin_user
from tests.helpers import build_test_session
from utils.exceptions import (
    BlackcrestAuthError,
    BlackcrestConfigError,
    BlackcrestInputError,
    BlackcrestIntegrationError,
    BlackcrestNotFoundError,
)
from utils.passwords import hash_password


class _OpenAISettingsStub:
    """Minimal settings stub that leaves API key empty for integration-error testing."""

    openai_api_key = ""
    openai_model = "gpt-4o-mini"

    def validate_openai_settings(self) -> None:
        return None


def test_settings_uses_application_specific_config_error(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("DATABASE_PATH", "./tmp.db")
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("LOG_LEVEL", "INFO")

    settings = Settings(validate_required=False)

    with pytest.raises(BlackcrestConfigError):
        settings.validate_feature_settings("calendar")


def test_applicant_service_input_errors_are_specific(tmp_path: Path) -> None:
    database_path = tmp_path / "applicant_exceptions.db"
    initialize_database(str(database_path))
    service = ApplicantService(database_url=f"sqlite:///{database_path}")

    with pytest.raises(BlackcrestInputError):
        service.search_applicants("   ")


def test_interview_scheduler_uses_specific_input_and_not_found_errors(tmp_path: Path) -> None:
    database_path = tmp_path / "scheduler_exceptions.db"
    initialize_database(str(database_path))
    scheduler = InterviewSchedulerService(database_url=f"sqlite:///{database_path}")

    with pytest.raises(BlackcrestInputError):
        scheduler.schedule_interview(
            applicant_id=1,
            interview_date="07-20-2026",
            interview_time="2:00 PM",
            recruiter="Avery",
        )

    with pytest.raises(BlackcrestNotFoundError):
        scheduler.schedule_interview(
            applicant_id=999,
            interview_date="2026-07-20",
            interview_time="14:00",
            recruiter="Avery",
        )


def test_resume_evaluator_raises_specific_integration_error_for_missing_key(tmp_path: Path) -> None:
    database_path = tmp_path / "resume_eval_exceptions.db"
    initialize_database(str(database_path))

    evaluator = ResumeEvaluator(
        database_url=f"sqlite:///{database_path}",
        settings=_OpenAISettingsStub(),
        client=None,
    )

    with pytest.raises(BlackcrestIntegrationError):
        evaluator._request_ai_evaluation(resume_text="Name: Test User")


def test_seed_admin_user_requires_credentials_with_specific_error(tmp_path: Path) -> None:
    session = build_test_session(tmp_path / "seed_admin_exceptions.db")

    with pytest.raises(BlackcrestAuthError):
        seed_admin_user(session=session, username=None, password=None)


def test_hash_password_uses_specific_input_error() -> None:
    with pytest.raises(BlackcrestInputError):
        hash_password("short")
