from __future__ import annotations

import tkinter as tk
import customtkinter as ctk


def _s(codes: list[int]) -> str:
    return "".join(chr(i) for i in codes)


OVERVIEW = _s([79, 118, 101, 114, 118, 105, 101, 119])
RESUME = _s([82, 101, 115, 117, 109, 101])
AI_REVIEW = _s([65, 73, 32, 82, 101, 118, 105, 101, 119])
DOCUMENTS = _s([68, 111, 99, 117, 109, 101, 110, 116, 115])
HISTORY = _s([72, 105, 115, 116, 111, 114, 121])


class ApplicantWorkspaceView(ctk.CTkFrame):
    """Applicant Workspace shell with placeholder-only layout sections."""

    def __init__(self, master: ctk.CTkFrame) -> None:
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main_container = ctk.CTkFrame(self)
        self.main_container.grid(row=0, column=0, sticky=tk.NSEW, padx=16, pady=16)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(1, weight=2)
        self.main_container.grid_columnconfigure(2, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        self.left_panel = ctk.CTkFrame(self.main_container)
        self.left_panel.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 8))
        self.left_panel.grid_columnconfigure(0, weight=1)

        self.center_panel = ctk.CTkFrame(self.main_container)
        self.center_panel.grid(row=0, column=1, sticky=tk.NSEW, padx=8)
        self.center_panel.grid_columnconfigure(0, weight=1)
        self.center_panel.grid_rowconfigure(1, weight=1)

        self.right_panel = ctk.CTkFrame(self.main_container)
        self.right_panel.grid(row=0, column=2, sticky=tk.NSEW, padx=(8, 0))
        self.right_panel.grid_columnconfigure(0, weight=1)

        self._build_left_panel()
        self._build_center_panel()
        self._build_right_panel()

    def _build_left_panel(self) -> None:
        ctk.CTkLabel(self.left_panel, text="Applicant Timeline", anchor=tk.W).grid(
            row=0, column=0, sticky=tk.W, padx=12, pady=(12, 6)
        )
        self.timeline_placeholder = ctk.CTkFrame(self.left_panel)
        self.timeline_placeholder.grid(row=1, column=0, sticky=tk.EW, padx=12, pady=6)
        self.timeline_label = ctk.CTkLabel(self.timeline_placeholder, text="No timeline events.", anchor=tk.W, justify=tk.LEFT)
        self.timeline_label.grid(row=0, column=0, sticky=tk.W, padx=8, pady=8)

        ctk.CTkLabel(self.left_panel, text="Recruiter Tasks", anchor=tk.W).grid(
            row=2, column=0, sticky=tk.W, padx=12, pady=(12, 6)
        )
        self.tasks_placeholder = ctk.CTkFrame(self.left_panel)
        self.tasks_placeholder.grid(row=3, column=0, sticky=tk.EW, padx=12, pady=6)
        self.tasks_label = ctk.CTkLabel(self.tasks_placeholder, text="No tasks.", anchor=tk.W, justify=tk.LEFT)
        self.tasks_label.grid(row=0, column=0, sticky=tk.W, padx=8, pady=8)

        ctk.CTkLabel(self.left_panel, text="Documents", anchor=tk.W).grid(
            row=4, column=0, sticky=tk.W, padx=12, pady=(12, 6)
        )
        self.communication_placeholder = ctk.CTkFrame(self.left_panel)
        self.communication_placeholder.grid(row=5, column=0, sticky=tk.EW, padx=12, pady=6)
        self.documents_label = ctk.CTkLabel(self.communication_placeholder, text="No documents.", anchor=tk.W, justify=tk.LEFT)
        self.documents_label.grid(row=0, column=0, sticky=tk.W, padx=8, pady=8)

    def _build_center_panel(self) -> None:
        self.header_frame = ctk.CTkFrame(self.center_panel)
        self.header_frame.grid(row=0, column=0, sticky=tk.EW, padx=12, pady=(12, 8))
        self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_frame.grid_columnconfigure(1, weight=1)
        self.header_frame.grid_columnconfigure(2, weight=1)
        self.header_frame.grid_columnconfigure(3, weight=1)

        self.applicant_name_label = ctk.CTkLabel(self.header_frame, anchor=tk.W)
        self.applicant_name_label.grid(row=0, column=0, sticky=tk.W, padx=8, pady=(8, 4))
        self.pipeline_stage_label = ctk.CTkLabel(self.header_frame, anchor=tk.W)
        self.pipeline_stage_label.grid(row=0, column=1, sticky=tk.W, padx=8, pady=(8, 4))
        self.assigned_recruiter_label = ctk.CTkLabel(self.header_frame, anchor=tk.W)
        self.assigned_recruiter_label.grid(row=0, column=2, sticky=tk.W, padx=8, pady=(8, 4))
        self.job_order_label = ctk.CTkLabel(self.header_frame, anchor=tk.W)
        self.job_order_label.grid(row=0, column=3, sticky=tk.W, padx=8, pady=(8, 4))

        self.client_label = ctk.CTkLabel(self.header_frame, anchor=tk.W)
        self.client_label.grid(row=1, column=0, sticky=tk.W, padx=8, pady=(0, 8))
        self.location_label = ctk.CTkLabel(self.header_frame, anchor=tk.W)
        self.location_label.grid(row=1, column=1, sticky=tk.W, padx=8, pady=(0, 8))
        self.applied_date_label = ctk.CTkLabel(self.header_frame, anchor=tk.W)
        self.applied_date_label.grid(row=1, column=2, sticky=tk.W, padx=8, pady=(0, 8))

        self.workspace_tabs = ctk.CTkTabview(self.center_panel)
        self.workspace_tabs.grid(row=1, column=0, sticky=tk.NSEW, padx=12, pady=(8, 12))
        self.tab_overview = self.workspace_tabs.add(OVERVIEW)
        self.tab_resume = self.workspace_tabs.add(RESUME)
        self.tab_ai_review = self.workspace_tabs.add(AI_REVIEW)
        self.tab_documents = self.workspace_tabs.add(DOCUMENTS)
        self.tab_history = self.workspace_tabs.add(HISTORY)

        self.overview_content_label = ctk.CTkLabel(self.tab_overview, text="Overview placeholder", anchor=tk.NW, justify=tk.LEFT)
        self.overview_content_label.grid(row=0, column=0, sticky=tk.NW, padx=12, pady=12)

        self.resume_metadata_label = ctk.CTkLabel(self.tab_resume, text="Resume metadata placeholder", anchor=tk.NW, justify=tk.LEFT)
        self.resume_metadata_label.grid(row=0, column=0, sticky=tk.NW, padx=12, pady=12)

        self.history_content_label = ctk.CTkLabel(self.tab_history, text="History placeholder", anchor=tk.NW, justify=tk.LEFT)
        self.history_content_label.grid(row=0, column=0, sticky=tk.NW, padx=12, pady=12)

        self.clear_workspace()

    def _build_right_panel(self) -> None:
        ctk.CTkLabel(self.right_panel, text="AI Panel Placeholder", anchor=tk.W).grid(
            row=0, column=0, sticky=tk.W, padx=12, pady=(12, 6)
        )
        self.ai_recommendation_placeholder = ctk.CTkFrame(self.right_panel)
        self.ai_recommendation_placeholder.grid(row=1, column=0, sticky=tk.EW, padx=12, pady=6)
        self.match_percentage_placeholder = ctk.CTkFrame(self.right_panel)
        self.match_percentage_placeholder.grid(row=2, column=0, sticky=tk.EW, padx=12, pady=6)
        self.confidence_placeholder = ctk.CTkFrame(self.right_panel)
        self.confidence_placeholder.grid(row=3, column=0, sticky=tk.EW, padx=12, pady=6)

        ctk.CTkLabel(self.right_panel, text="Pipeline Controls Placeholder", anchor=tk.W).grid(
            row=4, column=0, sticky=tk.W, padx=12, pady=(12, 6)
        )
        self.pipeline_controls_placeholder = ctk.CTkFrame(self.right_panel)
        self.pipeline_controls_placeholder.grid(row=5, column=0, sticky=tk.EW, padx=12, pady=6)

        ctk.CTkLabel(self.right_panel, text="Quick Actions Placeholder", anchor=tk.W).grid(
            row=6, column=0, sticky=tk.W, padx=12, pady=(12, 6)
        )
        self.quick_actions_placeholder = ctk.CTkFrame(self.right_panel)
        self.quick_actions_placeholder.grid(row=7, column=0, sticky=tk.EW, padx=12, pady=6)

    def set_applicant_header(self, payload: dict[str, object]) -> None:
        self.applicant_name_label.configure(text=f"Applicant Name: {payload.get('applicant_name', 'Placeholder')}")
        self.pipeline_stage_label.configure(text=f"Pipeline Stage: {payload.get('pipeline_stage', 'Placeholder')}")
        self.assigned_recruiter_label.configure(text=f"Assigned Recruiter: {payload.get('assigned_recruiter', 'Placeholder')}")
        self.job_order_label.configure(text=f"Job Order: {payload.get('job_order', 'Placeholder')}")
        self.client_label.configure(text=f"Client: {payload.get('client', 'Placeholder')}")
        self.location_label.configure(text=f"Location: {payload.get('location', 'Placeholder')}")
        self.applied_date_label.configure(text=f"Applied Date: {payload.get('applied_date', 'Placeholder')}")

    def clear_header(self) -> None:
        self.set_applicant_header(
            {
                "applicant_name": "Placeholder",
                "pipeline_stage": "Placeholder",
                "assigned_recruiter": "Placeholder",
                "job_order": "Placeholder",
                "client": "Placeholder",
                "location": "Placeholder",
                "applied_date": "Placeholder",
            }
        )

    def update_overview(self, overview: dict[str, object]) -> None:
        if not overview:
            self.overview_content_label.configure(text="Overview placeholder")
            return

        lines = [
            f"Name: {overview.get('name', 'Placeholder')}",
            f"Email: {overview.get('email', 'Placeholder')}",
            f"Phone: {overview.get('phone', 'Placeholder')}",
            f"Location: {overview.get('location', 'Placeholder')}",
            f"Job Order: {overview.get('job_order', 'Placeholder')}",
            f"Client: {overview.get('client', 'Placeholder')}",
            f"Pipeline Stage: {overview.get('pipeline_stage', 'Placeholder')}",
            f"Applied Date: {overview.get('applied_date', 'Placeholder')}",
            f"Recruiter: {overview.get('recruiter', 'Placeholder')}",
        ]
        self.overview_content_label.configure(text="\n".join(lines))

    def update_timeline(self, timeline: list[dict[str, object]]) -> None:
        if not timeline:
            self.timeline_label.configure(text="No timeline events.")
            return

        lines = [
            f"{item.get('timestamp', 'n/a')} - {item.get('event_type', 'event')} ({item.get('actor', 'system')})"
            for item in timeline
        ]
        self.timeline_label.configure(text="\n".join(lines))

    def update_tasks(self, tasks: list[dict[str, object]]) -> None:
        if not tasks:
            self.tasks_label.configure(text="No tasks.")
            return

        lines = [
            f"{item.get('title', 'Task')} [{item.get('priority', 'n/a')}] due {item.get('due_at', 'n/a')}"
            for item in tasks
        ]
        self.tasks_label.configure(text="\n".join(lines))

    def update_documents(self, documents: list[dict[str, object]]) -> None:
        if not documents:
            self.documents_label.configure(text="No documents.")
            return

        lines = [
            f"{item.get('document_type', 'doc')}: {item.get('file_name', 'file')} ({item.get('status', 'n/a')})"
            for item in documents
        ]
        self.documents_label.configure(text="\n".join(lines))

    def update_resume_metadata(self, metadata: dict[str, object]) -> None:
        if not metadata:
            self.resume_metadata_label.configure(text="Resume metadata placeholder")
            return

        lines = [
            f"Filename: {metadata.get('file_name', 'placeholder_resume.pdf')}",
            f"Uploaded: {metadata.get('uploaded_at', 'n/a')}",
            f"Source: {metadata.get('source', 'manual_upload')}",
        ]
        self.resume_metadata_label.configure(text="\n".join(lines))

    def update_history(self, history: list[dict[str, object]]) -> None:
        if not history:
            self.history_content_label.configure(text="History placeholder")
            return

        lines = [
            f"{item.get('date', 'n/a')}: {item.get('stage', 'stage')} ({item.get('status', 'status')})"
            for item in history
        ]
        self.history_content_label.configure(text="\n".join(lines))

    def clear_workspace(self) -> None:
        self.clear_header()
        self.update_overview({})
        self.update_timeline([])
        self.update_tasks([])
        self.update_documents([])
        self.update_resume_metadata({})
        self.update_history([])
