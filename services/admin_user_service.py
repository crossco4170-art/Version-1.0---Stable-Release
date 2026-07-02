from __future__ import annotations

from sqlalchemy.orm import Session

from models.admin_user import AdminUser
from services.base_service import BaseCRUDService


class AdminUserService(BaseCRUDService[AdminUser]):
    """CRUD service for admin user records."""

    def __init__(self, session: Session | None = None, database_url: str | None = None) -> None:
        super().__init__(AdminUser, session, database_url)

    def get_by_username(self, username: str) -> AdminUser | None:
        return self.session.query(self.model_cls).filter(self.model_cls.username == username).first()
