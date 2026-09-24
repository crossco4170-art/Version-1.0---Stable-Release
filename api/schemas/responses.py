from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class APIResponse(BaseModel):
    """Base type for API response models."""

    model_config = ConfigDict(extra="forbid")


class HealthResponse(APIResponse):
    status: str = Field(default="ok")
    version: str = Field(default="2.0")
    application: str = Field(default="Blackcrest RecruitOS")


class ErrorResponse(APIResponse):
    status: str = Field(default="error")
    detail: str


APIErrorResponse = ErrorResponse