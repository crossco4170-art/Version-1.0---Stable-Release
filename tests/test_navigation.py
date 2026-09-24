from __future__ import annotations

import tkinter as tk

import pytest

customtkinter = pytest.importorskip("customtkinter")

from app.main_window import RecruitOSMainWindow
from desktop.recruiting_dashboard import RecruitingDashboard
from views.applicant_workspace_view import ApplicantWorkspaceView
from views.clients_view import ClientsView
from views.dashboard_view import DashboardView
from views.job_orders_view import JobOrdersView
from views.reports_view import ReportsView
from views.settings_view import SettingsView


@pytest.fixture
def window() -> RecruitOSMainWindow:
    try:
        app = RecruitOSMainWindow()
    except tk.TclError as exc:
        pytest.skip(f"GUI environment not available: {exc}")

    app.update_idletasks()
    yield app
    app._on_close()


def test_main_window_loads(window: RecruitOSMainWindow) -> None:
    assert window.winfo_exists() == 1


def test_navigation_initializes(window: RecruitOSMainWindow) -> None:
    keys = [item[0] for item in window.NAV_ITEMS]
    assert window.navigation_controller.keys() == keys


def test_every_navigation_item_loads_correct_placeholder(window: RecruitOSMainWindow) -> None:
    expected = {
        "dashboard": RecruitingDashboard,
        "applicants": ApplicantWorkspaceView,
        "job_orders": JobOrdersView,
        "clients": ClientsView,
        "reports": ReportsView,
        "settings": SettingsView,
    }

    for key, expected_class in expected.items():
        window.show_view(key)
        loaded = window.navigation_controller._instances[key]
        assert isinstance(loaded, expected_class)
        assert window.navigation_controller.current_view_key == key


def test_window_title_is_correct(window: RecruitOSMainWindow) -> None:
    assert window.title() == "Blackcrest RecruitOS"


def test_header_components_exist(window: RecruitOSMainWindow) -> None:
    assert window.organization_selector.winfo_exists() == 1
    assert window.client_selector.winfo_exists() == 1
    assert window.global_search.winfo_exists() == 1
    assert window.notifications_button.winfo_exists() == 1
    assert window.current_user_label.winfo_exists() == 1


def test_status_bar_components_exist(window: RecruitOSMainWindow) -> None:
    assert window.status_org_label.winfo_exists() == 1
    assert window.status_client_label.winfo_exists() == 1
    assert window.status_db_label.winfo_exists() == 1
    assert window.status_version_label.winfo_exists() == 1
    assert window.status_time_label.winfo_exists() == 1
