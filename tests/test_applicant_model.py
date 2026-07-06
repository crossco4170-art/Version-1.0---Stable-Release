from __future__ import annotations

from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError

from models.applicant import Applicant, ApplicantPipelineStage
from models.client import Client
from models.job_order import JobOrder
from models.organization import Organization, OrganizationStatus
from tests.helpers import build_test_session


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


def test_applicant_creation(tmp_path) -> None:
    session = build_test_session(tmp_path / "applicant_creation.db")
    organization, client, job_order = _create_foundation(session)

    applicant = Applicant(
        organization_id=organization.id,
        client_id=client.id,
        job_order_id=job_order.id,
        name="Jane Doe",
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
        phone="555-0100",
        city="Milwaukee",
        state="WI",
        resume_filename="jane_resume.pdf",
        resume_path="/resumes/jane_resume.pdf",
        resume_score=92.5,
    )
    session.add(applicant)
    session.commit()

    assert applicant.id is not None
    assert applicant.first_name == "Jane"
    assert applicant.last_name == "Doe"


def test_organization_relationship(tmp_path) -> None:
    session = build_test_session(tmp_path / "applicant_org_rel.db")
    organization, client, job_order = _create_foundation(session)

    applicant = Applicant(
        organization_id=organization.id,
        client_id=client.id,
        job_order_id=job_order.id,
        name="Jane Doe",
    )
    session.add(applicant)
    session.commit()

    assert applicant.organization.id == organization.id


def test_client_relationship(tmp_path) -> None:
    session = build_test_session(tmp_path / "applicant_client_rel.db")
    organization, client, job_order = _create_foundation(session)

    applicant = Applicant(
        organization_id=organization.id,
        client_id=client.id,
        job_order_id=job_order.id,
        name="Jane Doe",
    )
    session.add(applicant)
    session.commit()

    assert applicant.client.id == client.id


def test_job_order_relationship(tmp_path) -> None:
    session = build_test_session(tmp_path / "applicant_job_order_rel.db")
    organization, client, job_order = _create_foundation(session)

    applicant = Applicant(
        organization_id=organization.id,
        client_id=client.id,
        job_order_id=job_order.id,
        name="Jane Doe",
    )
    session.add(applicant)
    session.commit()

    assert applicant.job_order.id == job_order.id


def test_default_pipeline_stage(tmp_path) -> None:
    session = build_test_session(tmp_path / "applicant_default_stage.db")
    organization, client, job_order = _create_foundation(session)

    applicant = Applicant(
        organization_id=organization.id,
        client_id=client.id,
        job_order_id=job_order.id,
        name="Jane Doe",
    )
    session.add(applicant)
    session.commit()

    assert applicant.pipeline_stage == ApplicantPipelineStage.NEW


def test_resume_score_validation(tmp_path) -> None:
    session = build_test_session(tmp_path / "applicant_resume_score_validation.db")
    organization, client, job_order = _create_foundation(session)

    applicant = Applicant(
        organization_id=organization.id,
        client_id=client.id,
        job_order_id=job_order.id,
        name="Jane Doe",
        resume_score=120,
    )
    session.add(applicant)

    with pytest.raises(IntegrityError):
        session.commit()

    session.rollback()


def test_timestamp_creation(tmp_path) -> None:
    session = build_test_session(tmp_path / "applicant_timestamps.db")
    organization, client, job_order = _create_foundation(session)

    applicant = Applicant(
        organization_id=organization.id,
        client_id=client.id,
        job_order_id=job_order.id,
        name="Jane Doe",
    )
    session.add(applicant)
    session.commit()

    assert isinstance(applicant.created_at, datetime)
    assert isinstance(applicant.updated_at, datetime)
    assert isinstance(applicant.applied_at, datetime)
    assert isinstance(applicant.last_activity_at, datetime)
    assert applicant.created_at is not None
    assert applicant.updated_at is not None


def test_required_foreign_keys(tmp_path) -> None:
    _ = build_test_session(tmp_path / "applicant_required_fks.db")

    organization_column = Applicant.__table__.c.organization_id
    client_column = Applicant.__table__.c.client_id
    job_order_column = Applicant.__table__.c.job_order_id

    assert organization_column.nullable is False
    assert client_column.nullable is False
    assert job_order_column.nullable is False


def test_same_email_allowed_on_different_job_orders(tmp_path) -> None:
    session = build_test_session(tmp_path / "applicant_email_diff_job_orders.db")
    organization, client, first_job_order = _create_foundation(session)

    second_job_order = JobOrder(
        organization_id=organization.id,
        client_id=client.id,
        job_code="USPS-RCA-2026-002",
        title="Rural Carrier Associate Backup",
    )
    session.add(second_job_order)
    session.commit()

    first = Applicant(
        organization_id=organization.id,
        client_id=client.id,
        job_order_id=first_job_order.id,
        name="Jane Doe",
        email="jane@example.com",
    )
    second = Applicant(
        organization_id=organization.id,
        client_id=client.id,
        job_order_id=second_job_order.id,
        name="Jane Doe",
        email="jane@example.com",
    )

    session.add(first)
    session.add(second)
    session.commit()

    assert first.id != second.id


def test_duplicate_email_rejected_for_same_job_order(tmp_path) -> None:
    session = build_test_session(tmp_path / "applicant_email_same_job_order.db")
    organization, client, job_order = _create_foundation(session)

    first = Applicant(
        organization_id=organization.id,
        client_id=client.id,
        job_order_id=job_order.id,
        name="Jane Doe",
        email="jane@example.com",
    )
    duplicate = Applicant(
        organization_id=organization.id,
        client_id=client.id,
        job_order_id=job_order.id,
        name="Jane Doe",
        email="jane@example.com",
    )

    session.add(first)
    session.commit()

    session.add(duplicate)
    with pytest.raises(IntegrityError):
        session.commit()

    session.rollback()
