from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from database.connection import get_session
from models.organization import Organization, OrganizationStatus
from services.base_service import BaseCRUDService
from utils.datetime_policy import utc_now_naive
from utils.exceptions import BlackcrestInputError, BlackcrestNotFoundError


class OrganizationService(BaseCRUDService[Organization]):
    """Business-layer operations for organization records."""

    def __init__(self, session: Session | None = None, database_url: str | None = None) -> None:
        super().__init__(Organization, session, database_url)

    def _validate_name(self, name: str) -> str:
        if not name or not name.strip():
            raise BlackcrestInputError("Organization name is required")
        return name.strip()

    def _validate_status(self, status: OrganizationStatus | str) -> OrganizationStatus:
        if status is None:
            raise BlackcrestInputError("Organization status is required")
        if isinstance(status, OrganizationStatus):
            return status

        normalized = str(status).strip().upper()
        if not normalized:
            raise BlackcrestInputError("Organization status is required")

        try:
            return OrganizationStatus(normalized)
        except ValueError as exc:
            raise BlackcrestInputError("Organization status must be ACTIVE, INACTIVE, or SUSPENDED") from exc

    def _ensure_unique_name(self, name: str) -> None:
        existing = (
            self.session.query(Organization)
            .filter(func.lower(Organization.name) == name.lower())
            .first()
        )
        if existing is not None:
            raise BlackcrestInputError("Organization name already exists")

    def _ensure_unique_name_for_update(self, name: str, organization_id: int) -> None:
        existing = (
            self.session.query(Organization)
            .filter(func.lower(Organization.name) == name.lower(), Organization.id != organization_id)
            .first()
        )
        if existing is not None:
            raise BlackcrestInputError("Organization name already exists")

    def create_organization(
        self,
        *,
        name: str,
        status: OrganizationStatus | str,
        legal_name: str | None = None,
        phone: str | None = None,
        email: str | None = None,
        website: str | None = None,
        street_address: str | None = None,
        city: str | None = None,
        state: str | None = None,
        zip_code: str | None = None,
        country: str | None = None,
    ) -> Organization:
        """Create and persist a new organization record."""
        normalized_name = self._validate_name(name)
        normalized_status = self._validate_status(status)
        self._ensure_unique_name(normalized_name)

        organization = Organization(
            name=normalized_name,
            legal_name=(legal_name.strip() if legal_name and legal_name.strip() else normalized_name),
            status=normalized_status,
            phone=phone.strip() if phone and phone.strip() else None,
            email=email.strip() if email and email.strip() else None,
            website=website.strip() if website and website.strip() else None,
            street_address=street_address.strip() if street_address and street_address.strip() else None,
            city=city.strip() if city and city.strip() else None,
            state=state.strip() if state and state.strip() else None,
            zip_code=zip_code.strip() if zip_code and zip_code.strip() else None,
            country=country.strip() if country and country.strip() else None,
        )
        self.session.add(organization)
        self.session.commit()
        self.session.refresh(organization)
        return organization

    def get_organization(self, organization_id: int) -> Organization:
        """Retrieve an organization by identifier or raise when not found."""
        if organization_id <= 0:
            raise BlackcrestInputError("Organization ID must be greater than zero")

        organization = self.session.get(Organization, organization_id)
        if organization is None:
            raise BlackcrestNotFoundError(f"Organization not found: {organization_id}")
        return organization

    def list_organizations(self) -> list[Organization]:
        """Return organizations ordered by newest creation timestamp first."""
        return list(self.session.query(Organization).order_by(Organization.created_at.desc()).all())

    def update_organization(
        self,
        organization_id: int,
        *,
        name: str | None = None,
        legal_name: str | None = None,
        phone: str | None = None,
        email: str | None = None,
        website: str | None = None,
        street_address: str | None = None,
        city: str | None = None,
        state: str | None = None,
        zip_code: str | None = None,
        country: str | None = None,
    ) -> Organization:
        """Update allowed mutable organization fields and refresh the update timestamp."""
        organization = self.get_organization(organization_id)

        if name is not None:
            normalized_name = self._validate_name(name)
            self._ensure_unique_name_for_update(normalized_name, organization_id)
            organization.name = normalized_name

        if legal_name is not None:
            organization.legal_name = legal_name.strip() if legal_name.strip() else organization.legal_name
        if phone is not None:
            organization.phone = phone.strip() if phone.strip() else None
        if email is not None:
            organization.email = email.strip() if email.strip() else None
        if website is not None:
            organization.website = website.strip() if website.strip() else None
        if street_address is not None:
            organization.street_address = street_address.strip() if street_address.strip() else None
        if city is not None:
            organization.city = city.strip() if city.strip() else None
        if state is not None:
            organization.state = state.strip() if state.strip() else None
        if zip_code is not None:
            organization.zip_code = zip_code.strip() if zip_code.strip() else None
        if country is not None:
            organization.country = country.strip() if country.strip() else None

        organization.updated_at = utc_now_naive()
        self.session.commit()
        self.session.refresh(organization)
        return organization

    def activate_organization(self, organization_id: int) -> Organization:
        """Set organization status to ACTIVE unless it is already active."""
        organization = self.get_organization(organization_id)
        if organization.status == OrganizationStatus.ACTIVE:
            raise BlackcrestInputError("Organization is already ACTIVE")

        organization.status = OrganizationStatus.ACTIVE
        organization.updated_at = utc_now_naive()
        self.session.commit()
        self.session.refresh(organization)
        return organization

    def deactivate_organization(self, organization_id: int) -> Organization:
        """Set organization status to INACTIVE unless it is already inactive."""
        organization = self.get_organization(organization_id)
        if organization.status == OrganizationStatus.INACTIVE:
            raise BlackcrestInputError("Organization is already INACTIVE")

        organization.status = OrganizationStatus.INACTIVE
        organization.updated_at = utc_now_naive()
        self.session.commit()
        self.session.refresh(organization)
        return organization
