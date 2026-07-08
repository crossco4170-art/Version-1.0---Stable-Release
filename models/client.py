from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from utils.datetime_policy import utc_now_naive


class ClientStatus(str, Enum):
    """Lifecycle status for client accounts."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"


class Client(Base):
    """Represents a client company hiring through the recruiting platform."""

    __tablename__ = "clients"
    __allow_unmapped__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    street_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    zip_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ClientStatus] = mapped_column(
        SqlEnum(ClientStatus), default=ClientStatus.ACTIVE, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), default=utc_now_naive, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), default=utc_now_naive, onupdate=utc_now_naive, nullable=False
    )

    organization: Mapped["Organization"] = relationship("Organization")

    # Relationship placeholders for future domain expansion.
    job_orders: list[object]
    contacts: list[object]
    activity_logs: list[object]
