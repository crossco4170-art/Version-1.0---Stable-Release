from __future__ import annotations

import pytest

from models.client import Client
from models.job_order import JobOrderStatus
from models.organization import Organization, OrganizationStatus
from services.job_order_service import JobOrderService
from tests.helpers import build_test_session
from utils.exceptions import BlackcrestInputError


def _create_organization(session, name: str = "Greater Connections Staffing") -> Organization:
    organization = Organization(
        name=name,
        legal_name=f"{name} LLC",
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


def test_create_job_order(tmp_path) -> None:
    session = build_test_session(tmp_path / "job_order_service_create.db")
    service = JobOrderService(session=session)
    organization = _create_organization(session)
    client = _create_client(session, organization.id)

    job_order = service.create_job_order(
        organization_id=organization.id,
        client_id=client.id,
        job_code="USPS-RCA-2026-001",
        title="Rural Carrier Associate",
        number_of_openings=5,
        positions_filled=0,
    )

    assert job_order.id is not None
    assert job_order.organization_id == organization.id
    assert job_order.client_id == client.id


def test_duplicate_job_code_rejected(tmp_path) -> None:
    session = build_test_session(tmp_path / "job_order_service_duplicate_code.db")
    service = JobOrderService(session=session)
    organization = _create_organization(session)
    client = _create_client(session, organization.id)

    service.create_job_order(
        organization_id=organization.id,
        client_id=client.id,
        job_code="USPS-RCA-2026-001",
        title="Rural Carrier Associate",
    )

    with pytest.raises(BlackcrestInputError):
        service.create_job_order(
            organization_id=organization.id,
            client_id=client.id,
            job_code="usps-rca-2026-001",
            title="Rural Carrier Associate Evening",
        )


def test_list_job_orders(tmp_path) -> None:
    session = build_test_session(tmp_path / "job_order_service_list.db")
    service = JobOrderService(session=session)
    organization = _create_organization(session)
    client = _create_client(session, organization.id)

    service.create_job_order(
        organization_id=organization.id,
        client_id=client.id,
        job_code="USPS-RCA-2026-001",
        title="Rural Carrier Associate",
    )
    service.create_job_order(
        organization_id=organization.id,
        client_id=client.id,
        job_code="USPS-RCA-2026-002",
        title="Rural Carrier Associate Relief",
    )

    orders = service.list_job_orders()

    assert len(orders) == 2


def test_list_job_orders_by_client(tmp_path) -> None:
    session = build_test_session(tmp_path / "job_order_service_list_by_client.db")
    service = JobOrderService(session=session)
    organization = _create_organization(session)
    client_a = _create_client(session, organization.id, company_name="USPS")
    client_b = _create_client(session, organization.id, company_name="Amazon")

    service.create_job_order(
        organization_id=organization.id,
        client_id=client_a.id,
        job_code="USPS-RCA-2026-001",
        title="Rural Carrier Associate",
    )
    service.create_job_order(
        organization_id=organization.id,
        client_id=client_b.id,
        job_code="AMZ-DSP-2026-001",
        title="Delivery Associate",
    )

    client_a_orders = service.list_job_orders_by_client(client_a.id)

    assert len(client_a_orders) == 1
    assert client_a_orders[0].client_id == client_a.id


def test_list_job_orders_by_organization(tmp_path) -> None:
    session = build_test_session(tmp_path / "job_order_service_list_by_org.db")
    service = JobOrderService(session=session)
    org_a = _create_organization(session, name="Greater Connections Staffing")
    org_b = _create_organization(session, name="Next Horizon Staffing")
    client_a = _create_client(session, org_a.id, company_name="USPS")
    client_b = _create_client(session, org_b.id, company_name="FedEx")

    service.create_job_order(
        organization_id=org_a.id,
        client_id=client_a.id,
        job_code="USPS-RCA-2026-001",
        title="Rural Carrier Associate",
    )
    service.create_job_order(
        organization_id=org_b.id,
        client_id=client_b.id,
        job_code="FDX-DRV-2026-001",
        title="Delivery Driver",
    )

    org_a_orders = service.list_job_orders_by_organization(org_a.id)

    assert len(org_a_orders) == 1
    assert org_a_orders[0].organization_id == org_a.id


def test_update_job_order(tmp_path) -> None:
    session = build_test_session(tmp_path / "job_order_service_update.db")
    service = JobOrderService(session=session)
    organization = _create_organization(session)
    client = _create_client(session, organization.id)

    job_order = service.create_job_order(
        organization_id=organization.id,
        client_id=client.id,
        job_code="USPS-RCA-2026-001",
        title="Rural Carrier Associate",
        number_of_openings=5,
        positions_filled=1,
    )

    updated = service.update_job_order(
        job_order.id,
        title="Rural Carrier Associate - Priority",
        number_of_openings=6,
        positions_filled=2,
        work_location="Milwaukee",
    )

    assert updated.title == "Rural Carrier Associate - Priority"
    assert updated.number_of_openings == 6
    assert updated.positions_filled == 2
    assert updated.work_location == "Milwaukee"
    assert updated.job_code == "USPS-RCA-2026-001"


def test_open_job_order(tmp_path) -> None:
    session = build_test_session(tmp_path / "job_order_service_open.db")
    service = JobOrderService(session=session)
    organization = _create_organization(session)
    client = _create_client(session, organization.id)

    job_order = service.create_job_order(
        organization_id=organization.id,
        client_id=client.id,
        job_code="USPS-RCA-2026-001",
        title="Rural Carrier Associate",
    )

    opened = service.open_job_order(job_order.id)

    assert opened.status == JobOrderStatus.OPEN
    assert opened.date_opened is not None


def test_hold_job_order(tmp_path) -> None:
    session = build_test_session(tmp_path / "job_order_service_hold.db")
    service = JobOrderService(session=session)
    organization = _create_organization(session)
    client = _create_client(session, organization.id)

    job_order = service.create_job_order(
        organization_id=organization.id,
        client_id=client.id,
        job_code="USPS-RCA-2026-001",
        title="Rural Carrier Associate",
    )
    service.open_job_order(job_order.id)

    held = service.hold_job_order(job_order.id)

    assert held.status == JobOrderStatus.ON_HOLD


def test_close_job_order(tmp_path) -> None:
    session = build_test_session(tmp_path / "job_order_service_close.db")
    service = JobOrderService(session=session)
    organization = _create_organization(session)
    client = _create_client(session, organization.id)

    job_order = service.create_job_order(
        organization_id=organization.id,
        client_id=client.id,
        job_code="USPS-RCA-2026-001",
        title="Rural Carrier Associate",
    )

    closed = service.close_job_order(job_order.id)

    assert closed.status == JobOrderStatus.CLOSED
    assert closed.date_closed is not None


def test_mark_job_order_filled(tmp_path) -> None:
    session = build_test_session(tmp_path / "job_order_service_filled.db")
    service = JobOrderService(session=session)
    organization = _create_organization(session)
    client = _create_client(session, organization.id)

    job_order = service.create_job_order(
        organization_id=organization.id,
        client_id=client.id,
        job_code="USPS-RCA-2026-001",
        title="Rural Carrier Associate",
        number_of_openings=3,
    )

    filled = service.mark_job_order_filled(job_order.id)

    assert filled.status == JobOrderStatus.FILLED
    assert filled.positions_filled == 3


def test_invalid_lifecycle_transitions(tmp_path) -> None:
    session = build_test_session(tmp_path / "job_order_service_invalid_transitions.db")
    service = JobOrderService(session=session)
    organization = _create_organization(session)
    client = _create_client(session, organization.id)

    closed_order = service.create_job_order(
        organization_id=organization.id,
        client_id=client.id,
        job_code="USPS-RCA-2026-001",
        title="Rural Carrier Associate",
        status=JobOrderStatus.CLOSED,
    )
    filled_order = service.create_job_order(
        organization_id=organization.id,
        client_id=client.id,
        job_code="USPS-RCA-2026-002",
        title="Rural Carrier Associate Evening",
        status=JobOrderStatus.FILLED,
    )
    on_hold_order = service.create_job_order(
        organization_id=organization.id,
        client_id=client.id,
        job_code="USPS-RCA-2026-003",
        title="Rural Carrier Associate Weekend",
        status=JobOrderStatus.ON_HOLD,
    )

    with pytest.raises(BlackcrestInputError):
        service.open_job_order(closed_order.id)

    with pytest.raises(BlackcrestInputError):
        service.open_job_order(filled_order.id)

    with pytest.raises(BlackcrestInputError):
        service.open_job_order(on_hold_order.id)


def test_positions_filled_validation(tmp_path) -> None:
    session = build_test_session(tmp_path / "job_order_service_positions_validation.db")
    service = JobOrderService(session=session)
    organization = _create_organization(session)
    client = _create_client(session, organization.id)

    with pytest.raises(BlackcrestInputError):
        service.create_job_order(
            organization_id=organization.id,
            client_id=client.id,
            job_code="USPS-RCA-2026-001",
            title="Rural Carrier Associate",
            number_of_openings=2,
            positions_filled=3,
        )

    created = service.create_job_order(
        organization_id=organization.id,
        client_id=client.id,
        job_code="USPS-RCA-2026-002",
        title="Rural Carrier Associate Evening",
        number_of_openings=2,
        positions_filled=1,
    )

    with pytest.raises(BlackcrestInputError):
        service.update_job_order(created.id, positions_filled=4)
