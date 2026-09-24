from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field


class PlaceholderResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = Field(default="ok")
    message: str = Field(default="Placeholder")


def create_placeholder_router(resource: str) -> APIRouter:
    router = APIRouter(prefix=f"/{resource}", tags=[resource])

    @router.get("/", response_model=PlaceholderResponse, summary=f"{resource} placeholder")
    def placeholder() -> PlaceholderResponse:
        return PlaceholderResponse()

    return router