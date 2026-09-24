from __future__ import annotations

from typing import Any

from models.applicant import Applicant
from services.applicant_service import ApplicantService
from utils.exceptions import BlackcrestInputError, BlackcrestNotFoundError


class ApplicantWorkspaceController:
    """Coordinates the real applicant workspace data path from AppState into the view."""

    def __init__(
        self,
        view: object | None = None,
        app_state: object | None = None,
        app_service: ApplicantService | None = None,
    ) -> None:
        self._workspace_data = self._build_cleared_workspace_payload()
        self._view = view
        self._app_state = app_state
        self._app_service = app_service or ApplicantService()
        self._last_error: str | None = None

        if self._app_state is not None:
            self.bind_app_state(self._app_state)

    def load_workspace(self) -> dict[str, object]:
        selected_id = self._get_selected_applicant_id()
        if selected_id is None:
            return self.clear_workspace()
        return self.load_selected_applicant(selected_id)

    def refresh_workspace(self) -> dict[str, object]:
        selected_id = self._get_selected_applicant_id()
        if selected_id is None:
            return self.clear_workspace()
        return self.load_selected_applicant(selected_id)

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
        self._last_error = None
        self._workspace_data = self._build_cleared_workspace_payload()
        if self._view is not None and hasattr(self._view, "clear_workspace"):
            self._view.clear_workspace()
        elif self._view is not None and hasattr(self._view, "clear_header"):
            self._view.clear_header()
        return dict(self._workspace_data)

    def load_selected_applicant(self, applicant_id: int) -> dict[str, object]:
        try:
            applicant = self._app_service.get_applicant(applicant_id)
        except (BlackcrestInputError, BlackcrestNotFoundError, ValueError, TypeError, RuntimeError) as exc:
            self._last_error = str(exc)
            return self._render_error_state(str(exc))

        if applicant is None:
            self._last_error = f"Applicant not found: {applicant_id}"
            return self._render_not_found_state(applicant_id)

        self._last_error = None
        self._workspace_data = self._build_workspace_payload(applicant)
        self._sync_view_with_workspace()
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

    def _render_not_found_state(self, applicant_id: int) -> dict[str, object]:
        self._workspace_data = self._build_cleared_workspace_payload()
        self._workspace_data["applicant_summary"] = {
            "applicant_name": "Applicant Not Found",
            "email": "",
            "phone": "",
            "pipeline_stage": "UNKNOWN",
            "assigned_recruiter": "",
            "job_order": "",
            "client": "",
            "location": "",
            "applied_date": "",
            "resume_metadata": {"file_name": "", "uploaded_at": "", "source": ""},
            "interview_history": [],
            "applicant_id": applicant_id,
        }
        self._workspace_data["overview"] = {"name": "Applicant Not Found", "error": f"Applicant {applicant_id} not found."}
        self._workspace_data["resume_metadata"] = {"file_name": "", "uploaded_at": "", "source": ""}
        self._workspace_data["history"] = []
        self._workspace_data["timeline"] = []
        self._workspace_data["tasks"] = []
        self._workspace_data["documents"] = []
        if self._view is not None and hasattr(self._view, "clear_workspace"):
            self._view.clear_workspace()
        elif self._view is not None and hasattr(self._view, "clear_header"):
            self._view.clear_header()
        return dict(self._workspace_data)

    def _render_error_state(self, message: str) -> dict[str, object]:
        self._workspace_data = self._build_cleared_workspace_payload()
        self._workspace_data["applicant_summary"] = {
            "applicant_name": "Workspace unavailable",
            "email": "",
            "phone": "",
            "pipeline_stage": "ERROR",
            "assigned_recruiter": "",
            "job_order": "",
            "client": "",
            "location": "",
            "applied_date": "",
            "resume_metadata": {"file_name": "", "uploaded_at": "", "source": ""},
            "interview_history": [],
            "error": message,
        }
        self._workspace_data["overview"] = {"name": "Workspace unavailable", "error": message}
        self._workspace_data["resume_metadata"] = {"file_name": "", "uploaded_at": "", "source": ""}
        self._workspace_data["history"] = []
        self._workspace_data["timeline"] = []
        self._workspace_data["tasks"] = []
        self._workspace_data["documents"] = []
        if self._view is not None and hasattr(self._view, "clear_workspace"):
            self._view.clear_workspace()
        elif self._view is not None and hasattr(self._view, "clear_header"):
            self._view.clear_header()
        return dict(self._workspace_data)

    def _build_workspace_payload(self, applicant: Applicant) -> dict[str, object]:
        applicant_name = self._coalesce_value(
            getattr(applicant, "name", None),
            " ".join(
                part for part in (getattr(applicant, "first_name", None), getattr(applicant, "last_name", None)) if part
            ),
            "Unknown Applicant",
        )
        city = getattr(applicant, "city", None) or ""
        state = getattr(applicant, "state", None) or ""
        location = ", ".join(part for part in (city, state) if part) if city or state else ""

        job_order_name = ""
        job_order = getattr(applicant, "job_order", None)
        if job_order is not None:
            job_order_name = getattr(job_order, "title", None) or getattr(job_order, "job_code", None) or ""

        client_name = ""
        client = getattr(applicant, "client", None)
        if client is not None:
            client_name = getattr(client, "company_name", None) or getattr(client, "name", None) or ""

        pipeline_stage = getattr(applicant, "pipeline_stage", None)
        pipeline_stage_value = pipeline_stage.value if hasattr(pipeline_stage, "value") else str(pipeline_stage or "NEW")
        applied_at = getattr(applicant, "applied_at", None)
        applied_date = applied_at.isoformat() if hasattr(applied_at, "isoformat") else str(applied_at or "")
        date_added = getattr(applicant, "date_added", None)
        uploaded_at = date_added.isoformat() if hasattr(date_added, "isoformat") else str(date_added or "")

        summary = {
            "applicant_name": applicant_name,
            "email": getattr(applicant, "email", None) or "",
            "phone": getattr(applicant, "phone", None) or "",
            "pipeline_stage": pipeline_stage_value,
            "assigned_recruiter": "Current Recruiter",
            "job_order": job_order_name,
            "client": client_name,
            "location": location,
            "applied_date": applied_date,
            "resume_metadata": {
                "file_name": getattr(applicant, "resume_filename", None) or "",
                "uploaded_at": uploaded_at,
                "source": "database",
            },
            "interview_history": [],
        }

        overview = {
            "name": applicant_name,
            "email": summary["email"],
            "phone": summary["phone"],
            "location": location,
            "job_order": job_order_name,
            "client": client_name,
            "pipeline_stage": pipeline_stage_value,
            "applied_date": applied_date,
            "recruiter": "Current Recruiter",
        }

        return {
            "applicant_summary": summary,
            "overview": overview,
            "resume_metadata": dict(summary["resume_metadata"]),
            "history": [],
            "timeline": [],
            "tasks": [],
            "documents": [
                {
                    "document_type": "resume",
                    "file_name": getattr(applicant, "resume_filename", None) or "",
                    "status": "available" if getattr(applicant, "resume_filename", None) else "missing",
                }
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
                "current_stage": pipeline_stage_value,
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
                "email": "",
                "phone": "",
                "pipeline_stage": "NEW",
                "assigned_recruiter": "",
                "job_order": "",
                "client": "",
                "location": "",
                "applied_date": "",
                "resume_metadata": {"file_name": "", "uploaded_at": "", "source": ""},
                "interview_history": [],
            },
            "overview": {},
            "resume_metadata": {"file_name": "", "uploaded_at": "", "source": ""},
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

    def _coalesce_value(self, *values: Any) -> Any:
        for value in values:
            if value not in (None, ""):
                return value
        return ""
