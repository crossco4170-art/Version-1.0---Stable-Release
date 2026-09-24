from __future__ import annotations

from fastapi.testclient import TestClient

from api.app import app, create_app
from api.schemas.responses import ErrorResponse, HealthResponse


def test_create_app_builds_fastapi_application() -> None:
    test_app = create_app()

    assert test_app.title == "Blackcrest RecruitOS API"
    assert test_app.version == "2.0"
    assert "/health" in test_app.openapi()["paths"]


def test_health_endpoint_returns_expected_payload() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "version": "2.0",
        "application": "Blackcrest RecruitOS",
    }


def test_health_endpoint_is_documented_with_response_model() -> None:
    schema = app.openapi()["components"]["schemas"]["HealthResponse"]

    assert schema["properties"]["status"]["default"] == "ok"
    assert schema["properties"]["version"]["default"] == "2.0"
    assert schema["properties"]["application"]["default"] == "Blackcrest RecruitOS"


def test_centralized_api_response_models_default_correctly() -> None:
    assert HealthResponse().model_dump() == {
        "status": "ok",
        "version": "2.0",
        "application": "Blackcrest RecruitOS",
    }
    assert ErrorResponse(detail="Unauthorized").model_dump() == {
        "status": "error",
        "detail": "Unauthorized",
    }