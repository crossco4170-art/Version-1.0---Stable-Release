from __future__ import annotations

from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError

from models.client import Client, ClientStatus
from models.organization import Organization, OrganizationStatus
from tests.helpers import build_test_session


def test_client_creation(tmp_path) -> None:
    session = build_test_session(tmp_path / "client_creation.db")

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
        contact_name="Hiring Lead",
        contact_title="Talent Acquisition",
        email="usps@example.com",
        phone="555-0200",
        website="https://www.usps.com",
        street_address="475 L'Enfant Plaza SW",
        city="Washington",
        state="DC",
        zip_code="20260",
        country="USA",
        notes="Priority logistics client",
    )
    session.add(client)
    session.commit()

    assert client.id is not None
    assert client.organization_id == organization.id
    assert client.company_name == "USPS"


def test_client_organization_relationship(tmp_path) -> None:
    session = build_test_session(tmp_path / "client_organization_relationship.db")

    organization = Organization(
        name="Greater Connections Staffing",
        legal_name="Greater Connections Staffing LLC",
        status=OrganizationStatus.ACTIVE,
    )
    session.add(organization)
    session.commit()

    client = Client(
        organization_id=organization.id,
        company_name="Amazon",
    )
    session.add(client)
    session.commit()

    assert client.organization.id == organization.id
    assert client.organization.name == "Greater Connections Staffing"


def test_client_default_status_is_active(tmp_path) -> None:
    session = build_test_session(tmp_path / "client_default_status.db")

    organization = Organization(
        name="Greater Connections Staffing",
        legal_name="Greater Connections Staffing LLC",
        status=OrganizationStatus.ACTIVE,
    )
    session.add(organization)
    session.commit()

    client = Client(
        organization_id=organization.id,
        company_name="FedEx",
    )
    session.add(client)
    session.commit()

    assert client.status == ClientStatus.ACTIVE


def test_client_requires_organization_id(tmp_path) -> None:
    session = build_test_session(tmp_path / "client_requires_organization.db")

    client = Client(
        company_name="UPS",
    )
    session.add(client)

    with pytest.raises(IntegrityError):
        session.commit()

    session.rollback()


def test_client_timestamp_creation(tmp_path) -> None:
    session = build_test_session(tmp_path / "client_timestamps.db")

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

    assert isinstance(client.created_at, datetime)
    assert isinstance(client.updated_at, datetime)
    assert client.created_at is not None
    assert client.updated_at is not None
