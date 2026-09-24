from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, RootModel

from models.applicant import ApplicantPipelineStage


class ApplicantResponse(BaseModel):
    """Serialized applicant payload returned by the REST API."""

    model_config = ConfigDict(from_attributes=True, use_enum_values=True, extra="forbid")

    id: int
    organization_id: int = Field(..., description="Owning organization identifier")
    client_id: int = Field(..., description="Owning client identifier")
    job_order_id: int = Field(..., description="Owning job order identifier")
    name: str
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    email: str | None = None
    city: str | None = None
    state: str | None = None
    resume_filename: str | None = None
    resume_path: str | None = None
    resume_score: float | None = None
    pipeline_stage: ApplicantPipelineStage | str
    applied_at: datetime
    last_activity_at: datetime
    address: str | None = None
    drivers_license_status: str | None = None
    experience: str | None = None
    resume_location: str | None = None
    current_status: str | None = None
    notes: str | None = None
    score: float | None = None
    date_added: datetime
    created_at: datetime
    updated_at: datetime


class ApplicantListResponse(RootModel[list[ApplicantResponse]]):
    """Root response model for applicant collections."""

    model_config = ConfigDict(from_attributes=True)
