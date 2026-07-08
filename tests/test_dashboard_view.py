from __future__ import annotations

import tkinter as tk

import pytest

customtkinter = pytest.importorskip("customtkinter")

from views.dashboard_view import DashboardView


@pytest.fixture
def dashboard_view() -> DashboardView:
    try:
        root = customtkinter.CTk()
    except tk.TclError as exc:
        pytest.skip(f"GUI environment not available: {exc}")

    root.geometry("1200x800")
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)

    view = DashboardView(root)
    view.grid(row=0, column=0, sticky="nsew")
    root.update_idletasks()

    yield view

    root.destroy()


def test_dashboard_loads(dashboard_view: DashboardView) -> None:
    assert dashboard_view.winfo_exists() == 1


def test_three_column_layout_exists(dashboard_view: DashboardView) -> None:
    assert dashboard_view.left_column.winfo_exists() == 1
    assert dashboard_view.center_column.winfo_exists() == 1
    assert dashboard_view.right_column.winfo_exists() == 1


def test_header_exists(dashboard_view: DashboardView) -> None:
    assert dashboard_view.header_frame.winfo_exists() == 1
    assert dashboard_view.greeting_label.cget("text") == "Good Morning,"
    assert dashboard_view.current_recruiter_label.cget("text") == "Current Recruiter"
    assert len(dashboard_view.today_date_label.cget("text")) > 0


def test_widget_placeholders_exist(dashboard_view: DashboardView) -> None:
    assert dashboard_view.widget_todays_applicants.winfo_exists() == 1
    assert dashboard_view.widget_phone_screens.winfo_exists() == 1
    assert dashboard_view.widget_ready_for_submission.winfo_exists() == 1
    assert dashboard_view.widget_follow_ups_due.winfo_exists() == 1
    assert dashboard_view.widget_interviews_today.winfo_exists() == 1
    assert dashboard_view.widget_ai_priority_queue.winfo_exists() == 1
    assert dashboard_view.widget_recent_activity.winfo_exists() == 1


def test_dashboard_resizes(dashboard_view: DashboardView) -> None:
    root = dashboard_view.master
    original_width = dashboard_view.winfo_width()
    original_height = dashboard_view.winfo_height()

    root.geometry("1450x900")
    root.update_idletasks()

    assert dashboard_view.winfo_width() >= original_width
    assert dashboard_view.winfo_height() >= original_height
