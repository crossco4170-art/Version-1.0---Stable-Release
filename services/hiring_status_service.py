from __future__ import annotations

from sqlalchemy.orm import Session

from models.hiring_status import HiringStatus
from services.base_service import BaseCRUDService


class HiringStatusService(BaseCRUDService[HiringStatus]):
    """CRUD service for hiring status records."""

    def __init__(self, session: Session | None = None, database_url: str | None = None) -> None:
        super().__init__(HiringStatus, session, database_url)
