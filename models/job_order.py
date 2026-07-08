from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, Enum as SqlEnum, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from utils.datetime_policy import utc_now_naive

if TYPE_CHECKING:
    from models.client import Client
    from models.organization import Organization


class JobOrderStatus(str, Enum):
    """Lifecycle status for one recruiting campaign."""

    DRAFT = "DRAFT"
    OPEN = "OPEN"
    ON_HOLD = "ON_HOLD"
    CLOSED = "CLOSED"
    FILLED = "FILLED"


class JobOrder(Base):
    """Represents an open recruiting job order for a client."""

    __tablename__ = "job_orders"
    __table_args__ = (UniqueConstraint("organization_id", "job_code", name="uq_job_orders_org_job_code"),)
    __allow_unmapped__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    job_code: Mapped[str] = mapped_column(String(100), nullable=False)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    employment_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    pay_min: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    pay_max: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(10), nullable=True)
    number_of_openings: Mapped[int | None] = mapped_column(Integer, nullable=True)
    positions_filled: Mapped[int | None] = mapped_column(Integer, nullable=True)
    work_location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    remote_allowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    travel_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[JobOrderStatus] = mapped_column(
        SqlEnum(JobOrderStatus), default=JobOrderStatus.DRAFT, nullable=False
    )
    date_opened: Mapped[date | None] = mapped_column(Date, nullable=True)
    date_closed: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), default=utc_now_naive, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), default=utc_now_naive, onupdate=utc_now_naive, nullable=False
    )

    organization: Mapped["Organization"] = relationship("Organization")
    client: Mapped["Client"] = relationship("Client")

    # Relationship placeholders for future domain expansion.
    applicants: list[object]
    interview_schedules: list[object]
    activity_logs: list[object]
    attachments: list[object]
