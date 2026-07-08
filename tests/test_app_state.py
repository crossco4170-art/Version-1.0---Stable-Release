from __future__ import annotations

from app.app_state import AppState


def test_default_state() -> None:
    state = AppState()

    assert state.get_current_organization() == "Greater Connections Staffing"
    assert state.get_current_client() == "USPS"
    assert state.get_current_user() == "Recruiter"
    assert state.get_selected_applicant() is None
    assert state.get_selected_job_order() is None
    assert state.get_notification_count() == 0
    assert state.get_theme() == "light"
    assert state.get_application_version() == "v2.0-shell"


def test_set_get_organization() -> None:
    state = AppState()
    state.set_current_organization("Next Horizon Staffing")

    assert state.get_current_organization() == "Next Horizon Staffing"


def test_set_get_client() -> None:
    state = AppState()
    state.set_current_client("Amazon")

    assert state.get_current_client() == "Amazon"


def test_set_get_user() -> None:
    state = AppState()
    state.set_current_user("Recruiting Lead")

    assert state.get_current_user() == "Recruiting Lead"


def test_set_get_applicant() -> None:
    state = AppState()
    state.set_selected_applicant(101)

    assert state.get_selected_applicant() == 101


def test_set_get_job_order() -> None:
    state = AppState()
    state.set_selected_job_order(205)

    assert state.get_selected_job_order() == 205


def test_notification_count_updates() -> None:
    state = AppState()

    state.set_notification_count(3)
    assert state.get_notification_count() == 3

    state.increment_notification_count()
    assert state.get_notification_count() == 4

    state.increment_notification_count(2)
    assert state.get_notification_count() == 6

    state.reset_notification_count()
    assert state.get_notification_count() == 0


def test_theme_updates() -> None:
    state = AppState()
    state.set_theme("dark")

    assert state.get_theme() == "dark"


def test_version_value() -> None:
    state = AppState()

    assert state.get_application_version() == "v2.0-shell"

    state.set_application_version("v2.1-shell")
    assert state.get_application_version() == "v2.1-shell"


def test_change_notification_support() -> None:
    state = AppState()
    observed: list[tuple[str, object]] = []

    def observer(field_name: str, value: object) -> None:
        observed.append((field_name, value))

    state.add_observer(observer)
    state.set_current_client("USPS West")
    state.set_notification_count(5)
    state.remove_observer(observer)
    state.set_theme("dark")

    assert observed == [
        ("current_client", "USPS West"),
        ("notification_count", 5),
    ]
