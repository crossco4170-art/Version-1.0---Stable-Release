from __future__ import annotations

import tkinter as tk
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from statistics import mean
from tkinter import filedialog, messagebox, ttk

import customtkinter as ctk

from config.settings import get_settings
from models.applicant import Applicant
from services.applicant_service import ApplicantService
from services.reporting_service import ReportingService


STATUS_ORDER = ["applied", "screened", "interview", "offer", "hired", "rejected"]

DEFAULT_PIPELINE_STAGE_COLORS = {
    "new": "#94a3b8",
    "applied": "#94a3b8",
    "screening": "#0ea5e9",
    "screened": "#0ea5e9",
    "interview": "#f59e0b",
    "offer": "#a855f7",
    "hired": "#16a34a",
    "rejected": "#dc2626",
    "other": "#64748b",
}


@dataclass
class DashboardFilters:
    query: str = ""
    status: str = "All"
    min_score: float = 0.0


class RecruitingDashboard(ctk.CTk):
    """CustomTkinter dashboard for applicant search, filtering, and hiring insights."""

    def __init__(
        self,
        database_url: str | None = None,
        pipeline_stage_colors: dict[str, str] | None = None,
    ) -> None:
        super().__init__()
        self.title("Blackcrest Recruiting AI Dashboard")
        self.geometry("1420x860")
        self.minsize(1200, 760)

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.settings = get_settings(validate_required=False)
        self.applicant_service = ApplicantService(database_url=database_url or self.settings.database_url)
        self.reporting_service = ReportingService(database_url=database_url or self.settings.database_url)
        self.score_threshold = self.settings.score_notification_threshold
        self.pipeline_stage_colors = dict(DEFAULT_PIPELINE_STAGE_COLORS)
        if pipeline_stage_colors:
            self.pipeline_stage_colors.update({key.lower(): value for key, value in pipeline_stage_colors.items()})

        self.sort_column = "date_added"
        self.sort_descending = True

        self.applicants: list[Applicant] = []
        self.filtered_applicants: list[Applicant] = []

        self.filters = DashboardFilters()
        self._setup_styles()
        self._build_layout()
        self._load_data()

    def _setup_styles(self) -> None:
        self.configure(fg_color="#f1f5f9")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Dashboard.Treeview",
            background="#ffffff",
            foreground="#0f172a",
            fieldbackground="#ffffff",
            rowheight=32,
            bordercolor="#d1d5db",
            borderwidth=1,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Dashboard.Treeview.Heading",
            background="#0f172a",
            foreground="#ffffff",
            font=("Segoe UI Semibold", 10),
            relief="flat",
        )
        style.map(
            "Dashboard.Treeview",
            background=[("selected", "#dbeafe")],
            foreground=[("selected", "#0f172a")],
        )

    def _build_layout(self) -> None:
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=3)
        self.grid_columnconfigure(2, weight=2)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_filter_panel()
        self._build_search_panel()
        self._build_side_panel()

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, corner_radius=0, fg_color="#0f172a", height=72)
        header.grid(row=0, column=0, columnspan=3, sticky="nsew")
        header.grid_propagate(False)

        title = ctk.CTkLabel(
            header,
            text="Blackcrest Recruiting Dashboard",
            text_color="#f8fafc",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
        )
        title.grid(row=0, column=0, padx=26, pady=16, sticky="w")

        subtitle = ctk.CTkLabel(
            header,
            text="Search applicants, monitor pipeline health, and review candidate details in one workspace.",
            text_color="#cbd5e1",
            font=ctk.CTkFont(family="Segoe UI", size=13),
        )
        subtitle.grid(row=1, column=0, padx=26, pady=(0, 14), sticky="w")

    def _build_filter_panel(self) -> None:
        panel = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=12, border_width=1, border_color="#e2e8f0")
        panel.grid(row=1, column=0, padx=(18, 10), pady=18, sticky="nsew")
        panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            panel,
            text="Filters",
            text_color="#0f172a",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
        ).grid(row=0, column=0, padx=16, pady=(16, 8), sticky="w")

        ctk.CTkLabel(panel, text="Search", text_color="#334155").grid(row=1, column=0, padx=16, pady=(8, 4), sticky="w")
        self.search_var = tk.StringVar()
        search_entry = ctk.CTkEntry(panel, textvariable=self.search_var, placeholder_text="Name, email, phone, status")
        search_entry.grid(row=2, column=0, padx=16, pady=(0, 12), sticky="ew")
        search_entry.bind("<KeyRelease>", lambda _: self._apply_filters())

        ctk.CTkLabel(panel, text="Status", text_color="#334155").grid(row=3, column=0, padx=16, pady=(4, 4), sticky="w")
        self.status_var = tk.StringVar(value="All")
        self.status_menu = ctk.CTkOptionMenu(
            panel,
            variable=self.status_var,
            values=["All", "Applied", "Screened", "Interview", "Offer", "Hired", "Rejected", "Other"],
            command=lambda _: self._apply_filters(),
        )
        self.status_menu.grid(row=4, column=0, padx=16, pady=(0, 12), sticky="ew")

        ctk.CTkLabel(panel, text="Minimum Score", text_color="#334155").grid(row=5, column=0, padx=16, pady=(4, 4), sticky="w")
        self.min_score_var = tk.DoubleVar(value=0.0)
        self.min_score_label = ctk.CTkLabel(panel, text="0", text_color="#0f172a")
        self.min_score_label.grid(row=6, column=0, padx=16, pady=(0, 2), sticky="e")

        score_slider = ctk.CTkSlider(
            panel,
            variable=self.min_score_var,
            from_=0,
            to=100,
            number_of_steps=100,
            command=self._on_slider_change,
        )
        score_slider.grid(row=7, column=0, padx=16, pady=(0, 14), sticky="ew")

        ctk.CTkButton(panel, text="Reset Filters", command=self._reset_filters).grid(
            row=8, column=0, padx=16, pady=(0, 8), sticky="ew"
        )
        ctk.CTkButton(panel, text="Refresh Data", fg_color="#0f766e", hover_color="#115e59", command=self._load_data).grid(
            row=9, column=0, padx=16, pady=(0, 16), sticky="ew"
        )

    def _build_search_panel(self) -> None:
        panel = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=12, border_width=1, border_color="#e2e8f0")
        panel.grid(row=1, column=1, padx=10, pady=18, sticky="nsew")
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            panel,
            text="Applicant Search",
            text_color="#0f172a",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
        ).grid(row=0, column=0, padx=16, pady=(14, 10), sticky="w")

        columns = ("id", "name", "status", "score", "date_added", "email", "phone")
        self.tree = ttk.Treeview(panel, columns=columns, show="headings", style="Dashboard.Treeview")
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Name", command=lambda: self._set_sort("name"))
        self.tree.heading("status", text="Status", command=lambda: self._set_sort("status"))
        self.tree.heading("score", text="Score", command=lambda: self._set_sort("score"))
        self.tree.heading("date_added", text="Date Added", command=lambda: self._set_sort("date_added"))
        self.tree.heading("email", text="Email")
        self.tree.heading("phone", text="Phone")

        self.tree.column("id", width=55, anchor="center")
        self.tree.column("name", width=170)
        self.tree.column("status", width=120, anchor="center")
        self.tree.column("score", width=75, anchor="center")
        self.tree.column("date_added", width=130, anchor="center")
        self.tree.column("email", width=210)
        self.tree.column("phone", width=120)

        scroll_y = ttk.Scrollbar(panel, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)

        self.tree.grid(row=1, column=0, padx=(16, 0), pady=(0, 16), sticky="nsew")
        scroll_y.grid(row=1, column=1, padx=(0, 16), pady=(0, 16), sticky="ns")

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

    def _build_side_panel(self) -> None:
        panel = ctk.CTkScrollableFrame(self, fg_color="#ffffff", corner_radius=12, border_width=1, border_color="#e2e8f0")
        panel.grid(row=1, column=2, padx=(10, 18), pady=18, sticky="nsew")
        panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            panel,
            text="Applicant Details",
            text_color="#0f172a",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
        ).grid(row=0, column=0, padx=14, pady=(14, 8), sticky="w")

        self.details_box = ctk.CTkTextbox(panel, height=230, fg_color="#f8fafc", border_width=1, border_color="#e2e8f0")
        self.details_box.grid(row=1, column=0, padx=14, pady=(0, 16), sticky="ew")
        self.details_box.insert("1.0", "Select an applicant to view details.")
        self.details_box.configure(state="disabled")

        ctk.CTkLabel(
            panel,
            text="Hiring Pipeline",
            text_color="#0f172a",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
        ).grid(row=2, column=0, padx=14, pady=(0, 8), sticky="w")

        self.pipeline_frame = ctk.CTkFrame(panel, fg_color="#f8fafc", border_width=1, border_color="#e2e8f0")
        self.pipeline_frame.grid(row=3, column=0, padx=14, pady=(0, 16), sticky="ew")
        self.pipeline_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            panel,
            text="Statistics",
            text_color="#0f172a",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
        ).grid(row=4, column=0, padx=14, pady=(0, 8), sticky="w")

        self.stats_frame = ctk.CTkFrame(panel, fg_color="#f8fafc", border_width=1, border_color="#e2e8f0")
        self.stats_frame.grid(row=5, column=0, padx=14, pady=(0, 16), sticky="ew")
        self.stats_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            panel,
            text="Reports",
            text_color="#0f172a",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
        ).grid(row=6, column=0, padx=14, pady=(0, 8), sticky="w")

        reports_frame = ctk.CTkFrame(panel, fg_color="#f8fafc", border_width=1, border_color="#e2e8f0")
        reports_frame.grid(row=7, column=0, padx=14, pady=(0, 16), sticky="ew")
        reports_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(
            reports_frame,
            text="Daily Report",
            command=lambda: self._generate_report_from_ui("daily"),
        ).grid(row=0, column=0, padx=10, pady=(10, 6), sticky="ew")

        ctk.CTkButton(
            reports_frame,
            text="Weekly Report",
            command=lambda: self._generate_report_from_ui("weekly"),
        ).grid(row=1, column=0, padx=10, pady=6, sticky="ew")

        ctk.CTkButton(
            reports_frame,
            text="Monthly Report",
            command=lambda: self._generate_report_from_ui("monthly"),
        ).grid(row=2, column=0, padx=10, pady=6, sticky="ew")

        ctk.CTkButton(
            reports_frame,
            text="Pipeline Report",
            command=lambda: self._generate_report_from_ui("pipeline"),
        ).grid(row=3, column=0, padx=10, pady=(6, 10), sticky="ew")

    def _on_slider_change(self, value: float) -> None:
        self.min_score_label.configure(text=f"{value:.0f}")
        self._apply_filters()

    def _reset_filters(self) -> None:
        self.search_var.set("")
        self.status_var.set("All")
        self.min_score_var.set(0)
        self.min_score_label.configure(text="0")
        self._apply_filters()

    def _load_data(self) -> None:
        try:
            self.applicants = self.applicant_service.list_applicants()
            self._apply_filters()
        except Exception as exc:
            messagebox.showerror("Data Error", f"Unable to load applicants: {exc}")

    def _apply_filters(self) -> None:
        query = self.search_var.get().strip().lower()
        status = self.status_var.get().strip().lower()
        min_score = float(self.min_score_var.get())

        self.filters = DashboardFilters(query=query, status=status, min_score=min_score)

        results: list[Applicant] = []
        for applicant in self.applicants:
            if not self._matches_query(applicant, query):
                continue
            if not self._matches_status(applicant, status):
                continue
            score_value = applicant.score if applicant.score is not None else 0.0
            if score_value < min_score:
                continue
            results.append(applicant)

        self.filtered_applicants = self._sorted_results(results)
        self._render_tree()
        self._render_pipeline()
        self._render_stats()

    def _set_sort(self, column: str) -> None:
        if self.sort_column == column:
            self.sort_descending = not self.sort_descending
        else:
            self.sort_column = column
            self.sort_descending = False
        self.filtered_applicants = self._sorted_results(self.filtered_applicants)
        self._render_tree()

    def _sorted_results(self, applicants: list[Applicant]) -> list[Applicant]:
        if not applicants:
            return []

        key_func = self._sort_key_for_column(self.sort_column)
        return sorted(applicants, key=key_func, reverse=self.sort_descending)

    def _sort_key_for_column(self, column: str):
        if column == "name":
            return lambda item: (item.name or "").lower()
        if column == "score":
            return lambda item: item.score if item.score is not None else -1.0
        if column == "status":
            return lambda item: (item.current_status or "").lower()
        if column == "date_added":
            return lambda item: item.date_added or datetime.min
        return lambda item: item.id

    def _matches_query(self, applicant: Applicant, query: str) -> bool:
        if not query:
            return True
        searchable = " ".join(
            [
                str(applicant.id),
                applicant.name or "",
                applicant.email or "",
                applicant.phone or "",
                applicant.current_status or "",
                applicant.notes or "",
            ]
        ).lower()
        return query in searchable

    def _matches_status(self, applicant: Applicant, selected_status: str) -> bool:
        if selected_status in {"", "all"}:
            return True
        normalized = (applicant.current_status or "other").strip().lower()
        if selected_status == "other":
            return normalized not in STATUS_ORDER
        return normalized == selected_status

    def _render_tree(self) -> None:
        for row in self.tree.get_children():
            self.tree.delete(row)

        for applicant in self.filtered_applicants:
            score_text = "-" if applicant.score is None else f"{applicant.score:.1f}"
            date_text = applicant.date_added.strftime("%Y-%m-%d") if applicant.date_added else "N/A"
            self.tree.insert(
                "",
                "end",
                iid=str(applicant.id),
                values=(
                    applicant.id,
                    applicant.name,
                    (applicant.current_status or "N/A").title(),
                    score_text,
                    date_text,
                    applicant.email or "N/A",
                    applicant.phone or "N/A",
                ),
            )

    def _on_tree_select(self, _: tk.Event) -> None:
        selected = self.tree.selection()
        if not selected:
            return
        applicant_id = int(selected[0])
        applicant = next((item for item in self.filtered_applicants if item.id == applicant_id), None)
        if applicant is None:
            return

        details = [
            f"Applicant ID: {applicant.id}",
            f"Name: {applicant.name}",
            f"Email: {applicant.email or 'Not provided'}",
            f"Phone: {applicant.phone or 'Not provided'}",
            f"Address: {applicant.address or 'Not provided'}",
            f"Status: {(applicant.current_status or 'N/A').title()}",
            f"Score: {applicant.score if applicant.score is not None else 'N/A'}",
            f"Experience: {applicant.experience or 'Not provided'}",
            "",
            "Notes:",
            applicant.notes or "No notes on file.",
        ]

        self.details_box.configure(state="normal")
        self.details_box.delete("1.0", "end")
        self.details_box.insert("1.0", "\n".join(details))
        self.details_box.configure(state="disabled")

    def _render_pipeline(self) -> None:
        for child in self.pipeline_frame.winfo_children():
            child.destroy()

        counts = Counter((item.current_status or "other").strip().lower() for item in self.filtered_applicants)
        total = max(len(self.filtered_applicants), 1)

        row = 0
        for status in STATUS_ORDER + ["other"]:
            count = counts.get(status, 0)
            ratio = count / total
            label = status.title() if status != "other" else "Other"
            color = self._color_for_stage(status)

            row_frame = ctk.CTkFrame(self.pipeline_frame, fg_color="transparent")
            row_frame.grid(row=row, column=0, padx=12, pady=(10 if row == 0 else 6, 2), sticky="ew")
            row_frame.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                row_frame,
                text="●",
                text_color=color,
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            ).grid(row=0, column=0, padx=(0, 6), sticky="w")

            ctk.CTkLabel(
                row_frame,
                text=f"{label}: {count}",
                text_color="#1e293b",
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            ).grid(row=0, column=1, sticky="w")

            progress = ctk.CTkProgressBar(self.pipeline_frame, height=10, progress_color=color)
            progress.grid(row=row + 1, column=0, padx=12, pady=(0, 2), sticky="ew")
            progress.set(ratio)

            row += 2

    def _color_for_stage(self, status: str) -> str:
        normalized = (status or "other").strip().lower()
        if normalized in self.pipeline_stage_colors:
            return self.pipeline_stage_colors[normalized]
        if normalized == "applied":
            return self.pipeline_stage_colors.get("new", DEFAULT_PIPELINE_STAGE_COLORS["new"])
        if normalized == "screened":
            return self.pipeline_stage_colors.get("screening", DEFAULT_PIPELINE_STAGE_COLORS["screening"])
        return self.pipeline_stage_colors.get("other", DEFAULT_PIPELINE_STAGE_COLORS["other"])

    def _render_stats(self) -> None:
        for child in self.stats_frame.winfo_children():
            child.destroy()

        scores = [item.score for item in self.filtered_applicants if item.score is not None]
        total = len(self.filtered_applicants)
        avg_score = mean(scores) if scores else 0.0
        top_candidates = len([value for value in scores if value >= self.score_threshold])

        cards = [
            ("Total Applicants", str(total), "#0f172a"),
            ("Average Score", f"{avg_score:.1f}", "#1d4ed8"),
            ("Above Threshold", str(top_candidates), "#0f766e"),
            ("Threshold", f"{self.score_threshold:.1f}", "#7c3aed"),
        ]

        for idx, (title, value, accent) in enumerate(cards):
            card = ctk.CTkFrame(self.stats_frame, fg_color="#ffffff", border_width=1, border_color="#e2e8f0")
            card.grid(row=idx, column=0, padx=12, pady=(10 if idx == 0 else 6, 0), sticky="ew")
            card.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                card,
                text=title,
                text_color="#64748b",
                font=ctk.CTkFont(family="Segoe UI", size=11),
            ).grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")

            ctk.CTkLabel(
                card,
                text=value,
                text_color=accent,
                font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            ).grid(row=1, column=0, padx=10, pady=(0, 10), sticky="w")

    def _generate_report_from_ui(self, report_type: str) -> None:
        try:
            report = self._generate_report_data(report_type)
            save_path = self._choose_export_path(report_type)
            if not save_path:
                return

            exported = self._export_report(report, save_path)
            messagebox.showinfo("Report Generated", f"Report saved successfully:\n{exported}")
        except Exception as exc:
            messagebox.showerror("Report Error", f"Failed to generate report: {exc}")

    def _generate_report_data(self, report_type: str) -> dict[str, object]:
        if report_type == "daily":
            return self.reporting_service.generate_daily_report()
        if report_type == "weekly":
            return self.reporting_service.generate_weekly_report()
        if report_type == "monthly":
            return self.reporting_service.generate_monthly_report()
        if report_type == "pipeline":
            return self.reporting_service.generate_applicant_pipeline_report()
        raise ValueError(f"Unsupported report type: {report_type}")

    def _choose_export_path(self, report_type: str) -> str:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"{report_type}_report_{stamp}.csv"
        return filedialog.asksaveasfilename(
            title="Save Report",
            defaultextension=".csv",
            initialfile=default_name,
            filetypes=[
                ("CSV", "*.csv"),
                ("Excel Workbook", "*.xlsx"),
                ("PDF", "*.pdf"),
            ],
        )

    def _export_report(self, report: dict[str, object], output_path: str) -> Path:
        destination = Path(output_path)
        suffix = destination.suffix.lower()
        if suffix == ".csv":
            return self.reporting_service.export_report_to_csv(report, destination)
        if suffix == ".xlsx":
            return self.reporting_service.export_report_to_excel(report, destination)
        if suffix == ".pdf":
            return self.reporting_service.export_report_to_pdf(report, destination)
        raise ValueError("Unsupported export format. Choose .csv, .xlsx, or .pdf")


def run_dashboard(
    database_url: str | None = None,
    pipeline_stage_colors: dict[str, str] | None = None,
) -> None:
    app = RecruitingDashboard(database_url=database_url, pipeline_stage_colors=pipeline_stage_colors)
    app.mainloop()


if __name__ == "__main__":
    run_dashboard()
