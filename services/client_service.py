from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.client import Client
from models.client import ClientStatus
from services.base_service import BaseCRUDService
from utils.datetime_policy import utc_now_naive
from utils.exceptions import BlackcrestInputError, BlackcrestNotFoundError


class ClientService(BaseCRUDService[Client]):
    """CRUD service for client records."""

    def __init__(self, session: Session | None = None, database_url: str | None = None) -> None:
        super().__init__(Client, session, database_url)

    def _validate_organization_id(self, organization_id: int) -> int:
        if organization_id <= 0:
            raise BlackcrestInputError("Organization ID must be greater than zero")
        return organization_id

    def _validate_company_name(self, company_name: str) -> str:
        if not company_name or not company_name.strip():
            raise BlackcrestInputError("Client company name is required")
        return company_name.strip()

    def _validate_status(self, status: ClientStatus | str) -> ClientStatus:
        if status is None:
            raise BlackcrestInputError("Client status is required")
        if isinstance(status, ClientStatus):
            return status

        normalized = str(status).strip().upper()
        if not normalized:
            raise BlackcrestInputError("Client status is required")

        try:
            return ClientStatus(normalized)
        except ValueError as exc:
            raise BlackcrestInputError("Client status must be ACTIVE, INACTIVE, or SUSPENDED") from exc

    def _ensure_unique_name_within_organization(self, organization_id: int, company_name: str) -> None:
        existing = (
            self.session.query(Client)
            .filter(
                Client.organization_id == organization_id,
                func.lower(Client.company_name) == company_name.lower(),
            )
            .first()
        )
        if existing is not None:
            raise BlackcrestInputError("Client company name already exists for this organization")

    def _ensure_unique_name_within_organization_for_update(
        self,
        client_id: int,
        organization_id: int,
        company_name: str,
    ) -> None:
        existing = (
            self.session.query(Client)
            .filter(
                Client.organization_id == organization_id,
                func.lower(Client.company_name) == company_name.lower(),
                Client.id != client_id,
            )
            .first()
        )
        if existing is not None:
            raise BlackcrestInputError("Client company name already exists for this organization")

    def create_client(
        self,
        *,
        organization_id: int,
        company_name: str,
        status: ClientStatus | str = ClientStatus.ACTIVE,
        contact_name: str | None = None,
        contact_title: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        website: str | None = None,
        street_address: str | None = None,
        city: str | None = None,
        state: str | None = None,
        zip_code: str | None = None,
        country: str | None = None,
        notes: str | None = None,
    ) -> Client:
        """Create and persist a client belonging to an organization."""
        validated_organization_id = self._validate_organization_id(organization_id)
        normalized_company_name = self._validate_company_name(company_name)
        normalized_status = self._validate_status(status)
        self._ensure_unique_name_within_organization(validated_organization_id, normalized_company_name)

        client = Client(
            organization_id=validated_organization_id,
            company_name=normalized_company_name,
            status=normalized_status,
            contact_name=contact_name.strip() if contact_name and contact_name.strip() else None,
            contact_title=contact_title.strip() if contact_title and contact_title.strip() else None,
            email=email.strip() if email and email.strip() else None,
            phone=phone.strip() if phone and phone.strip() else None,
            website=website.strip() if website and website.strip() else None,
            street_address=street_address.strip() if street_address and street_address.strip() else None,
            city=city.strip() if city and city.strip() else None,
            state=state.strip() if state and state.strip() else None,
            zip_code=zip_code.strip() if zip_code and zip_code.strip() else None,
            country=country.strip() if country and country.strip() else None,
            notes=notes.strip() if notes and notes.strip() else None,
        )
        self.session.add(client)
        self.session.commit()
        self.session.refresh(client)
        return client

    def get_client(self, client_id: int) -> Client:
        """Retrieve a client by identifier or raise when not found."""
        if client_id <= 0:
            raise BlackcrestInputError("Client ID must be greater than zero")

        client = self.session.get(Client, client_id)
        if client is None:
            raise BlackcrestNotFoundError(f"Client not found: {client_id}")
        return client

    def list_clients(self) -> list[Client]:
        """Return all clients ordered by newest creation timestamp first."""
        return list(self.session.query(Client).order_by(Client.created_at.desc()).all())

    def list_clients_by_organization(self, organization_id: int) -> list[Client]:
        """Return clients for one organization ordered by newest creation timestamp first."""
        validated_organization_id = self._validate_organization_id(organization_id)
        return list(
            self.session.query(Client)
            .filter(Client.organization_id == validated_organization_id)
            .order_by(Client.created_at.desc())
            .all()
        )

    def update_client(
        self,
        client_id: int,
        *,
        company_name: str | None = None,
        contact_name: str | None = None,
        contact_title: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        website: str | None = None,
        street_address: str | None = None,
        city: str | None = None,
        state: str | None = None,
        zip_code: str | None = None,
        country: str | None = None,
        notes: str | None = None,
    ) -> Client:
        """Update mutable client fields and refresh the update timestamp."""
        client = self.get_client(client_id)

        if company_name is not None:
            normalized_company_name = self._validate_company_name(company_name)
            self._ensure_unique_name_within_organization_for_update(
                client.id,
                client.organization_id,
                normalized_company_name,
            )
            client.company_name = normalized_company_name

        if contact_name is not None:
            client.contact_name = contact_name.strip() if contact_name.strip() else None
        if contact_title is not None:
            client.contact_title = contact_title.strip() if contact_title.strip() else None
        if email is not None:
            client.email = email.strip() if email.strip() else None
        if phone is not None:
            client.phone = phone.strip() if phone.strip() else None
        if website is not None:
            client.website = website.strip() if website.strip() else None
        if street_address is not None:
            client.street_address = street_address.strip() if street_address.strip() else None
        if city is not None:
            client.city = city.strip() if city.strip() else None
        if state is not None:
            client.state = state.strip() if state.strip() else None
        if zip_code is not None:
            client.zip_code = zip_code.strip() if zip_code.strip() else None
        if country is not None:
            client.country = country.strip() if country.strip() else None
        if notes is not None:
            client.notes = notes.strip() if notes.strip() else None

        client.updated_at = utc_now_naive()
        self.session.commit()
        self.session.refresh(client)
        return client

    def activate_client(self, client_id: int) -> Client:
        """Set client status to ACTIVE unless it is already active."""
        client = self.get_client(client_id)
        if client.status == ClientStatus.ACTIVE:
            raise BlackcrestInputError("Client is already ACTIVE")

        client.status = ClientStatus.ACTIVE
        client.updated_at = utc_now_naive()
        self.session.commit()
        self.session.refresh(client)
        return client

    def deactivate_client(self, client_id: int) -> Client:
        """Set client status to INACTIVE unless it is already inactive."""
        client = self.get_client(client_id)
        if client.status == ClientStatus.INACTIVE:
            raise BlackcrestInputError("Client is already INACTIVE")

        client.status = ClientStatus.INACTIVE
        client.updated_at = utc_now_naive()
        self.session.commit()
        self.session.refresh(client)
        return client
