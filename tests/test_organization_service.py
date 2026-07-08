from __future__ import annotations

import pytest

from models.organization import OrganizationStatus
from services.organization_service import OrganizationService
from tests.helpers import build_test_session
from utils.exceptions import BlackcrestInputError


def test_create_organization(tmp_path) -> None:
    session = build_test_session(tmp_path / "organization_service_create.db")
    service = OrganizationService(session=session)

    organization = service.create_organization(
        name="Greater Connections Staffing",
        legal_name="Greater Connections Staffing LLC",
        status=OrganizationStatus.ACTIVE,
        email="ops@greaterconnect.com",
    )

    assert organization.id is not None
    assert organization.name == "Greater Connections Staffing"
    assert organization.status == OrganizationStatus.ACTIVE


def test_duplicate_organization_rejected(tmp_path) -> None:
    session = build_test_session(tmp_path / "organization_service_duplicate.db")
    service = OrganizationService(session=session)

    service.create_organization(
        name="Greater Connections Staffing",
        status=OrganizationStatus.ACTIVE,
    )

    with pytest.raises(BlackcrestInputError):
        service.create_organization(
            name="greater connections staffing",
            status=OrganizationStatus.ACTIVE,
        )


def test_retrieve_organization_by_id(tmp_path) -> None:
    session = build_test_session(tmp_path / "organization_service_get.db")
    service = OrganizationService(session=session)

    created = service.create_organization(
        name="Greater Connections Staffing",
        status=OrganizationStatus.ACTIVE,
    )

    retrieved = service.get_organization(created.id)

    assert retrieved.id == created.id
    assert retrieved.name == created.name


def test_list_organizations(tmp_path) -> None:
    session = build_test_session(tmp_path / "organization_service_list.db")
    service = OrganizationService(session=session)

    service.create_organization(name="Org One", status=OrganizationStatus.ACTIVE)
    service.create_organization(name="Org Two", status=OrganizationStatus.INACTIVE)

    organizations = service.list_organizations()

    assert len(organizations) == 2
    assert all(organization.id is not None for organization in organizations)


def test_update_organization(tmp_path) -> None:
    session = build_test_session(tmp_path / "organization_service_update.db")
    service = OrganizationService(session=session)

    organization = service.create_organization(
        name="Greater Connections Staffing",
        legal_name="Greater Connections Staffing LLC",
        status=OrganizationStatus.ACTIVE,
        phone="555-0100",
    )
    original_updated_at = organization.updated_at

    updated = service.update_organization(
        organization.id,
        name="Greater Connections Staffing Midwest",
        legal_name="Greater Connections Staffing Midwest LLC",
        phone="555-9999",
        city="Milwaukee",
        state="WI",
        country="USA",
    )

    assert updated.name == "Greater Connections Staffing Midwest"
    assert updated.legal_name == "Greater Connections Staffing Midwest LLC"
    assert updated.phone == "555-9999"
    assert updated.city == "Milwaukee"
    assert updated.state == "WI"
    assert updated.country == "USA"
    assert updated.updated_at > original_updated_at


def test_duplicate_update_rejected(tmp_path) -> None:
    session = build_test_session(tmp_path / "organization_service_update_duplicate.db")
    service = OrganizationService(session=session)

    first = service.create_organization(name="Org One", status=OrganizationStatus.ACTIVE)
    service.create_organization(name="Org Two", status=OrganizationStatus.ACTIVE)

    with pytest.raises(BlackcrestInputError):
        service.update_organization(first.id, name="org two")


def test_activate_organization(tmp_path) -> None:
    session = build_test_session(tmp_path / "organization_service_activate.db")
    service = OrganizationService(session=session)

    organization = service.create_organization(
        name="Org Activate",
        status=OrganizationStatus.INACTIVE,
    )

    activated = service.activate_organization(organization.id)

    assert activated.status == OrganizationStatus.ACTIVE


def test_activate_already_active_organization(tmp_path) -> None:
    session = build_test_session(tmp_path / "organization_service_activate_active.db")
    service = OrganizationService(session=session)

    organization = service.create_organization(
        name="Org Active",
        status=OrganizationStatus.ACTIVE,
    )

    with pytest.raises(BlackcrestInputError):
        service.activate_organization(organization.id)


def test_deactivate_organization(tmp_path) -> None:
    session = build_test_session(tmp_path / "organization_service_deactivate.db")
    service = OrganizationService(session=session)

    organization = service.create_organization(
        name="Org Deactivate",
        status=OrganizationStatus.ACTIVE,
    )

    deactivated = service.deactivate_organization(organization.id)

    assert deactivated.status == OrganizationStatus.INACTIVE


def test_deactivate_already_inactive_organization(tmp_path) -> None:
    session = build_test_session(tmp_path / "organization_service_deactivate_inactive.db")
    service = OrganizationService(session=session)

    organization = service.create_organization(
        name="Org Inactive",
        status=OrganizationStatus.INACTIVE,
    )

    with pytest.raises(BlackcrestInputError):
        service.deactivate_organization(organization.id)
