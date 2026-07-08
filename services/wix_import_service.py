from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from database.connection import get_session
from models.applicant import Applicant, ApplicantPipelineStage
from services.applicant_service import ApplicantService
from utils.exceptions import BlackcrestInputError


class WixApplicantImportService:
    """Imports Wix-style applicant payloads into RecruitOS applicant records."""

    def __init__(self, session: Session | None = None, database_url: str | None = None) -> None:
        self.session = session or get_session(database_url=database_url, ensure_schema=True)
        self.applicant_service = ApplicantService(session=self.session)

    def import_applicant_payload(self, payload: dict[str, Any]) -> Applicant:
        """Validate and import one Wix-style payload, returning the created or existing applicant."""
        first_name = self._required_text(payload, "first_name", "firstName")
        last_name = self._required_text(payload, "last_name", "lastName")
        email = self._required_email(payload, "email")
        phone = self._required_text(payload, "phone")

        organization_id = self._required_int(payload, "organization_id", "organizationId")
        client_id = self._required_int(payload, "client_id", "clientId")
        job_order_id = self._required_int(payload, "job_order_id", "jobOrderId")

        city = self._optional_text(payload, "city")
        state = self._optional_text(payload, "state")
        resume_filename = self._optional_text(payload, "resume_filename", "resumeFilename")
        resume_path = self._optional_text(payload, "resume_path", "resumePath")
        resume_score = self._optional_float(payload, "resume_score", "resumeScore")

        existing = self._find_existing_applicant(email=email, job_order_id=job_order_id)
        if existing is not None:
            updated = self.applicant_service.update_applicant(
                existing.id,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                city=city,
                state=state,
                resume_filename=resume_filename,
                resume_path=resume_path,
            )
            if resume_score is not None:
                updated = self.applicant_service.update_resume_score(updated.id, resume_score)
            return updated

        created = self.applicant_service.create_applicant(
            organization_id=organization_id,
            client_id=client_id,
            job_order_id=job_order_id,
            first_name=first_name,
            last_name=last_name,
            name=f"{first_name} {last_name}",
            email=email,
            phone=phone,
            city=city,
            state=state,
            resume_filename=resume_filename,
            resume_path=resume_path,
            resume_score=resume_score,
            pipeline_stage=ApplicantPipelineStage.NEW,
        )
        return created

    def _find_existing_applicant(self, *, email: str, job_order_id: int) -> Applicant | None:
        for applicant in self.applicant_service.list_by_job_order(job_order_id):
            if (applicant.email or "").strip().lower() == email:
                return applicant
        return None

    def _required_text(self, payload: dict[str, Any], *keys: str) -> str:
        value = self._first_present(payload, *keys)
        if value is None or not str(value).strip():
            raise BlackcrestInputError(f"{keys[0]} is required")
        return str(value).strip()

    def _required_email(self, payload: dict[str, Any], *keys: str) -> str:
        email = self._required_text(payload, *keys).lower()
        if "@" not in email or "." not in email:
            raise BlackcrestInputError("email must be a valid email address")
        return email

    def _required_int(self, payload: dict[str, Any], *keys: str) -> int:
        value = self._first_present(payload, *keys)
        if value is None:
            raise BlackcrestInputError(f"{keys[0]} is required")
        try:
            parsed = int(value)
        except (TypeError, ValueError) as exc:
            raise BlackcrestInputError(f"{keys[0]} must be an integer") from exc
        if parsed <= 0:
            raise BlackcrestInputError(f"{keys[0]} must be greater than zero")
        return parsed

    def _optional_text(self, payload: dict[str, Any], *keys: str) -> str | None:
        value = self._first_present(payload, *keys)
        if value is None:
            return None
        cleaned = str(value).strip()
        return cleaned if cleaned else None

    def _optional_float(self, payload: dict[str, Any], *keys: str) -> float | None:
        value = self._first_present(payload, *keys)
        if value is None or str(value).strip() == "":
            return None
        try:
            return float(value)
        except (TypeError, ValueError) as exc:
            raise BlackcrestInputError(f"{keys[0]} must be numeric") from exc

    @staticmethod
    def _first_present(payload: dict[str, Any], *keys: str) -> Any:
        for key in keys:
            if key in payload:
                return payload[key]
        return None
