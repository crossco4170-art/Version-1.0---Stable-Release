from __future__ import annotations

from sqlalchemy.orm import Session

from models.interview import Interview
from services.base_service import BaseCRUDService


class InterviewService(BaseCRUDService[Interview]):
    """CRUD service for interview records."""

    def __init__(self, session: Session | None = None, database_url: str | None = None) -> None:
        super().__init__(Interview, session, database_url)
