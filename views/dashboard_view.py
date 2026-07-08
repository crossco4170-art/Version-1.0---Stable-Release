from __future__ import annotations

from datetime import datetime

import customtkinter as ctk


class DashboardView(ctk.CTkFrame):
    """Recruiter dashboard shell with deterministic placeholder widgets only."""

    def __init__(self, master: ctk.CTkFrame) -> None:
        super().__init__(master, fg_color="#f1f5f9")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_columns()

    def _build_header(self) -> None:
        self.header_frame = ctk.CTkFrame(
            self,
            fg_color="#ffffff",
            corner_radius=12,
            border_width=1,
            border_color="#e2e8f0",
        )
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 10))
        self.header_frame.grid_columnconfigure(0, weight=1)

        greeting_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        greeting_frame.grid(row=0, column=0, sticky="w", padx=16, pady=14)

        self.greeting_label = ctk.CTkLabel(
            greeting_frame,
            text="Good Morning,",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#0f172a",
        )
        self.greeting_label.grid(row=0, column=0, sticky="w")

        self.current_recruiter_label = ctk.CTkLabel(
            greeting_frame,
            text="Current Recruiter",
            font=ctk.CTkFont(size=16, weight="normal"),
            text_color="#334155",
        )
        self.current_recruiter_label.grid(row=1, column=0, sticky="w", pady=(4, 0))

        self.today_date_label = ctk.CTkLabel(
            self.header_frame,
            text=datetime.now().strftime("%A, %B %d, %Y"),
            font=ctk.CTkFont(size=14),
            text_color="#475569",
        )
        self.today_date_label.grid(row=0, column=1, sticky="e", padx=16, pady=16)

    def _build_columns(self) -> None:
        self.columns_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.columns_frame.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))
        self.columns_frame.grid_columnconfigure(0, weight=1)
        self.columns_frame.grid_columnconfigure(1, weight=2)
        self.columns_frame.grid_columnconfigure(2, weight=1)
        self.columns_frame.grid_rowconfigure(0, weight=1)

        self.left_column = ctk.CTkFrame(
            self.columns_frame,
            fg_color="#ffffff",
            corner_radius=12,
            border_width=1,
            border_color="#e2e8f0",
        )
        self.left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.left_column.grid_columnconfigure(0, weight=1)

        self.center_column = ctk.CTkFrame(
            self.columns_frame,
            fg_color="#ffffff",
            corner_radius=12,
            border_width=1,
            border_color="#e2e8f0",
        )
        self.center_column.grid(row=0, column=1, sticky="nsew", padx=8)
        self.center_column.grid_columnconfigure(0, weight=1)
        self.center_column.grid_rowconfigure(2, weight=1)

        self.right_column = ctk.CTkFrame(
            self.columns_frame,
            fg_color="#ffffff",
            corner_radius=12,
            border_width=1,
            border_color="#e2e8f0",
        )
        self.right_column.grid(row=0, column=2, sticky="nsew", padx=(8, 0))
        self.right_column.grid_columnconfigure(0, weight=1)

        self._build_left_column()
        self._build_center_column()
        self._build_right_column()

    def _build_section_title(self, parent: ctk.CTkFrame, text: str, row: int) -> None:
        ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#0f172a",
            anchor="w",
        ).grid(row=row, column=0, sticky="w", padx=14, pady=(14, 8))

    def _build_placeholder_card(self, parent: ctk.CTkFrame, text: str, row: int) -> ctk.CTkFrame:
        card = ctk.CTkFrame(parent, fg_color="#f8fafc", corner_radius=10, border_width=1, border_color="#e2e8f0")
        card.grid(row=row, column=0, sticky="ew", padx=14, pady=6)
        card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(card, text=text, anchor="w", text_color="#334155").grid(
            row=0, column=0, sticky="w", padx=10, pady=10
        )
        return card

    def _build_left_column(self) -> None:
        self._build_section_title(self.left_column, "Today's Work", 0)
        self.widget_todays_applicants = self._build_placeholder_card(self.left_column, "Today's Applicants: 24", 1)
        self.widget_phone_screens = self._build_placeholder_card(self.left_column, "Phone Screens: 8", 2)
        self.widget_follow_ups_due = self._build_placeholder_card(self.left_column, "Follow-ups Due: 11", 3)

        self._build_section_title(self.left_column, "Daily Tasks", 4)
        self.widget_interviews_today = self._build_placeholder_card(self.left_column, "Interviews Today: 5", 5)
        self.widget_recent_activity = self._build_placeholder_card(self.left_column, "Recent Activity: Placeholder", 6)

        self._build_section_title(self.left_column, "Quick Filters", 7)
        self._build_placeholder_card(self.left_column, "Filter: New Applicants", 8)
        self._build_placeholder_card(self.left_column, "Filter: Ready for Submission", 9)
        self._build_placeholder_card(self.left_column, "Filter: Follow-up Needed", 10)

    def _build_center_column(self) -> None:
        self._build_section_title(self.center_column, "Applicant Queue Placeholder", 0)
        self.widget_ready_for_submission = self._build_placeholder_card(
            self.center_column, "Ready for Submission: 6", 1
        )

        self.future_queue_grid = ctk.CTkFrame(
            self.center_column,
            fg_color="#f8fafc",
            corner_radius=10,
            border_width=1,
            border_color="#e2e8f0",
        )
        self.future_queue_grid.grid(row=2, column=0, sticky="nsew", padx=14, pady=(6, 14))
        self.future_queue_grid.grid_columnconfigure(0, weight=1)
        self.future_queue_grid.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self.future_queue_grid,
            text="Future Queue Grid",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#0f172a",
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=12, pady=(12, 6))

        ctk.CTkLabel(
            self.future_queue_grid,
            text="Placeholder: applicant grid rows, sorting, and filters will be implemented in later stories.",
            text_color="#475569",
            anchor="w",
            justify="left",
            wraplength=520,
        ).grid(row=1, column=0, sticky="nw", padx=12, pady=(0, 12))

    def _build_right_column(self) -> None:
        self._build_section_title(self.right_column, "AI Intelligence Placeholder", 0)
        self.widget_ai_priority_queue = self._build_placeholder_card(self.right_column, "AI Priority Queue: 4", 1)
        self.widget_match_score = self._build_placeholder_card(self.right_column, "Match Score: Placeholder", 2)
        self.widget_recommendation = self._build_placeholder_card(self.right_column, "Recommendation: Placeholder", 3)
        self.widget_confidence = self._build_placeholder_card(self.right_column, "Confidence: Placeholder", 4)

        self._build_section_title(self.right_column, "Notifications Placeholder", 5)
        self._build_placeholder_card(self.right_column, "Notification Feed: Placeholder", 6)

        ctk.CTkLabel(
            self,
            text="Dashboard",
            font=ctk.CTkFont(size=28, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=24, pady=(24, 8))

        ctk.CTkLabel(
            self,
            text="Recruiter dashboard workspace for queue metrics and operational visibility.",
            anchor="w",
            text_color="#475569",
        ).grid(row=1, column=0, sticky="w", padx=24)

        ctk.CTkLabel(
            self,
            text="Placeholder: Dashboard widgets will be implemented in future stories.",
            anchor="w",
            text_color="#0f766e",
        ).grid(row=2, column=0, sticky="w", padx=24, pady=(14, 0))
