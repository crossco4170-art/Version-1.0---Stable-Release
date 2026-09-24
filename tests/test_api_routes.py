from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api.app import app
from api.routes import api_router
from api.routes import clients as clients_module
from api.routes import interviews as interviews_module
from api.routes import job_orders as job_orders_module
from api.routes import organizations as organizations_module
from api.routes import reports as reports_module


@pytest.mark.parametrize(
    ("path", "router_prefix"),
    [
        ("/api/v1/organizations/", "/organizations"),
        ("/api/v1/clients/", "/clients"),
        ("/api/v1/job-orders/", "/job-orders"),
        ("/api/v1/interviews/", "/interviews"),
        ("/api/v1/reports/", "/reports"),
    ],
)
def test_placeholder_routes_return_ok(path: str, router_prefix: str) -> None:
    client = TestClient(app)

    response = client.get(path)

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Placeholder"}
    assert path in app.openapi()["paths"]
    assert router_prefix in path


def test_api_router_is_registered_with_version_ready_prefix() -> None:
    paths = set(app.openapi()["paths"])

    assert "/api/v1/organizations/" in paths
    assert "/api/v1/clients/" in paths
    assert "/api/v1/job-orders/" in paths
    assert "/api/v1/interviews/" in paths
    assert "/api/v1/reports/" in paths


def test_placeholder_response_schema_is_centralized() -> None:
    schema = app.openapi()["components"]["schemas"]["PlaceholderResponse"]

    assert schema["properties"]["status"]["default"] == "ok"
    assert schema["properties"]["message"]["default"] == "Placeholder"


def test_route_prefixes_are_version_ready() -> None:
    assert api_router.prefix == "/api/v1"
    assert organizations_module.router.prefix == "/organizations"
    assert clients_module.router.prefix == "/clients"
    assert job_orders_module.router.prefix == "/job-orders"
    assert interviews_module.router.prefix == "/interviews"
    assert reports_module.router.prefix == "/reports"