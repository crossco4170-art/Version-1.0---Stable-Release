from __future__ import annotations

import customtkinter as ctk


class ReportsView(ctk.CTkFrame):
    """Reports placeholder for future recruiter and hiring analytics views."""

    def __init__(self, master: ctk.CTkFrame) -> None:
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self,
            text="Reports",
            font=ctk.CTkFont(size=28, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=24, pady=(24, 8))

        ctk.CTkLabel(
            self,
            text="Reporting workspace for operational and hiring insights.",
            anchor="w",
            text_color="#475569",
        ).grid(row=1, column=0, sticky="w", padx=24)

        ctk.CTkLabel(
            self,
            text="Placeholder: Reports functionality will be implemented in future stories.",
            anchor="w",
            text_color="#0f766e",
        ).grid(row=2, column=0, sticky="w", padx=24, pady=(14, 0))
