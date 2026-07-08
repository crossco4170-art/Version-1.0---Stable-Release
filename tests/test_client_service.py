from __future__ import annotations

import pytest

from models.client import ClientStatus
from models.organization import Organization, OrganizationStatus
from services.client_service import ClientService
from tests.helpers import build_test_session
from utils.exceptions import BlackcrestInputError


def _create_organization(session, name: str) -> Organization:
    organization = Organization(
        name=name,
        legal_name=f"{name} LLC",
        status=OrganizationStatus.ACTIVE,
    )
    session.add(organization)
    session.commit()
    return organization


def test_create_client(tmp_path) -> None:
    session = build_test_session(tmp_path / "client_service_create.db")
    service = ClientService(session=session)
    organization = _create_organization(session, "Greater Connections Staffing")

    client = service.create_client(
        organization_id=organization.id,
        company_name="USPS",
        contact_name="Hiring Lead",
        status=ClientStatus.ACTIVE,
    )

    assert client.id is not None
    assert client.organization_id == organization.id
    assert client.company_name == "USPS"
    assert client.status == ClientStatus.ACTIVE


def test_duplicate_client_rejected_within_organization(tmp_path) -> None:
    session = build_test_session(tmp_path / "client_service_duplicate_same_org.db")
    service = ClientService(session=session)
    organization = _create_organization(session, "Greater Connections Staffing")

    service.create_client(organization_id=organization.id, company_name="USPS")

    with pytest.raises(BlackcrestInputError):
        service.create_client(organization_id=organization.id, company_name="usps")


def test_same_client_name_allowed_in_different_organizations(tmp_path) -> None:
    session = build_test_session(tmp_path / "client_service_duplicate_different_org.db")
    service = ClientService(session=session)
    org_a = _create_organization(session, "Greater Connections Staffing")
    org_b = _create_organization(session, "Next Horizon Staffing")

    first = service.create_client(organization_id=org_a.id, company_name="USPS")
    second = service.create_client(organization_id=org_b.id, company_name="USPS")

    assert first.id != second.id
    assert first.organization_id != second.organization_id


def test_retrieve_client(tmp_path) -> None:
    session = build_test_session(tmp_path / "client_service_get.db")
    service = ClientService(session=session)
    organization = _create_organization(session, "Greater Connections Staffing")

    created = service.create_client(organization_id=organization.id, company_name="USPS")
    retrieved = service.get_client(created.id)

    assert retrieved.id == created.id
    assert retrieved.company_name == "USPS"


def test_list_clients(tmp_path) -> None:
    session = build_test_session(tmp_path / "client_service_list.db")
    service = ClientService(session=session)
    organization = _create_organization(session, "Greater Connections Staffing")

    service.create_client(organization_id=organization.id, company_name="USPS")
    service.create_client(organization_id=organization.id, company_name="Amazon")

    clients = service.list_clients()

    assert len(clients) == 2
    assert {client.company_name for client in clients} == {"USPS", "Amazon"}


def test_list_clients_by_organization(tmp_path) -> None:
    session = build_test_session(tmp_path / "client_service_list_by_org.db")
    service = ClientService(session=session)
    org_a = _create_organization(session, "Greater Connections Staffing")
    org_b = _create_organization(session, "Next Horizon Staffing")

    service.create_client(organization_id=org_a.id, company_name="USPS")
    service.create_client(organization_id=org_a.id, company_name="Amazon")
    service.create_client(organization_id=org_b.id, company_name="FedEx")

    org_a_clients = service.list_clients_by_organization(org_a.id)

    assert len(org_a_clients) == 2
    assert {client.company_name for client in org_a_clients} == {"USPS", "Amazon"}


def test_update_client(tmp_path) -> None:
    session = build_test_session(tmp_path / "client_service_update.db")
    service = ClientService(session=session)
    organization = _create_organization(session, "Greater Connections Staffing")

    client = service.create_client(
        organization_id=organization.id,
        company_name="USPS",
        contact_name="Initial Contact",
    )
    original_updated_at = client.updated_at

    updated = service.update_client(
        client.id,
        company_name="USPS National",
        contact_name="Updated Contact",
        city="Washington",
        state="DC",
        notes="Preferred partner",
    )

    assert updated.company_name == "USPS National"
    assert updated.contact_name == "Updated Contact"
    assert updated.city == "Washington"
    assert updated.state == "DC"
    assert updated.notes == "Preferred partner"
    assert updated.organization_id == organization.id
    assert updated.updated_at > original_updated_at


def test_activate_client(tmp_path) -> None:
    session = build_test_session(tmp_path / "client_service_activate.db")
    service = ClientService(session=session)
    organization = _create_organization(session, "Greater Connections Staffing")

    client = service.create_client(
        organization_id=organization.id,
        company_name="USPS",
        status=ClientStatus.INACTIVE,
    )

    activated = service.activate_client(client.id)

    assert activated.status == ClientStatus.ACTIVE


def test_deactivate_client(tmp_path) -> None:
    session = build_test_session(tmp_path / "client_service_deactivate.db")
    service = ClientService(session=session)
    organization = _create_organization(session, "Greater Connections Staffing")

    client = service.create_client(
        organization_id=organization.id,
        company_name="USPS",
        status=ClientStatus.ACTIVE,
    )

    deactivated = service.deactivate_client(client.id)

    assert deactivated.status == ClientStatus.INACTIVE


def test_invalid_lifecycle_transitions(tmp_path) -> None:
    session = build_test_session(tmp_path / "client_service_invalid_transitions.db")
    service = ClientService(session=session)
    organization = _create_organization(session, "Greater Connections Staffing")

    active_client = service.create_client(
        organization_id=organization.id,
        company_name="USPS",
        status=ClientStatus.ACTIVE,
    )
    inactive_client = service.create_client(
        organization_id=organization.id,
        company_name="Amazon",
        status=ClientStatus.INACTIVE,
    )

    with pytest.raises(BlackcrestInputError):
        service.activate_client(active_client.id)

    with pytest.raises(BlackcrestInputError):
        service.deactivate_client(inactive_client.id)
