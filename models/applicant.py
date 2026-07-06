from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, Enum as SqlEnum, Float, ForeignKey, String, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from utils.datetime_policy import utc_now_naive

if TYPE_CHECKING:
    from models.client import Client
    from models.job_order import JobOrder
    from models.organization import Organization


class ApplicantPipelineStage(str, Enum):
    """Standardized recruiting pipeline stages for applicants."""

    NEW = "NEW"
    UNDER_REVIEW = "UNDER_REVIEW"
    PHONE_SCREEN = "PHONE_SCREEN"
    INTERVIEW = "INTERVIEW"
    SUBMITTED_TO_CLIENT = "SUBMITTED_TO_CLIENT"
    CLIENT_REVIEW = "CLIENT_REVIEW"
    OFFER = "OFFER"
    HIRED = "HIRED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"


class Applicant(Base):
    """Represents a recruiting applicant."""

    __tablename__ = "applicants"
    __table_args__ = (
        CheckConstraint("resume_score IS NULL OR (resume_score >= 0 AND resume_score <= 100)", name="ck_applicants_resume_score_range"),
        UniqueConstraint("email", "job_order_id", name="uq_applicants_email_job_order"),
    )
    __allow_unmapped__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Ownership scope for Version 2 pipeline foundation.
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, server_default=text("1")
    )
    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id"), nullable=False, server_default=text("1")
    )
    job_order_id: Mapped[int] = mapped_column(
        ForeignKey("job_orders.id"), nullable=False, server_default=text("1")
    )

    # New production pipeline profile fields.
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    resume_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    resume_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    resume_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    pipeline_stage: Mapped[ApplicantPipelineStage] = mapped_column(
        SqlEnum(ApplicantPipelineStage), default=ApplicantPipelineStage.NEW, nullable=False
    )
    applied_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=utc_now_naive, nullable=False)
    last_activity_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), default=utc_now_naive, nullable=False
    )

    # Legacy Version 1 fields preserved for compatibility.
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    drivers_license_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    experience: Mapped[str | None] = mapped_column(Text, nullable=True)
    resume_location: Mapped[str | None] = mapped_column(String(500), nullable=True)
    current_status: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    date_added: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=utc_now_naive)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), default=utc_now_naive, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), default=utc_now_naive, onupdate=utc_now_naive, nullable=False
    )

    organization: Mapped["Organization"] = relationship("Organization")
    client: Mapped["Client"] = relationship("Client")
    job_order: Mapped["JobOrder"] = relationship("JobOrder")

    # Relationship placeholders for future domain expansion.
    interviews: list[object]
    notes_entries: list[object]
    activity_logs: list[object]
    attachments: list[object]
