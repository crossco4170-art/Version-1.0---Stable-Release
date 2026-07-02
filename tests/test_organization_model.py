from __future__ import annotations

from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError

from models.organization import Organization, OrganizationStatus
from tests.helpers import build_test_session


def test_organization_creation(tmp_path) -> None:
    session = build_test_session(tmp_path / "organization_creation.db")

    organization = Organization(
        name="Greater Connections Staffing",
        legal_name="Greater Connections Staffing LLC",
        phone="555-0100",
        email="ops@greaterconnect.com",
        website="https://greaterconnect.com",
        street_address="123 Main St",
        city="Milwaukee",
        state="WI",
        zip_code="53202",
        country="USA",
    )

    session.add(organization)
    session.commit()

    assert organization.id is not None
    assert organization.name == "Greater Connections Staffing"
    assert organization.legal_name == "Greater Connections Staffing LLC"


def test_default_status_is_active(tmp_path) -> None:
    session = build_test_session(tmp_path / "organization_default_status.db")

    organization = Organization(
        name="Greater Connections Staffing",
        legal_name="Greater Connections Staffing LLC",
    )

    session.add(organization)
    session.commit()

    assert organization.status == OrganizationStatus.ACTIVE


def test_required_fields_enforced(tmp_path) -> None:
    session = build_test_session(tmp_path / "organization_required_fields.db")

    organization = Organization(legal_name="Greater Connections Staffing LLC")
    session.add(organization)

    with pytest.raises(IntegrityError):
        session.commit()

    session.rollback()


def test_timestamp_creation(tmp_path) -> None:
    session = build_test_session(tmp_path / "organization_timestamps.db")

    organization = Organization(
        name="Greater Connections Staffing",
        legal_name="Greater Connections Staffing LLC",
    )

    session.add(organization)
    session.commit()

    assert isinstance(organization.created_at, datetime)
    assert isinstance(organization.updated_at, datetime)
    assert organization.created_at is not None
    assert organization.updated_at is not None
