from __future__ import annotations

from sqlalchemy.orm import Session

from models.job_order import JobOrder
from services.base_service import BaseCRUDService


class JobOrderService(BaseCRUDService[JobOrder]):
    """CRUD service for job order records."""

    def __init__(self, session: Session | None = None, database_url: str | None = None) -> None:
        super().__init__(JobOrder, session, database_url)
