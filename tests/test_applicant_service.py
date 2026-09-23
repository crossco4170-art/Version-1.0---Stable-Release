from __future__ import annotations

import sqlite3

import pytest

from config.settings import Settings
import database.connection as database_connection
from database.init_db import initialize_database
from models.applicant import ApplicantPipelineStage
from models.client import Client
from models.job_order import JobOrder
from models.organization import Organization, OrganizationStatus
from services.applicant_service import ApplicantService
from tests.helpers import build_test_session
from utils.exceptions import BlackcrestInputError


def test_service_construction_does_not_initialize_schema(tmp_path, monkeypatch) -> None:
    database_path = tmp_path / "service_without_schema.db"
    monkeypatch.setattr(
        database_connection,
        "get_settings",
        lambda: Settings(database_url=str(database_path)),
    )

    service = ApplicantService()

    assert service.session is not None
    with sqlite3.connect(database_path) as connection:
        tables = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    assert tables == []


def test_service_reads_from_explicitly_initialized_database(tmp_path) -> None:
    database_path = tmp_path / "service_initialized.db"
    initialize_database(str(database_path))
    session = build_test_session(database_path)
    organization, client, job_order = _create_foundation(session)
    applicant = ApplicantService(session=session).create_applicant(
        organization_id=organization.id,
        client_id=client.id,
        job_order_id=job_order.id,
        name="Initialized Applicant",
        email="initialized@example.com",
    )
    session.close()

    service = ApplicantService(database_url=str(database_path))

    loaded = service.get_applicant(applicant.id)

    assert loaded is not None
    assert loaded.name == "Initialized Applicant"


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

    job_order = JobOrder(
        organization_id=organization.id,
        client_id=client.id,
        job_code="USPS-RCA-2026-001",
        title="Rural Carrier Associate",
    )
    session.add(job_order)
    session.commit()

    return organization, client, job_order


def test_create_applicant(tmp_path) -> None:
    session = build_test_session(tmp_path / "applicant_service_create.db")
    service = ApplicantService(session=session)
    organization, client, job_order = _create_foundation(session)

    applicant = service.create_applicant(
        organization_id=organization.id,
        client_id=client.id,
        job_order_id=job_order.id,
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
    )

    assert applicant.id is not None
    assert applicant.organization_id == organization.id


def test_organization_ownership_validation(tmp_path) -> None:
    session = build_test_session(tmp_path / "applicant_service_org_ownership.db")
    service = ApplicantService(session=session)

    org_a, _, _ = _create_foundation(session)
    org_b = Organization(
        name="Next Horizon Staffing",
        legal_name="Next Horizon Staffing LLC",
        status=OrganizationStatus.ACTIVE,
    )
    session.add(org_b)
    session.commit()

    client = Client(organization_id=org_a.id, company_name="Amazon")
    session.add(client)
    session.commit()

    job_order = JobOrder(
        organization_id=org_a.id,
        client_id=client.id,
        job_code="AMZ-DRV-2026-001",
        title="Driver",
    )
    session.add(job_order)
    session.commit()

    with pytest.raises(BlackcrestInputError):
        service.create_applicant(
            organization_id=org_b.id,
            client_id=client.id,
            job_order_id=job_order.id,
            name="Jane Doe",
        )


def test_client_ownership_validation(tmp_path) -> None:
    session = build_test_session(tmp_path / "applicant_service_client_ownership.db")
    service = ApplicantService(session=session)
    organization, _, _ = _create_foundation(session)

    client = Client(organization_id=organization.id, company_name="FedEx")
    session.add(client)
    session.commit()

    other_client = Client(organization_id=organization.id, company_name="UPS")
    session.add(other_client)
    session.commit()

    job_order = JobOrder(
        organization_id=organization.id,
        client_id=client.id,
        job_code="FDX-DRV-2026-001",
        title="Driver",
    )
    session.add(job_order)
    session.commit()

    with pytest.raises(BlackcrestInputError):
        service.create_applicant(
            organization_id=organization.id,
            client_id=other_client.id,
            job_order_id=job_order.id,
            name="Jane Doe",
        )


def test_job_order_ownership_validation(tmp_path) -> None:
    session = build_test_session(tmp_path / "applicant_service_job_order_ownership.db")
    service = ApplicantService(session=session)
    organization, client, _ = _create_foundation(session)

    other_client = Client(organization_id=organization.id, company_name="Amazon")
    session.add(other_client)
    session.commit()

    job_order = JobOrder(
        organization_id=organization.id,
        client_id=other_client.id,
        job_code="AMZ-DRV-2026-001",
        title="Driver",
    )
    session.add(job_order)
    session.commit()

    with pytest.raises(BlackcrestInputError):
        service.create_applicant(
            organization_id=organization.id,
            client_id=client.id,
            job_order_id=job_order.id,
            name="Jane Doe",
        )


def test_list_by_organization(tmp_path) -> None:
    session = build_test_session(tmp_path / "applicant_service_list_org.db")
    service = ApplicantService(session=session)
    organization, client, job_order = _create_foundation(session)

    service.create_applicant(
        organization_id=organization.id,
        client_id=client.id,
        job_order_id=job_order.id,
        name="Alice Doe",
    )
    service.create_applicant(
        organization_id=organization.id,
        client_id=client.id,
        job_order_id=job_order.id,
        name="Bob Doe",
    )

    applicants = service.list_by_organization(organization.id)

    assert len(applicants) == 2


def test_list_by_client(tmp_path) -> None:
    session = build_test_session(tmp_path / "applicant_service_list_client.db")
    service = ApplicantService(session=session)
    organization, client, job_order = _create_foundation(session)

    service.create_applicant(
        organization_id=organization.id,
        client_id=client.id,
        job_order_id=job_order.id,
        name="Alice Doe",
    )

    applicants = service.list_by_client(client.id)

    assert len(applicants) == 1
    assert applicants[0].client_id == client.id


def test_list_by_job_order(tmp_path) -> None:
    session = build_test_session(tmp_path / "applicant_service_list_job_order.db")
    service = ApplicantService(session=session)
    organization, client, job_order = _create_foundation(session)

    service.create_applicant(
        organization_id=organization.id,
        client_id=client.id,
        job_order_id=job_order.id,
        name="Alice Doe",
    )

    applicants = service.list_by_job_order(job_order.id)

    assert len(applicants) == 1
    assert applicants[0].job_order_id == job_order.id


def test_list_by_pipeline_stage(tmp_path) -> None:
    session = build_test_session(tmp_path / "applicant_service_list_stage.db")
    service = ApplicantService(session=session)
    organization, client, job_order = _create_foundation(session)

    service.create_applicant(
        organization_id=organization.id,
        client_id=client.id,
        job_order_id=job_order.id,
        name="Alice Doe",
        pipeline_stage=ApplicantPipelineStage.NEW,
    )
    service.create_applicant(
        organization_id=organization.id,
        client_id=client.id,
        job_order_id=job_order.id,
        name="Bob Doe",
        pipeline_stage=ApplicantPipelineStage.UNDER_REVIEW,
    )

    applicants = service.list_by_pipeline_stage(ApplicantPipelineStage.NEW)

    assert len(applicants) == 1
    assert applicants[0].pipeline_stage == ApplicantPipelineStage.NEW


def test_update_applicant(tmp_path) -> None:
    session = build_test_session(tmp_path / "applicant_service_update.db")
    service = ApplicantService(session=session)
    organization, client, job_order = _create_foundation(session)

    applicant = service.create_applicant(
        organization_id=organization.id,
        client_id=client.id,
        job_order_id=job_order.id,
        name="Alice Doe",
    )

    updated = service.update_applicant(
        applicant.id,
        first_name="Alicia",
        city="Milwaukee",
        state="WI",
        notes="Updated",
    )

    assert updated.first_name == "Alicia"
    assert updated.city == "Milwaukee"
    assert updated.state == "WI"
    assert updated.notes == "Updated"


def test_resume_score_validation(tmp_path) -> None:
    session = build_test_session(tmp_path / "applicant_service_resume_score.db")
    service = ApplicantService(session=session)
    organization, client, job_order = _create_foundation(session)

    applicant = service.create_applicant(
        organization_id=organization.id,
        client_id=client.id,
        job_order_id=job_order.id,
        name="Alice Doe",
    )

    with pytest.raises(BlackcrestInputError):
        service.update_resume_score(applicant.id, 101)

    scored = service.update_resume_score(applicant.id, 88)
    assert scored.resume_score == 88


def test_valid_pipeline_transitions(tmp_path) -> None:
    session = build_test_session(tmp_path / "applicant_service_valid_transitions.db")
    service = ApplicantService(session=session)
    organization, client, job_order = _create_foundation(session)

    applicant = service.create_applicant(
        organization_id=organization.id,
        client_id=client.id,
        job_order_id=job_order.id,
        name="Alice Doe",
    )

    applicant = service.move_pipeline_stage(applicant.id, ApplicantPipelineStage.UNDER_REVIEW)
    applicant = service.move_pipeline_stage(applicant.id, ApplicantPipelineStage.PHONE_SCREEN)
    applicant = service.move_pipeline_stage(applicant.id, ApplicantPipelineStage.INTERVIEW)

    assert applicant.pipeline_stage == ApplicantPipelineStage.INTERVIEW


def test_invalid_pipeline_transitions(tmp_path) -> None:
    session = build_test_session(tmp_path / "applicant_service_invalid_transitions.db")
    service = ApplicantService(session=session)
    organization, client, job_order = _create_foundation(session)

    applicant = service.create_applicant(
        organization_id=organization.id,
        client_id=client.id,
        job_order_id=job_order.id,
        name="Alice Doe",
    )

    with pytest.raises(BlackcrestInputError):
        service.move_pipeline_stage(applicant.id, ApplicantPipelineStage.INTERVIEW)

    moved = service.move_pipeline_stage(applicant.id, ApplicantPipelineStage.UNDER_REVIEW)
    moved = service.move_pipeline_stage(moved.id, ApplicantPipelineStage.REJECTED)

    with pytest.raises(BlackcrestInputError):
        service.move_pipeline_stage(moved.id, ApplicantPipelineStage.PHONE_SCREEN)
