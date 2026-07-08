from __future__ import annotations

import pytest

from models.applicant import ApplicantPipelineStage
from models.client import Client
from models.job_order import JobOrder
from models.organization import Organization, OrganizationStatus
from services.applicant_service import ApplicantService
from services.wix_import_service import WixApplicantImportService
from tests.helpers import build_test_session
from utils.exceptions import BlackcrestInputError


def _create_foundation(session):
    organization = Organization(
        name="Greater Connections Staffing",
        legal_name="Greater Connections Staffing LLC",
        status=OrganizationStatus.ACTIVE,
    )
    session.add(organization)
    session.commit()

    client = Client(
        organization_id=organization.id,
        company_name="USPS",
    )
    session.add(client)
    session.commit()

    first_job_order = JobOrder(
        organization_id=organization.id,
        client_id=client.id,
        job_code="USPS-RCA-2026-001",
        title="Rural Carrier Associate",
    )
    second_job_order = JobOrder(
        organization_id=organization.id,
        client_id=client.id,
        job_code="USPS-RCA-2026-002",
        title="Rural Carrier Associate Backup",
    )
    session.add(first_job_order)
    session.add(second_job_order)
    session.commit()

    return organization, client, first_job_order, second_job_order


def _build_payload(organization_id: int, client_id: int, job_order_id: int) -> dict[str, object]:
    return {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane@example.com",
        "phone": "555-0100",
        "organization_id": organization_id,
        "client_id": client_id,
        "job_order_id": job_order_id,
        "city": "Milwaukee",
        "state": "WI",
        "resume_filename": "jane_resume.pdf",
        "resume_path": "/resumes/jane_resume.pdf",
    }


def test_successful_import(tmp_path) -> None:
    session = build_test_session(tmp_path / "wix_import_success.db")
    service = WixApplicantImportService(session=session)
    organization, client, job_order, _ = _create_foundation(session)

    applicant = service.import_applicant_payload(
        _build_payload(organization.id, client.id, job_order.id)
    )

    assert applicant.id is not None
    assert applicant.first_name == "Jane"
    assert applicant.job_order_id == job_order.id


def test_duplicate_prevention(tmp_path) -> None:
    session = build_test_session(tmp_path / "wix_import_duplicate.db")
    service = WixApplicantImportService(session=session)
    applicant_service = ApplicantService(session=session)
    organization, client, job_order, _ = _create_foundation(session)

    payload = _build_payload(organization.id, client.id, job_order.id)
    first = service.import_applicant_payload(payload)
    second = service.import_applicant_payload(payload)

    assert first.id == second.id
    assert len(applicant_service.list_by_job_order(job_order.id)) == 1


def test_same_email_allowed_on_different_job_orders(tmp_path) -> None:
    session = build_test_session(tmp_path / "wix_import_different_job_orders.db")
    service = WixApplicantImportService(session=session)
    applicant_service = ApplicantService(session=session)
    organization, client, first_job_order, second_job_order = _create_foundation(session)

    payload_one = _build_payload(organization.id, client.id, first_job_order.id)
    payload_two = _build_payload(organization.id, client.id, second_job_order.id)

    first = service.import_applicant_payload(payload_one)
    second = service.import_applicant_payload(payload_two)

    assert first.id != second.id
    assert len(applicant_service.list_by_job_order(first_job_order.id)) == 1
    assert len(applicant_service.list_by_job_order(second_job_order.id)) == 1


def test_invalid_payload_rejection(tmp_path) -> None:
    session = build_test_session(tmp_path / "wix_import_invalid_payload.db")
    service = WixApplicantImportService(session=session)
    organization, client, job_order, _ = _create_foundation(session)

    payload = _build_payload(organization.id, client.id, job_order.id)
    payload["phone"] = ""

    with pytest.raises(BlackcrestInputError):
        service.import_applicant_payload(payload)


def test_pipeline_defaults_to_new(tmp_path) -> None:
    session = build_test_session(tmp_path / "wix_import_default_pipeline.db")
    service = WixApplicantImportService(session=session)
    organization, client, job_order, _ = _create_foundation(session)

    applicant = service.import_applicant_payload(
        _build_payload(organization.id, client.id, job_order.id)
    )

    assert applicant.pipeline_stage == ApplicantPipelineStage.NEW


def test_ownership_validation(tmp_path) -> None:
    session = build_test_session(tmp_path / "wix_import_ownership_validation.db")
    service = WixApplicantImportService(session=session)
    organization, client, job_order, _ = _create_foundation(session)

    other_organization = Organization(
        name="Next Horizon Staffing",
        legal_name="Next Horizon Staffing LLC",
        status=OrganizationStatus.ACTIVE,
    )
    session.add(other_organization)
    session.commit()

    payload = _build_payload(other_organization.id, client.id, job_order.id)

    with pytest.raises(BlackcrestInputError):
        service.import_applicant_payload(payload)
