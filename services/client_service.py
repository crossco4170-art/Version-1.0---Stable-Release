from __future__ import annotations

from sqlalchemy.orm import Session

from models.client import Client
from services.base_service import BaseCRUDService


class ClientService(BaseCRUDService[Client]):
    """CRUD service for client records."""

    def __init__(self, session: Session | None = None, database_url: str | None = None) -> None:
        super().__init__(Client, session, database_url)
