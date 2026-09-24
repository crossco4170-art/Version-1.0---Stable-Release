from __future__ import annotations

from fastapi import APIRouter, Depends

from api.schemas.responses import HealthResponse

router = APIRouter(tags=["health"])


def build_health_response() -> HealthResponse:
    """Return the canonical health response payload."""
    return HealthResponse()


@router.get("/health", response_model=HealthResponse, summary="Health check")
def health(response: HealthResponse = Depends(build_health_response)) -> HealthResponse:
    return response