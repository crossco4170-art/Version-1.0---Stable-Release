from __future__ import annotations

from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError

from models.client import Client
from models.job_order import JobOrder, JobOrderStatus
from models.organization import Organization, OrganizationStatus
from tests.helpers import build_test_session


def _create_organization(session) -> Organization:
    organization = Organization(
        name="Greater Connections Staffing",
        legal_name="Greater Connections Staffing LLC",
        status=OrganizationStatus.ACTIVE,
    )
    session.add(organization)
    session.commit()
    return organization


def _create_client(session, organization_id: int, company_name: str = "USPS") -> Client:
    client = Client(
        organization_id=organization_id,
        company_name=company_name,
    )
    session.add(client)
    session.commit()
    return client


def test_job_order_creation(tmp_path) -> None:
    session = build_test_session(tmp_path / "job_order_creation.db")
    organization = _create_organization(session)
    client = _create_client(session, organization.id)

    job_order = JobOrder(
        organization_id=organization.id,
        client_id=client.id,
        job_code="USPS-RCA-2026-001",
        title="Rural Carrier Associate",
        employment_type="Full-Time",
    )
    session.add(job_order)
    session.commit()

    assert job_order.id is not None
    assert job_order.job_code == "USPS-RCA-2026-001"


def test_job_order_organization_relationship(tmp_path) -> None:
    session = build_test_session(tmp_path / "job_order_org_relationship.db")
    organization = _create_organization(session)
    client = _create_client(session, organization.id)

    job_order = JobOrder(
        organization_id=organization.id,
        client_id=client.id,
        job_code="USPS-RCA-2026-001",
        title="Rural Carrier Associate",
    )
    session.add(job_order)
    session.commit()

    assert job_order.organization.id == organization.id
    assert job_order.organization.name == "Greater Connections Staffing"


def test_job_order_client_relationship(tmp_path) -> None:
    session = build_test_session(tmp_path / "job_order_client_relationship.db")
    organization = _create_organization(session)
    client = _create_client(session, organization.id, company_name="Amazon")

    job_order = JobOrder(
        organization_id=organization.id,
        client_id=client.id,
        job_code="AMZ-DSP-2026-001",
        title="Delivery Associate",
    )
    session.add(job_order)
    session.commit()

    assert job_order.client.id == client.id
    assert job_order.client.company_name == "Amazon"


def test_job_order_default_status_is_draft(tmp_path) -> None:
    session = build_test_session(tmp_path / "job_order_default_status.db")
    organization = _create_organization(session)
    client = _create_client(session, organization.id)

    job_order = JobOrder(
        organization_id=organization.id,
        client_id=client.id,
        job_code="USPS-RCA-2026-001",
        title="Rural Carrier Associate",
    )
    session.add(job_order)
    session.commit()

    assert job_order.status == JobOrderStatus.DRAFT


def test_job_order_requires_foreign_keys(tmp_path) -> None:
    session = build_test_session(tmp_path / "job_order_required_foreign_keys.db")

    job_order = JobOrder(
        job_code="USPS-RCA-2026-001",
        title="Rural Carrier Associate",
    )
    session.add(job_order)

    with pytest.raises(IntegrityError):
        session.commit()

    session.rollback()


def test_job_order_timestamp_creation(tmp_path) -> None:
    session = build_test_session(tmp_path / "job_order_timestamps.db")
    organization = _create_organization(session)
    client = _create_client(session, organization.id)

    job_order = JobOrder(
        organization_id=organization.id,
        client_id=client.id,
        job_code="USPS-RCA-2026-001",
        title="Rural Carrier Associate",
    )
    session.add(job_order)
    session.commit()

    assert isinstance(job_order.created_at, datetime)
    assert isinstance(job_order.updated_at, datetime)
    assert job_order.created_at is not None
    assert job_order.updated_at is not None


def test_job_code_uniqueness_within_organization(tmp_path) -> None:
    session = build_test_session(tmp_path / "job_order_unique_job_code.db")
    organization = _create_organization(session)
    client = _create_client(session, organization.id)

    first = JobOrder(
        organization_id=organization.id,
        client_id=client.id,
        job_code="USPS-RCA-2026-001",
        title="Rural Carrier Associate",
    )
    session.add(first)
    session.commit()

    duplicate = JobOrder(
        organization_id=organization.id,
        client_id=client.id,
        job_code="USPS-RCA-2026-001",
        title="Rural Carrier Associate - Evening",
    )
    session.add(duplicate)

    with pytest.raises(IntegrityError):
        session.commit()

    session.rollback()
