from __future__ import annotations

from datetime import datetime

import customtkinter as ctk

from app.app_state import AppState
from app.navigation import NavigationController
from controllers.applicant_workspace_controller import ApplicantWorkspaceController
from desktop.recruiting_dashboard import RecruitingDashboard
from views.applicant_workspace_view import ApplicantWorkspaceView
from views.clients_view import ClientsView
from views.dashboard_view import DashboardView
from views.job_orders_view import JobOrdersView
from views.reports_view import ReportsView
from views.settings_view import SettingsView


APP_VERSION = "v2.0-shell"


class RecruitOSMainWindow(ctk.CTk):
    """Desktop shell window for RecruitOS navigation and placeholder work areas."""

    NAV_ITEMS: list[tuple[str, str]] = [
        ("dashboard", "Dashboard"),
        ("applicants", "Applicants"),
        ("job_orders", "Job Orders"),
        ("clients", "Clients"),
        ("reports", "Reports"),
        ("settings", "Settings"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.app_state = AppState()
        self.title("Blackcrest RecruitOS")
        self.geometry("1400x860")
        self.minsize(1120, 700)
        self.configure(fg_color="#f8fafc")

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)

        self._time_after_id: str | None = None

        self._build_header()
        self._build_layout_body()
        self._build_status_bar()
        self._build_navigation()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_header(self) -> None:
        self.header_frame = ctk.CTkFrame(self, fg_color="#0f172a", corner_radius=0, height=64)
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.header_frame.grid_propagate(False)
        self.header_frame.grid_columnconfigure(0, weight=0)
        self.header_frame.grid_columnconfigure(1, weight=0)
        self.header_frame.grid_columnconfigure(2, weight=1)
        self.header_frame.grid_columnconfigure(3, weight=0)
        self.header_frame.grid_columnconfigure(4, weight=0)

        self.organization_selector = ctk.CTkOptionMenu(
            self.header_frame,
            values=["Greater Connections Staffing"],
            width=220,
        )
        self.organization_selector.grid(row=0, column=0, padx=(16, 8), pady=14, sticky="w")

        self.client_selector = ctk.CTkOptionMenu(
            self.header_frame,
            values=["USPS"],
            width=160,
        )
        self.client_selector.grid(row=0, column=1, padx=8, pady=14, sticky="w")

        self.global_search = ctk.CTkEntry(
            self.header_frame,
            placeholder_text="Global Search",
            width=340,
        )
        self.global_search.grid(row=0, column=2, padx=8, pady=14, sticky="w")

        self.notifications_button = ctk.CTkButton(
            self.header_frame,
            text="Notifications",
            width=130,
            fg_color="#1e293b",
            hover_color="#334155",
        )
        self.notifications_button.grid(row=0, column=3, padx=8, pady=14, sticky="e")

        self.current_user_label = ctk.CTkLabel(
            self.header_frame,
            text="Current User: Recruiter",
            text_color="#e2e8f0",
        )
        self.current_user_label.grid(row=0, column=4, padx=(8, 16), pady=14, sticky="e")

    def _build_layout_body(self) -> None:
        self.navigation_rail = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=0, width=220)
        self.navigation_rail.grid(row=1, column=0, sticky="nsew")
        self.navigation_rail.grid_propagate(False)
        self.navigation_rail.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.navigation_rail,
            text="RecruitOS",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#0f172a",
        ).grid(row=0, column=0, padx=18, pady=(20, 16), sticky="w")

        self.content_area = ctk.CTkFrame(self, fg_color="#f1f5f9", corner_radius=0)
        self.content_area.grid(row=1, column=1, sticky="nsew")
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(0, weight=1)

    def _build_navigation(self) -> None:
        self.navigation_controller = NavigationController(self.content_area)
        self.navigation_buttons: dict[str, ctk.CTkButton] = {}

        self.navigation_controller.register("dashboard", lambda parent: self._build_dashboard(parent))
        self.navigation_controller.register(
            "applicants",
            lambda parent: self._build_applicant_workspace(parent),
        )
        self.navigation_controller.register("job_orders", lambda parent: JobOrdersView(parent))
        self.navigation_controller.register("clients", lambda parent: ClientsView(parent))
        self.navigation_controller.register("reports", lambda parent: ReportsView(parent))
        self.navigation_controller.register("settings", lambda parent: SettingsView(parent))

        for idx, (key, label) in enumerate(self.NAV_ITEMS, start=1):
            button = ctk.CTkButton(
                self.navigation_rail,
                text=label,
                height=40,
                corner_radius=8,
                anchor="w",
                fg_color="#e2e8f0",
                hover_color="#cbd5e1",
                text_color="#0f172a",
                command=lambda selected=key: self.show_view(selected),
            )
            button.grid(row=idx, column=0, padx=14, pady=6, sticky="ew")
            self.navigation_buttons[key] = button

        self.show_view("dashboard")

    def _build_applicant_workspace(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        view = ApplicantWorkspaceView(parent)
        self.applicant_workspace_controller = ApplicantWorkspaceController(
            view=view,
            app_state=self.app_state,
        )
        return view

    def _build_dashboard(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        return RecruitingDashboard(
            parent,
            app_state=self.app_state,
            on_applicant_selected=lambda _: self.show_view("applicants"),
        )

    def _build_status_bar(self) -> None:
        self.status_bar = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=0, height=34)
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky="nsew")
        self.status_bar.grid_propagate(False)

        self.status_org_label = ctk.CTkLabel(self.status_bar, text="Organization: Greater Connections Staffing")
        self.status_org_label.pack(side="left", padx=(12, 10), pady=6)

        self.status_client_label = ctk.CTkLabel(self.status_bar, text="Client: USPS")
        self.status_client_label.pack(side="left", padx=10, pady=6)

        self.status_db_label = ctk.CTkLabel(self.status_bar, text="DB: Disconnected")
        self.status_db_label.pack(side="left", padx=10, pady=6)

        self.status_version_label = ctk.CTkLabel(self.status_bar, text=f"Version: {APP_VERSION}")
        self.status_version_label.pack(side="right", padx=(10, 12), pady=6)

        self.status_time_label = ctk.CTkLabel(self.status_bar, text="Time: --:--:--")
        self.status_time_label.pack(side="right", padx=10, pady=6)
        self._refresh_clock()

    def show_view(self, key: str) -> None:
        self.navigation_controller.show(key)

        for button_key, button in self.navigation_buttons.items():
            if button_key == key:
                button.configure(fg_color="#0ea5e9", text_color="#ffffff", hover_color="#0284c7")
            else:
                button.configure(fg_color="#e2e8f0", text_color="#0f172a", hover_color="#cbd5e1")

    def _refresh_clock(self) -> None:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status_time_label.configure(text=f"Time: {now}")
        self._time_after_id = self.after(1000, self._refresh_clock)

    def _on_close(self) -> None:
        if self._time_after_id:
            self.after_cancel(self._time_after_id)
            self._time_after_id = None
        self.destroy()


if __name__ == "__main__":
    app = RecruitOSMainWindow()
    app.mainloop()
