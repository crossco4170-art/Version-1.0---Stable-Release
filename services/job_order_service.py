from __future__ import annotations

from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.client import Client
from models.job_order import JobOrder
from models.job_order import JobOrderStatus
from services.base_service import BaseCRUDService
from utils.datetime_policy import utc_now_naive
from utils.exceptions import BlackcrestInputError, BlackcrestNotFoundError


class JobOrderService(BaseCRUDService[JobOrder]):
    """CRUD service for job order records."""

    def __init__(self, session: Session | None = None, database_url: str | None = None) -> None:
        super().__init__(JobOrder, session, database_url)

    def _validate_organization_id(self, organization_id: int) -> int:
        if organization_id <= 0:
            raise BlackcrestInputError("Organization ID must be greater than zero")
        return organization_id

    def _validate_client_id(self, client_id: int) -> int:
        if client_id <= 0:
            raise BlackcrestInputError("Client ID must be greater than zero")
        return client_id

    def _validate_job_code(self, job_code: str) -> str:
        if not job_code or not job_code.strip():
            raise BlackcrestInputError("Job code is required")
        return job_code.strip()

    def _validate_title(self, title: str) -> str:
        if not title or not title.strip():
            raise BlackcrestInputError("Job order title is required")
        return title.strip()

    def _validate_status(self, status: JobOrderStatus | str) -> JobOrderStatus:
        if status is None:
            raise BlackcrestInputError("Job order status is required")
        if isinstance(status, JobOrderStatus):
            return status

        normalized = str(status).strip().upper()
        if not normalized:
            raise BlackcrestInputError("Job order status is required")

        try:
            return JobOrderStatus(normalized)
        except ValueError as exc:
            raise BlackcrestInputError("Job order status must be DRAFT, OPEN, ON_HOLD, CLOSED, or FILLED") from exc

    def _validate_client_organization(self, organization_id: int, client_id: int) -> Client:
        client = self.session.get(Client, client_id)
        if client is None:
            raise BlackcrestNotFoundError(f"Client not found: {client_id}")
        if client.organization_id != organization_id:
            raise BlackcrestInputError("Client does not belong to the provided organization")
        return client

    def _ensure_unique_job_code(self, organization_id: int, job_code: str) -> None:
        existing = (
            self.session.query(JobOrder)
            .filter(
                JobOrder.organization_id == organization_id,
                func.lower(JobOrder.job_code) == job_code.lower(),
            )
            .first()
        )
        if existing is not None:
            raise BlackcrestInputError("Job code already exists for this organization")

    def _validate_positions(self, number_of_openings: int | None, positions_filled: int | None) -> None:
        if number_of_openings is not None and number_of_openings < 0:
            raise BlackcrestInputError("Number of openings cannot be negative")
        if positions_filled is not None and positions_filled < 0:
            raise BlackcrestInputError("Positions filled cannot be negative")
        if (
            number_of_openings is not None
            and positions_filled is not None
            and positions_filled > number_of_openings
        ):
            raise BlackcrestInputError("Positions filled cannot exceed number of openings")

    def create_job_order(
        self,
        *,
        organization_id: int,
        client_id: int,
        job_code: str,
        title: str,
        description: str | None = None,
        employment_type: str | None = None,
        pay_min: float | None = None,
        pay_max: float | None = None,
        currency: str | None = None,
        number_of_openings: int | None = None,
        positions_filled: int | None = None,
        work_location: str | None = None,
        remote_allowed: bool = False,
        travel_required: bool = False,
        status: JobOrderStatus | str = JobOrderStatus.DRAFT,
        date_opened: date | None = None,
        date_closed: date | None = None,
    ) -> JobOrder:
        """Create and persist a job order within one organization and one client."""
        validated_organization_id = self._validate_organization_id(organization_id)
        validated_client_id = self._validate_client_id(client_id)
        normalized_job_code = self._validate_job_code(job_code)
        normalized_title = self._validate_title(title)
        normalized_status = self._validate_status(status)
        self._validate_client_organization(validated_organization_id, validated_client_id)
        self._ensure_unique_job_code(validated_organization_id, normalized_job_code)
        self._validate_positions(number_of_openings, positions_filled)

        job_order = JobOrder(
            organization_id=validated_organization_id,
            client_id=validated_client_id,
            job_code=normalized_job_code,
            title=normalized_title,
            description=description.strip() if description and description.strip() else None,
            employment_type=employment_type.strip() if employment_type and employment_type.strip() else None,
            pay_min=pay_min,
            pay_max=pay_max,
            currency=currency.strip() if currency and currency.strip() else None,
            number_of_openings=number_of_openings,
            positions_filled=positions_filled,
            work_location=work_location.strip() if work_location and work_location.strip() else None,
            remote_allowed=remote_allowed,
            travel_required=travel_required,
            status=normalized_status,
            date_opened=date_opened,
            date_closed=date_closed,
        )
        self.session.add(job_order)
        self.session.commit()
        self.session.refresh(job_order)
        return job_order

    def get_job_order(self, job_order_id: int) -> JobOrder:
        """Retrieve one job order by id or raise when missing."""
        if job_order_id <= 0:
            raise BlackcrestInputError("Job order ID must be greater than zero")

        job_order = self.session.get(JobOrder, job_order_id)
        if job_order is None:
            raise BlackcrestNotFoundError(f"Job order not found: {job_order_id}")
        return job_order

    def list_job_orders(self) -> list[JobOrder]:
        """Return all job orders ordered by newest creation timestamp first."""
        return list(self.session.query(JobOrder).order_by(JobOrder.created_at.desc()).all())

    def list_job_orders_by_client(self, client_id: int) -> list[JobOrder]:
        """Return job orders for one client ordered by newest creation timestamp first."""
        validated_client_id = self._validate_client_id(client_id)
        return list(
            self.session.query(JobOrder)
            .filter(JobOrder.client_id == validated_client_id)
            .order_by(JobOrder.created_at.desc())
            .all()
        )

    def list_job_orders_by_organization(self, organization_id: int) -> list[JobOrder]:
        """Return job orders for one organization ordered by newest creation timestamp first."""
        validated_organization_id = self._validate_organization_id(organization_id)
        return list(
            self.session.query(JobOrder)
            .filter(JobOrder.organization_id == validated_organization_id)
            .order_by(JobOrder.created_at.desc())
            .all()
        )

    def update_job_order(
        self,
        job_order_id: int,
        *,
        title: str | None = None,
        description: str | None = None,
        employment_type: str | None = None,
        pay_min: float | None = None,
        pay_max: float | None = None,
        currency: str | None = None,
        number_of_openings: int | None = None,
        positions_filled: int | None = None,
        work_location: str | None = None,
        remote_allowed: bool | None = None,
        travel_required: bool | None = None,
        date_opened: date | None = None,
        date_closed: date | None = None,
    ) -> JobOrder:
        """Update mutable job order fields while keeping job code immutable."""
        job_order = self.get_job_order(job_order_id)

        openings = number_of_openings if number_of_openings is not None else job_order.number_of_openings
        filled = positions_filled if positions_filled is not None else job_order.positions_filled
        self._validate_positions(openings, filled)

        if title is not None:
            job_order.title = self._validate_title(title)
        if description is not None:
            job_order.description = description.strip() if description.strip() else None
        if employment_type is not None:
            job_order.employment_type = employment_type.strip() if employment_type.strip() else None
        if pay_min is not None:
            job_order.pay_min = pay_min
        if pay_max is not None:
            job_order.pay_max = pay_max
        if currency is not None:
            job_order.currency = currency.strip() if currency.strip() else None
        if number_of_openings is not None:
            job_order.number_of_openings = number_of_openings
        if positions_filled is not None:
            job_order.positions_filled = positions_filled
        if work_location is not None:
            job_order.work_location = work_location.strip() if work_location.strip() else None
        if remote_allowed is not None:
            job_order.remote_allowed = remote_allowed
        if travel_required is not None:
            job_order.travel_required = travel_required
        if date_opened is not None:
            job_order.date_opened = date_opened
        if date_closed is not None:
            job_order.date_closed = date_closed

        job_order.updated_at = utc_now_naive()
        self.session.commit()
        self.session.refresh(job_order)
        return job_order

    def open_job_order(self, job_order_id: int) -> JobOrder:
        """Transition a job order from DRAFT to OPEN."""
        job_order = self.get_job_order(job_order_id)

        if job_order.status == JobOrderStatus.CLOSED:
            raise BlackcrestInputError("CLOSED job orders cannot be reopened")
        if job_order.status == JobOrderStatus.FILLED:
            raise BlackcrestInputError("FILLED job orders cannot transition to OPEN")
        if job_order.status != JobOrderStatus.DRAFT:
            raise BlackcrestInputError("Only DRAFT job orders may transition to OPEN")

        job_order.status = JobOrderStatus.OPEN
        if job_order.date_opened is None:
            job_order.date_opened = utc_now_naive().date()
        job_order.updated_at = utc_now_naive()
        self.session.commit()
        self.session.refresh(job_order)
        return job_order

    def hold_job_order(self, job_order_id: int) -> JobOrder:
        """Transition a job order from OPEN to ON_HOLD."""
        job_order = self.get_job_order(job_order_id)

        if job_order.status == JobOrderStatus.CLOSED:
            raise BlackcrestInputError("CLOSED job orders cannot transition to ON_HOLD")
        if job_order.status == JobOrderStatus.FILLED:
            raise BlackcrestInputError("FILLED job orders cannot transition to ON_HOLD")
        if job_order.status != JobOrderStatus.OPEN:
            raise BlackcrestInputError("Only OPEN job orders may transition to ON_HOLD")

        job_order.status = JobOrderStatus.ON_HOLD
        job_order.updated_at = utc_now_naive()
        self.session.commit()
        self.session.refresh(job_order)
        return job_order

    def close_job_order(self, job_order_id: int) -> JobOrder:
        """Transition a job order to CLOSED and set close date when missing."""
        job_order = self.get_job_order(job_order_id)

        if job_order.status == JobOrderStatus.CLOSED:
            raise BlackcrestInputError("Job order is already CLOSED")

        job_order.status = JobOrderStatus.CLOSED
        if job_order.date_closed is None:
            job_order.date_closed = utc_now_naive().date()
        job_order.updated_at = utc_now_naive()
        self.session.commit()
        self.session.refresh(job_order)
        return job_order

    def mark_job_order_filled(self, job_order_id: int) -> JobOrder:
        """Transition a job order to FILLED when opening counts are valid."""
        job_order = self.get_job_order(job_order_id)

        if job_order.status == JobOrderStatus.CLOSED:
            raise BlackcrestInputError("CLOSED job orders cannot transition to FILLED")

        openings = job_order.number_of_openings
        filled = job_order.positions_filled
        self._validate_positions(openings, filled)
        if openings is not None and openings > 0 and filled is None:
            job_order.positions_filled = openings

        self._validate_positions(job_order.number_of_openings, job_order.positions_filled)
        job_order.status = JobOrderStatus.FILLED
        if job_order.date_closed is None:
            job_order.date_closed = utc_now_naive().date()
        job_order.updated_at = utc_now_naive()
        self.session.commit()
        self.session.refresh(job_order)
        return job_order
