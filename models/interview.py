from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from utils.datetime_policy import utc_now_naive


class Interview(Base):
    """Represents an interview scheduled for an applicant and job order."""

    __tablename__ = "interviews"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    applicant_id: Mapped[int] = mapped_column(ForeignKey("applicants.id"), nullable=False)
    job_order_id: Mapped[int | None] = mapped_column(ForeignKey("job_orders.id"), nullable=True)
    interview_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    interview_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    interviewer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    outcome: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), default=utc_now_naive, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), default=utc_now_naive, onupdate=utc_now_naive, nullable=False
    )
