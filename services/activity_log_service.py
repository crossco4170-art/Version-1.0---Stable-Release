from __future__ import annotations

from sqlalchemy.orm import Session

from models.activity_log import ActivityLog
from services.base_service import BaseCRUDService


class ActivityLogService(BaseCRUDService[ActivityLog]):
    """CRUD service for activity log records."""

    def __init__(self, session: Session | None = None, database_url: str | None = None) -> None:
        super().__init__(ActivityLog, session, database_url)
