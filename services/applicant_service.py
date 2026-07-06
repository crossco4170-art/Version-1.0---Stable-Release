from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import or_
from sqlalchemy.orm import Session

from database.connection import get_session
from models.applicant import Applicant, ApplicantPipelineStage
from models.client import Client
from models.job_order import JobOrder
from utils.datetime_policy import as_utc_naive, utc_now_naive
from utils.exceptions import BlackcrestInputError, BlackcrestNotFoundError


class ApplicantService:
    """Simple, clean CRUD and search service for applicant records."""

    def __init__(self, session: Session | None = None, database_url: str | None = None) -> None:
        self.session = session or get_session(database_url=database_url, ensure_schema=True)

    # ---------------------------------------------------------------------
    # Validation
    # ---------------------------------------------------------------------

    def _validate_applicant_id(self, applicant_id: int) -> int:
        if applicant_id <= 0:
            raise BlackcrestInputError("Applicant ID must be greater than zero")
        return applicant_id

    def _validate_required(self, name: str, email: str | None = None) -> None:
        if not name or not name.strip():
            raise BlackcrestInputError("Applicant name is required")
        if email is not None and email.strip():
            if "@" not in email or "." not in email:
                raise BlackcrestInputError("Applicant email must be a valid email address")

    def _validate_resume_score(self, score: float | None) -> None:
        if score is not None and (score < 0 or score > 100):
            raise BlackcrestInputError("Applicant resume score must be between 0 and 100")

    def _normalize_pipeline_stage(
        self,
        stage: ApplicantPipelineStage | str,
    ) -> ApplicantPipelineStage:
        if isinstance(stage, ApplicantPipelineStage):
            return stage

        normalized = str(stage).strip().upper()
        if not normalized:
            raise BlackcrestInputError("Applicant pipeline stage is required")

        try:
            return ApplicantPipelineStage(normalized)
        except ValueError as exc:
            raise BlackcrestInputError("Applicant pipeline stage is invalid") from exc

    # ---------------------------------------------------------------------
    # Business Rules
    # ---------------------------------------------------------------------

    def _validate_ownership(
        self,
        *,
        organization_id: int,
        client_id: int,
        job_order_id: int,
    ) -> None:
        if organization_id <= 0:
            raise BlackcrestInputError("Organization ID must be greater than zero")
        if client_id <= 0:
            raise BlackcrestInputError("Client ID must be greater than zero")
        if job_order_id <= 0:
            raise BlackcrestInputError("Job order ID must be greater than zero")

        client = self.session.get(Client, client_id)
        if client is None:
            raise BlackcrestNotFoundError(f"Client not found: {client_id}")
        if client.organization_id != organization_id:
            raise BlackcrestInputError("Client does not belong to the specified organization")

        job_order = self.session.get(JobOrder, job_order_id)
        if job_order is None:
            raise BlackcrestNotFoundError(f"Job order not found: {job_order_id}")
        if job_order.client_id != client_id:
            raise BlackcrestInputError("Job order does not belong to the specified client")
        if job_order.organization_id != organization_id:
            raise BlackcrestInputError("Job order does not belong to the specified organization")

    def _get_applicant_or_raise(self, applicant_id: int) -> Applicant:
        validated_id = self._validate_applicant_id(applicant_id)
        applicant = self.session.get(Applicant, validated_id)
        if applicant is None:
            raise BlackcrestNotFoundError(f"Applicant not found: {applicant_id}")
        return applicant

    def _validate_pipeline_transition(
        self,
        current_stage: ApplicantPipelineStage,
        target_stage: ApplicantPipelineStage,
    ) -> None:
        if current_stage == target_stage:
            raise BlackcrestInputError("Applicant is already in the requested pipeline stage")

        active_flow = [
            ApplicantPipelineStage.NEW,
            ApplicantPipelineStage.UNDER_REVIEW,
            ApplicantPipelineStage.PHONE_SCREEN,
            ApplicantPipelineStage.INTERVIEW,
            ApplicantPipelineStage.SUBMITTED_TO_CLIENT,
            ApplicantPipelineStage.CLIENT_REVIEW,
            ApplicantPipelineStage.OFFER,
            ApplicantPipelineStage.HIRED,
        ]
        terminal_stages = {
            ApplicantPipelineStage.HIRED,
            ApplicantPipelineStage.REJECTED,
            ApplicantPipelineStage.WITHDRAWN,
        }

        if current_stage in terminal_stages:
            raise BlackcrestInputError(
                "Applicants in HIRED, REJECTED, or WITHDRAWN cannot move back into active recruiting stages"
            )

        if target_stage in {ApplicantPipelineStage.REJECTED, ApplicantPipelineStage.WITHDRAWN}:
            return

        current_index = active_flow.index(current_stage)
        target_index = active_flow.index(target_stage)
        if target_index != current_index + 1:
            raise BlackcrestInputError("Invalid pipeline transition")

    # ---------------------------------------------------------------------
    # Persistence
    # ---------------------------------------------------------------------

    def create_applicant(
        self,
        *,
        organization_id: int | None = None,
        client_id: int | None = None,
        job_order_id: int | None = None,
        name: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        phone: str | None = None,
        email: str | None = None,
        city: str | None = None,
        state: str | None = None,
        resume_filename: str | None = None,
        resume_path: str | None = None,
        resume_score: float | None = None,
        pipeline_stage: ApplicantPipelineStage | str = ApplicantPipelineStage.NEW,
        applied_at: datetime | None = None,
        last_activity_at: datetime | None = None,
        address: str | None = None,
        drivers_license_status: str | None = None,
        experience: str | None = None,
        resume_location: str | None = None,
        current_status: str | None = None,
        notes: str | None = None,
        score: float | None = None,
        date_added: datetime | None = None,
    ) -> Applicant:
        """Create and persist a new applicant within organization/client/job-order ownership constraints."""
        candidate_name = (name or f"{first_name or ''} {last_name or ''}").strip()
        self._validate_required(name=candidate_name, email=email)

        resolved_organization_id = organization_id if organization_id is not None else 1
        resolved_client_id = client_id if client_id is not None else 1
        resolved_job_order_id = job_order_id if job_order_id is not None else 1

        if organization_id is not None and client_id is not None and job_order_id is not None:
            self._validate_ownership(
                organization_id=organization_id,
                client_id=client_id,
                job_order_id=job_order_id,
            )

        normalized_resume_score = resume_score if resume_score is not None else score
        self._validate_resume_score(normalized_resume_score)
        normalized_stage = self._normalize_pipeline_stage(pipeline_stage)

        applicant = Applicant(
            organization_id=resolved_organization_id,
            client_id=resolved_client_id,
            job_order_id=resolved_job_order_id,
            name=candidate_name,
            first_name=first_name.strip() if first_name and first_name.strip() else None,
            last_name=last_name.strip() if last_name and last_name.strip() else None,
            phone=phone.strip() if phone and phone.strip() else None,
            email=email.strip() if email and email.strip() else None,
            city=city.strip() if city and city.strip() else None,
            state=state.strip() if state and state.strip() else None,
            resume_filename=resume_filename.strip() if resume_filename and resume_filename.strip() else None,
            resume_path=resume_path.strip() if resume_path and resume_path.strip() else None,
            resume_score=normalized_resume_score,
            pipeline_stage=normalized_stage,
            applied_at=as_utc_naive(applied_at) if applied_at else utc_now_naive(),
            last_activity_at=as_utc_naive(last_activity_at) if last_activity_at else utc_now_naive(),
            address=address.strip() if address and address.strip() else None,
            drivers_license_status=(
                drivers_license_status.strip()
                if drivers_license_status and drivers_license_status.strip()
                else None
            ),
            experience=experience.strip() if experience and experience.strip() else None,
            resume_location=(
                resume_location.strip() if resume_location and resume_location.strip() else None
            ),
            current_status=current_status.strip() if current_status and current_status.strip() else None,
            notes=notes.strip() if notes and notes.strip() else None,
            score=normalized_resume_score,
            date_added=as_utc_naive(date_added) if date_added else utc_now_naive(),
        )
        self.session.add(applicant)
        self.session.commit()
        self.session.refresh(applicant)
        return applicant

    def create(self, **kwargs: Any) -> Applicant:
        """Legacy create alias preserved for compatibility."""
        return self.create_applicant(**kwargs)

    def get_applicant(self, applicant_id: int) -> Applicant | None:
        """Retrieve an applicant by id; return None when no record exists."""
        validated_id = self._validate_applicant_id(applicant_id)
        return self.session.get(Applicant, validated_id)

    def get_by_id(self, applicant_id: int) -> Applicant | None:
        """Legacy get-by-id alias preserved for compatibility."""
        return self.get_applicant(applicant_id)

    def list_applicants(self) -> list[Applicant]:
        """List applicants ordered by creation timestamp descending."""
        return list(self.session.query(Applicant).order_by(Applicant.created_at.desc()).all())

    def list_by_job_order(self, job_order_id: int) -> list[Applicant]:
        """List applicants for a specific job order."""
        if job_order_id <= 0:
            raise BlackcrestInputError("Job order ID must be greater than zero")
        return list(
            self.session.query(Applicant)
            .filter(Applicant.job_order_id == job_order_id)
            .order_by(Applicant.created_at.desc())
            .all()
        )

    def list_by_client(self, client_id: int) -> list[Applicant]:
        """List applicants for a specific client."""
        if client_id <= 0:
            raise BlackcrestInputError("Client ID must be greater than zero")
        return list(
            self.session.query(Applicant)
            .filter(Applicant.client_id == client_id)
            .order_by(Applicant.created_at.desc())
            .all()
        )

    def list_by_organization(self, organization_id: int) -> list[Applicant]:
        """List applicants for a specific organization."""
        if organization_id <= 0:
            raise BlackcrestInputError("Organization ID must be greater than zero")
        return list(
            self.session.query(Applicant)
            .filter(Applicant.organization_id == organization_id)
            .order_by(Applicant.created_at.desc())
            .all()
        )

    def list_by_pipeline_stage(self, stage: ApplicantPipelineStage | str) -> list[Applicant]:
        """List applicants filtered by pipeline stage."""
        normalized_stage = self._normalize_pipeline_stage(stage)
        return list(
            self.session.query(Applicant)
            .filter(Applicant.pipeline_stage == normalized_stage)
            .order_by(Applicant.created_at.desc())
            .all()
        )

    def search_applicants(self, query: str) -> list[Applicant]:
        """Search applicants across legacy core fields."""
        if not query or not query.strip():
            raise BlackcrestInputError("Search query is required")
        term = f"%{query.strip()}%"
        return list(
            self.session.query(Applicant)
            .filter(
                or_(
                    Applicant.name.ilike(term),
                    Applicant.email.ilike(term),
                    Applicant.phone.ilike(term),
                    Applicant.current_status.ilike(term),
                    Applicant.notes.ilike(term),
                )
            )
            .order_by(Applicant.created_at.desc())
            .all()
        )

    def update_applicant(self, applicant_id: int, **updates: Any) -> Applicant:
        """Update mutable applicant profile fields while preserving ownership and lifecycle rules."""
        applicant = self._get_applicant_or_raise(applicant_id)
        allowed_fields = {
            "name",
            "first_name",
            "last_name",
            "phone",
            "email",
            "city",
            "state",
            "resume_filename",
            "resume_path",
            "address",
            "drivers_license_status",
            "experience",
            "resume_location",
            "current_status",
            "notes",
            "applied_at",
            "last_activity_at",
        }

        for key, value in updates.items():
            if key not in allowed_fields:
                raise BlackcrestInputError(f"Unsupported field: {key}")
            if key == "name" and (not value or not str(value).strip()):
                raise BlackcrestInputError("Applicant name is required")
            if key == "email" and value is not None and value != "":
                if "@" not in str(value) or "." not in str(value):
                    raise BlackcrestInputError("Applicant email must be a valid email address")
            if key in {"applied_at", "last_activity_at"} and value is not None:
                setattr(applicant, key, as_utc_naive(value))
                continue

            if isinstance(value, str):
                setattr(applicant, key, value.strip() or None)
            else:
                setattr(applicant, key, value)

        applicant.updated_at = utc_now_naive()
        applicant.last_activity_at = utc_now_naive()
        self.session.commit()
        self.session.refresh(applicant)
        return applicant

    def edit_applicant(self, applicant_id: int, **updates: Any) -> Applicant | None:
        """Legacy edit alias preserved for compatibility; returns None when missing."""
        applicant = self.get_applicant(applicant_id)
        if applicant is None:
            return None
        return self.update_applicant(applicant_id, **updates)

    def update(self, applicant_id: int, **kwargs: Any) -> Applicant | None:
        """Legacy update alias preserved for compatibility."""
        return self.edit_applicant(applicant_id, **kwargs)

    def move_pipeline_stage(
        self,
        applicant_id: int,
        new_stage: ApplicantPipelineStage | str,
    ) -> Applicant:
        """Move an applicant to a new pipeline stage when transition rules allow it."""
        applicant = self._get_applicant_or_raise(applicant_id)
        target_stage = self._normalize_pipeline_stage(new_stage)
        self._validate_pipeline_transition(applicant.pipeline_stage, target_stage)

        applicant.pipeline_stage = target_stage
        applicant.current_status = target_stage.value
        applicant.last_activity_at = utc_now_naive()
        applicant.updated_at = utc_now_naive()
        self.session.commit()
        self.session.refresh(applicant)
        return applicant

    def update_resume_score(self, applicant_id: int, resume_score: float) -> Applicant:
        """Update the applicant resume score with range validation."""
        applicant = self._get_applicant_or_raise(applicant_id)
        self._validate_resume_score(resume_score)

        applicant.resume_score = resume_score
        applicant.score = resume_score
        applicant.last_activity_at = utc_now_naive()
        applicant.updated_at = utc_now_naive()
        self.session.commit()
        self.session.refresh(applicant)
        return applicant

    def delete_applicant(self, applicant_id: int) -> bool:
        """Delete an applicant by id."""
        self._validate_applicant_id(applicant_id)
        applicant = self.get_applicant(applicant_id)
        if applicant is None:
            return False

        self.session.delete(applicant)
        self.session.commit()
        return True

    def delete(self, applicant_id: int) -> bool:
        """Legacy delete alias preserved for compatibility."""
        return self.delete_applicant(applicant_id)
