from __future__ import annotations


class ApplicantWorkspaceController:
    """Coordinates placeholder workspace data without business or data-source logic."""

    def __init__(self, view: object | None = None) -> None:
        self._workspace_data = self._build_cleared_workspace_payload()
        self._view = view
        self._app_state = None

        self._mock_applicant = {
            "name": "Jordan Miles",
            "email": "jordan.miles@example.com",
            "phone": "(414) 555-0148",
            "location": "Milwaukee, WI",
            "job_order": "USPS Carrier Associate",
            "client": "USPS",
            "pipeline_stage": "REVIEW",
            "applied_date": "2026-07-05",
            "recruiter": "Current Recruiter",
            "resume_filename": "jordan_miles_resume.pdf",
        }

    def load_workspace(self) -> dict[str, object]:
        self._workspace_data = self._build_workspace_payload(self.load_mock_applicant())
        self._sync_view_with_workspace()
        return dict(self._workspace_data)

    def refresh_workspace(self) -> dict[str, object]:
        selected_id = self._get_selected_applicant_id()
        if selected_id is None and self._app_state is not None:
            return self.clear_workspace()
        return self.load_workspace()

    def load_mock_applicant(self) -> dict[str, object]:
        return dict(self._mock_applicant)

    def bind_app_state(self, app_state: object) -> None:
        self._app_state = app_state
        if hasattr(app_state, "add_observer"):
            app_state.add_observer(self._on_app_state_change)
        self.refresh_workspace()

    def on_selected_applicant_changed(self) -> dict[str, object]:
        return self.refresh_workspace()

    def refresh_header(self) -> dict[str, object]:
        summary = self.get_applicant_summary()
        if self._view is not None and hasattr(self._view, "set_applicant_header"):
            self._view.set_applicant_header(summary)
        return dict(summary)

    def clear_workspace(self) -> dict[str, object]:
        self._workspace_data = self._build_cleared_workspace_payload()
        if self._view is not None and hasattr(self._view, "clear_workspace"):
            self._view.clear_workspace()
        elif self._view is not None and hasattr(self._view, "clear_header"):
            self._view.clear_header()
        return dict(self._workspace_data)

    def get_applicant_summary(self) -> dict[str, object]:
        return dict(self._workspace_data["applicant_summary"])

    def get_timeline(self) -> list[dict[str, object]]:
        return [dict(item) for item in self._workspace_data["timeline"]]

    def get_tasks(self) -> list[dict[str, object]]:
        return [dict(item) for item in self._workspace_data["tasks"]]

    def get_documents(self) -> list[dict[str, object]]:
        return [dict(item) for item in self._workspace_data["documents"]]

    def get_ai_placeholder(self) -> dict[str, object]:
        return dict(self._workspace_data["ai_placeholder"])

    def get_pipeline_controls(self) -> dict[str, object]:
        return dict(self._workspace_data["pipeline_controls"])

    def get_quick_actions(self) -> list[dict[str, object]]:
        return [dict(item) for item in self._workspace_data["quick_actions"]]

    def _on_app_state_change(self, field_name: str, value: object) -> None:
        if field_name == "selected_applicant":
            self.on_selected_applicant_changed()

    def _sync_view_with_workspace(self) -> None:
        if self._view is None:
            return

        summary = self.get_applicant_summary()
        if hasattr(self._view, "set_applicant_header"):
            self._view.set_applicant_header(summary)
        if hasattr(self._view, "update_overview"):
            self._view.update_overview(dict(self._workspace_data["overview"]))
        if hasattr(self._view, "update_timeline"):
            self._view.update_timeline(self.get_timeline())
        if hasattr(self._view, "update_tasks"):
            self._view.update_tasks(self.get_tasks())
        if hasattr(self._view, "update_documents"):
            self._view.update_documents(self.get_documents())
        if hasattr(self._view, "update_resume_metadata"):
            self._view.update_resume_metadata(dict(self._workspace_data["resume_metadata"]))
        if hasattr(self._view, "update_history"):
            self._view.update_history([dict(item) for item in self._workspace_data["history"]])

    def _get_selected_applicant_id(self) -> int | None:
        if self._app_state is not None and hasattr(self._app_state, "get_selected_applicant"):
            return self._app_state.get_selected_applicant()
        return None

    def _build_workspace_payload(self, profile: dict[str, object]) -> dict[str, object]:
        summary = {
            "applicant_name": profile["name"],
            "email": profile["email"],
            "phone": profile["phone"],
            "pipeline_stage": profile["pipeline_stage"],
            "assigned_recruiter": profile["recruiter"],
            "job_order": profile["job_order"],
            "client": profile["client"],
            "location": profile["location"],
            "applied_date": profile["applied_date"],
            "resume_metadata": {
                "file_name": profile["resume_filename"],
                "uploaded_at": "2026-07-05T08:40:00",
                "source": "manual_upload",
            },
            "interview_history": [
                {
                    "stage": "intro_screen",
                    "status": "completed",
                    "date": "2026-07-06",
                    "notes": "Completed recruiter intro call with positive candidate response.",
                }
            ],
        }

        return {
            "applicant_summary": summary,
            "overview": {
                "name": profile["name"],
                "email": profile["email"],
                "phone": profile["phone"],
                "location": profile["location"],
                "job_order": profile["job_order"],
                "client": profile["client"],
                "pipeline_stage": profile["pipeline_stage"],
                "applied_date": profile["applied_date"],
                "recruiter": profile["recruiter"],
            },
            "resume_metadata": dict(summary["resume_metadata"]),
            "history": list(summary["interview_history"]),
            "timeline": [
                {
                    "event_type": "application_submitted",
                    "timestamp": "2026-07-05T08:40:00",
                    "actor": profile["name"],
                    "notes": f"Applied to {profile['job_order']} ({profile['client']}).",
                },
                {
                    "event_type": "resume_reviewed",
                    "timestamp": "2026-07-05T13:25:00",
                    "actor": profile["recruiter"],
                    "notes": "Resume reviewed and moved to REVIEW stage.",
                },
            ],
            "tasks": [
                {
                    "title": f"Call {profile['name']} for interview availability",
                    "priority": "high",
                    "status": "open",
                    "due_at": "2026-07-08T10:00:00",
                },
                {
                    "title": "Confirm valid driver documentation",
                    "priority": "medium",
                    "status": "open",
                    "due_at": "2026-07-08T15:30:00",
                },
            ],
            "documents": [
                {
                    "document_type": "resume",
                    "file_name": profile["resume_filename"],
                    "status": "available",
                },
                {
                    "document_type": "drivers_license",
                    "file_name": "jordan_miles_license.pdf",
                    "status": "verified",
                },
            ],
            "ai_placeholder": {
                "recommendation": "placeholder",
                "match_percentage": 0.0,
                "confidence": 0.0,
                "summary": "AI placeholder payload for future workspace integration.",
                "strengths": [],
                "missing_requirements": [],
            },
            "pipeline_controls": {
                "current_stage": "REVIEW",
                "available_actions": ["move_stage", "hold", "schedule_interview"],
                "status": "placeholder",
            },
            "quick_actions": [
                {"action": "add_note", "label": "Add Note"},
                {"action": "create_task", "label": "Create Task"},
                {"action": "send_email", "label": "Send Email"},
            ],
            "attachments": [],
        }

    def _build_cleared_workspace_payload(self) -> dict[str, object]:
        return {
            "applicant_summary": {
                "applicant_name": "Placeholder Applicant",
                "email": "placeholder@example.com",
                "phone": "(000) 000-0000",
                "pipeline_stage": "NEW",
                "assigned_recruiter": "Current Recruiter",
                "job_order": "Placeholder Job Order",
                "client": "USPS",
                "location": "Milwaukee, WI",
                "applied_date": "2026-07-06",
                "resume_metadata": {
                    "file_name": "placeholder_resume.pdf",
                    "uploaded_at": "2026-07-06T09:00:00",
                    "source": "manual_upload",
                },
                "interview_history": [],
            },
            "overview": {},
            "resume_metadata": {},
            "history": [],
            "timeline": [],
            "tasks": [],
            "documents": [],
            "ai_placeholder": {
                "recommendation": "placeholder",
                "match_percentage": 0.0,
                "confidence": 0.0,
                "summary": "AI placeholder payload for future workspace integration.",
                "strengths": [],
                "missing_requirements": [],
            },
            "pipeline_controls": {
                "current_stage": "NEW",
                "available_actions": ["move_stage", "hold", "schedule_interview"],
                "status": "placeholder",
            },
            "quick_actions": [
                {"action": "add_note", "label": "Add Note"},
                {"action": "create_task", "label": "Create Task"},
                {"action": "send_email", "label": "Send Email"},
            ],
            "attachments": [],
        }
