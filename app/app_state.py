from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass


StateObserver = Callable[[str, object], None]


@dataclass(slots=True)
class _StateData:
    current_organization: str = "Greater Connections Staffing"
    current_client: str = "USPS"
    current_user: str = "Recruiter"
    selected_applicant: int | None = None
    selected_job_order: int | None = None
    notification_count: int = 0
    theme: str = "light"
    application_version: str = "v2.0-shell"


class AppState:
    """Centralized desktop application state container with change notifications."""

    def __init__(self) -> None:
        self._state = _StateData()
        self._observers: list[StateObserver] = []

    def add_observer(self, observer: StateObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: StateObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify(self, field_name: str, value: object) -> None:
        for observer in list(self._observers):
            observer(field_name, value)

    def get_current_organization(self) -> str:
        return self._state.current_organization

    def set_current_organization(self, value: str) -> None:
        self._state.current_organization = value
        self._notify("current_organization", value)

    def get_current_client(self) -> str:
        return self._state.current_client

    def set_current_client(self, value: str) -> None:
        self._state.current_client = value
        self._notify("current_client", value)

    def get_current_user(self) -> str:
        return self._state.current_user

    def set_current_user(self, value: str) -> None:
        self._state.current_user = value
        self._notify("current_user", value)

    def get_selected_applicant(self) -> int | None:
        return self._state.selected_applicant

    def set_selected_applicant(self, value: int | None) -> None:
        self._state.selected_applicant = value
        self._notify("selected_applicant", value)

    def get_selected_job_order(self) -> int | None:
        return self._state.selected_job_order

    def set_selected_job_order(self, value: int | None) -> None:
        self._state.selected_job_order = value
        self._notify("selected_job_order", value)

    def get_notification_count(self) -> int:
        return self._state.notification_count

    def set_notification_count(self, value: int) -> None:
        self._state.notification_count = value
        self._notify("notification_count", value)

    def increment_notification_count(self, amount: int = 1) -> None:
        self._state.notification_count += amount
        self._notify("notification_count", self._state.notification_count)

    def reset_notification_count(self) -> None:
        self._state.notification_count = 0
        self._notify("notification_count", 0)

    def get_theme(self) -> str:
        return self._state.theme

    def set_theme(self, value: str) -> None:
        self._state.theme = value
        self._notify("theme", value)

    def get_application_version(self) -> str:
        return self._state.application_version

    def set_application_version(self, value: str) -> None:
        self._state.application_version = value
        self._notify("application_version", value)
