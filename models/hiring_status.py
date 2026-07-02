from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from utils.datetime_policy import utc_now_naive


class HiringStatus(Base):
    """Tracks the current hiring status of an applicant for a job order."""

    __tablename__ = "hiring_statuses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    applicant_id: Mapped[int] = mapped_column(ForeignKey("applicants.id"), nullable=False)
    job_order_id: Mapped[int | None] = mapped_column(ForeignKey("job_orders.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(100), nullable=False)
    status_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), default=utc_now_naive, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), default=utc_now_naive, onupdate=utc_now_naive, nullable=False
    )
