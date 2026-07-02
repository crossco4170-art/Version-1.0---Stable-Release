from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import or_
from sqlalchemy.orm import Session

from database.connection import get_session
from models.applicant import Applicant
from utils.datetime_policy import as_utc_naive, utc_now_naive
from utils.exceptions import BlackcrestInputError


class ApplicantService:
    """Simple, clean CRUD and search service for applicant records."""

    def __init__(self, session: Session | None = None, database_url: str | None = None) -> None:
        self.session = session or get_session(database_url=database_url, ensure_schema=True)

    def _validate_required(self, name: str, email: str | None = None) -> None:
        if not name or not name.strip():
            raise BlackcrestInputError("Applicant name is required")
        if email is not None and email.strip():
            if "@" not in email or "." not in email:
                raise BlackcrestInputError("Applicant email must be a valid email address")

    def _validate_score(self, score: float | None) -> None:
        if score is not None and (score < 0 or score > 100):
            raise BlackcrestInputError("Applicant score must be between 0 and 100")

    def create_applicant(
        self,
        *,
        name: str,
        phone: str | None = None,
        email: str | None = None,
        address: str | None = None,
        drivers_license_status: str | None = None,
        experience: str | None = None,
        resume_location: str | None = None,
        current_status: str | None = None,
        notes: str | None = None,
        score: float | None = None,
        date_added: datetime | None = None,
    ) -> Applicant:
        self._validate_required(name=name, email=email)
        self._validate_score(score)

        applicant = Applicant(
            name=name.strip(),
            phone=phone.strip() if phone and phone.strip() else None,
            email=email.strip() if email and email.strip() else None,
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
            score=score,
            date_added=as_utc_naive(date_added) if date_added else utc_now_naive(),
        )
        self.session.add(applicant)
        self.session.commit()
        self.session.refresh(applicant)
        return applicant

    def create(self, **kwargs: Any) -> Applicant:
        return self.create_applicant(**kwargs)

    def get_applicant(self, applicant_id: int) -> Applicant | None:
        if applicant_id <= 0:
            raise BlackcrestInputError("Applicant ID must be greater than zero")
        return self.session.get(Applicant, applicant_id)

    def get_by_id(self, applicant_id: int) -> Applicant | None:
        return self.get_applicant(applicant_id)

    def list_applicants(self) -> list[Applicant]:
        return list(self.session.query(Applicant).order_by(Applicant.created_at.desc()).all())

    def search_applicants(self, query: str) -> list[Applicant]:
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

    def edit_applicant(self, applicant_id: int, **updates: Any) -> Applicant | None:
        if applicant_id <= 0:
            raise BlackcrestInputError("Applicant ID must be greater than zero")

        applicant = self.get_applicant(applicant_id)
        if applicant is None:
            return None

        allowed_fields = {
            "name",
            "phone",
            "email",
            "address",
            "drivers_license_status",
            "experience",
            "resume_location",
            "current_status",
            "notes",
            "score",
        }

        for key, value in updates.items():
            if key not in allowed_fields:
                raise BlackcrestInputError(f"Unsupported field: {key}")
            if key == "name" and (not value or not str(value).strip()):
                raise BlackcrestInputError("Applicant name is required")
            if key == "email" and value is not None and value != "":
                if "@" not in str(value) or "." not in str(value):
                    raise BlackcrestInputError("Applicant email must be a valid email address")
            if key == "score" and value is not None:
                self._validate_score(float(value))
            if isinstance(value, str):
                setattr(applicant, key, value.strip() or None)
            else:
                setattr(applicant, key, value)

        self.session.commit()
        self.session.refresh(applicant)
        return applicant

    def update(self, applicant_id: int, **kwargs: Any) -> Applicant | None:
        return self.edit_applicant(applicant_id, **kwargs)

    def delete_applicant(self, applicant_id: int) -> bool:
        if applicant_id <= 0:
            raise BlackcrestInputError("Applicant ID must be greater than zero")

        applicant = self.get_applicant(applicant_id)
        if applicant is None:
            return False

        self.session.delete(applicant)
        self.session.commit()
        return True

    def delete(self, applicant_id: int) -> bool:
        return self.delete_applicant(applicant_id)
