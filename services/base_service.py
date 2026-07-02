from __future__ import annotations

from typing import Any, Generic, TypeVar

from sqlalchemy.orm import Session

from database.connection import get_session

T = TypeVar("T")


class BaseCRUDService(Generic[T]):
    """Minimal CRUD helper for SQLAlchemy models."""

    def __init__(
        self,
        model_cls: type[T],
        session: Session | None = None,
        database_url: str | None = None,
    ) -> None:
        self.model_cls = model_cls
        self.session = session or get_session(database_url=database_url, ensure_schema=True)

    def create(self, **kwargs: Any) -> T:
        instance = self.model_cls(**kwargs)
        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)
        return instance

    def get_by_id(self, obj_id: int) -> T | None:
        return self.session.get(self.model_cls, obj_id)

    def list(self) -> list[T]:
        return list(self.session.query(self.model_cls).all())

    def update(self, obj_id: int, **kwargs: Any) -> T | None:
        instance = self.get_by_id(obj_id)
        if instance is None:
            return None

        for key, value in kwargs.items():
            setattr(instance, key, value)

        self.session.commit()
        self.session.refresh(instance)
        return instance

    def delete(self, obj_id: int) -> bool:
        instance = self.get_by_id(obj_id)
        if instance is None:
            return False

        self.session.delete(instance)
        self.session.commit()
        return True
