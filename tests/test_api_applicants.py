from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from api.app import app
from api.routes import applicants as applicants_module
from api.routes.applicants import get_applicant_service, router as applicants_router
from api.schemas.applicants import ApplicantListResponse, ApplicantResponse
from database.connection import get_session
from database.init_db import initialize_database
from models.client import Client
from models.job_order import JobOrder
from models.organization import Organization, OrganizationStatus
from services.applicant_service import ApplicantService


def _build_applicant(applicant_id: int = 7) -> SimpleNamespace:
    return SimpleNamespace(
        id=applicant_id,
        organization_id=1,
        client_id=2,
        job_order_id=3,
        name="Jordan Miles",
        first_name="Jordan",
        last_name="Miles",
        phone="(414) 555-0148",
        email="jordan.miles@example.com",
        city="Milwaukee",
        state="WI",
        resume_filename="jordan_miles_resume.pdf",
        resume_path="/resumes/jordan_miles_resume.pdf",
        resume_score=92.5,
        pipeline_stage="REVIEW",
        applied_at="2026-07-05T12:00:00",
        last_activity_at="2026-07-06T12:00:00",
        address="123 Main St",
        drivers_license_status="Valid",
        experience="3 years logistics and delivery",
        resume_location="Local disk",
        current_status="Active",
        notes="Strong candidate",
        score=92.5,
        date_added="2026-07-05T12:00:00",
        created_at="2026-07-05T12:00:00",
        updated_at="2026-07-06T12:00:00",
    )


def _override_service(service: Mock) -> None:
    app.dependency_overrides[get_applicant_service] = lambda: service


def _clear_overrides() -> None:
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def reset_overrides() -> None:
    _clear_overrides()
    yield
    _clear_overrides()


def test_applicant_list_endpoint_returns_applicants() -> None:
    applicant = _build_applicant()
    service = Mock(spec=ApplicantService)
    service.list_applicants.return_value = [applicant]
    _override_service(service)

    client = TestClient(app)
    response = client.get("/api/v1/applicants/")

    assert response.status_code == 200
    assert response.json() == [ApplicantResponse.model_validate(applicant, from_attributes=True).model_dump(mode="json")]
    service.list_applicants.assert_called_once_with()


def test_applicant_get_endpoint_returns_one_applicant() -> None:
    applicant = _build_applicant(applicant_id=11)
    service = Mock(spec=ApplicantService)
    service.get_applicant.return_value = applicant
    _override_service(service)

    client = TestClient(app)
    response = client.get("/api/v1/applicants/11")

    assert response.status_code == 200
    assert response.json() == ApplicantResponse.model_validate(applicant, from_attributes=True).model_dump(mode="json")
    service.get_applicant.assert_called_once_with(11)


def test_applicant_get_endpoint_returns_404_for_missing_record() -> None:
    service = Mock(spec=ApplicantService)
    service.get_applicant.return_value = None
    _override_service(service)

    client = TestClient(app)
    response = client.get("/api/v1/applicants/99")

    assert response.status_code == 404
    assert response.json() == {"status": "error", "detail": "Applicant not found: 99"}


def test_applicant_list_endpoint_returns_500_for_service_failure() -> None:
    service = Mock(spec=ApplicantService)
    service.list_applicants.side_effect = RuntimeError("database unavailable")
    _override_service(service)

    client = TestClient(app)
    response = client.get("/api/v1/applicants/")

    assert response.status_code == 500
    assert response.json() == {"status": "error", "detail": "Applicant lookup failed"}


def test_applicant_routes_use_dependency_injection() -> None:
    dependency_calls = {
        dependency.call for route in applicants_router.routes for dependency in route.dependant.dependencies
    }

    assert get_applicant_service in dependency_calls


def test_applicant_response_schema_is_centralized() -> None:
    schema = app.openapi()["components"]["schemas"]["ApplicantResponse"]

    assert schema["properties"]["name"]["type"] == "string"
    assert schema["properties"]["pipeline_stage"]["title"] == "Pipeline Stage"
    assert "created_at" in schema["required"]


def test_applicant_route_registration_and_prefixes() -> None:
    paths = app.openapi()["paths"]

    assert "/api/v1/applicants/" in paths
    assert "/api/v1/applicants/{applicant_id}" in paths
    assert applicants_module.router.prefix == "/applicants"


def test_applicant_list_response_model_round_trips() -> None:
    applicant = _build_applicant()
    response_model = ApplicantListResponse(root=[ApplicantResponse.model_validate(applicant, from_attributes=True)])

    assert response_model.model_dump(mode="json") == [ApplicantResponse.model_validate(applicant, from_attributes=True).model_dump(mode="json")]


def test_applicant_list_endpoint_uses_preinitialized_database_without_request_schema_init(tmp_path) -> None:
    database_path = tmp_path / "api_applicants.db"
    initialize_database(str(database_path))
    session = get_session(database_url=str(database_path))

    organization = Organization(
        name="Greater Connections Staffing",
        legal_name="Greater Connections Staffing LLC",
        status=OrganizationStatus.ACTIVE,
    )
    session.add(organization)
    session.commit()

    client = Client(organization_id=organization.id, company_name="USPS")
    session.add(client)
    session.commit()

    job_order = JobOrder(
        organization_id=organization.id,
        client_id=client.id,
        job_code="USPS-RCA-2026-001",
        title="Rural Carrier Associate",
    )
    session.add(job_order)
    session.commit()

    ApplicantService(session=session).create_applicant(
        organization_id=organization.id,
        client_id=client.id,
        job_order_id=job_order.id,
        first_name="Jordan",
        last_name="Miles",
        email="jordan@example.com",
    )

    observed: dict[str, object] = {}
    original_get_session = applicants_module.get_session

    def recording_get_session(*, database_url=None, ensure_schema: bool = False):
        observed["database_url"] = database_url
        observed["ensure_schema"] = ensure_schema
        return session

    applicants_module.get_session = recording_get_session
    try:
        client_app = TestClient(app)
        response = client_app.get("/api/v1/applicants/")
    finally:
        applicants_module.get_session = original_get_session
        session.close()

    assert observed["ensure_schema"] is False
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["organization_id"] == organization.id