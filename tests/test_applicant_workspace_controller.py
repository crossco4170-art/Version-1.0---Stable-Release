from __future__ import annotations

from app.app_state import AppState
from controllers.applicant_workspace_controller import ApplicantWorkspaceController


class _FakeView:
    def __init__(self) -> None:
        self.last_header_payload: dict[str, object] | None = None
        self.overview_payload: dict[str, object] | None = None
        self.timeline_payload: list[dict[str, object]] | None = None
        self.tasks_payload: list[dict[str, object]] | None = None
        self.documents_payload: list[dict[str, object]] | None = None
        self.resume_metadata_payload: dict[str, object] | None = None
        self.history_payload: list[dict[str, object]] | None = None
        self.clear_calls = 0

    def set_applicant_header(self, payload: dict[str, object]) -> None:
        self.last_header_payload = dict(payload)

    def update_overview(self, payload: dict[str, object]) -> None:
        self.overview_payload = dict(payload)

    def update_timeline(self, payload: list[dict[str, object]]) -> None:
        self.timeline_payload = [dict(item) for item in payload]

    def update_tasks(self, payload: list[dict[str, object]]) -> None:
        self.tasks_payload = [dict(item) for item in payload]

    def update_documents(self, payload: list[dict[str, object]]) -> None:
        self.documents_payload = [dict(item) for item in payload]

    def update_resume_metadata(self, payload: dict[str, object]) -> None:
        self.resume_metadata_payload = dict(payload)

    def update_history(self, payload: list[dict[str, object]]) -> None:
        self.history_payload = [dict(item) for item in payload]

    def clear_header(self) -> None:
        self.clear_calls += 1

    def clear_workspace(self) -> None:
        self.clear_calls += 1
        self.last_header_payload = None
        self.overview_payload = None
        self.timeline_payload = None
        self.tasks_payload = None
        self.documents_payload = None
        self.resume_metadata_payload = None
        self.history_payload = None


def test_controller_initializes() -> None:
    controller = ApplicantWorkspaceController()

    assert controller is not None


def test_load_mock_applicant_returns_deterministic_profile() -> None:
    controller = ApplicantWorkspaceController()

    profile = controller.load_mock_applicant()

    assert profile["name"] == "Jordan Miles"
    assert profile["email"] == "jordan.miles@example.com"
    assert profile["phone"] == "(414) 555-0148"
    assert profile["location"] == "Milwaukee, WI"
    assert profile["job_order"] == "USPS Carrier Associate"
    assert profile["client"] == "USPS"
    assert profile["pipeline_stage"] == "REVIEW"
    assert profile["applied_date"] == "2026-07-05"
    assert profile["recruiter"] == "Current Recruiter"
    assert profile["resume_filename"] == "jordan_miles_resume.pdf"


def test_workspace_loads_with_all_sections_populated() -> None:
    controller = ApplicantWorkspaceController()

    payload = controller.load_workspace()

    assert payload["applicant_summary"]["applicant_name"] == "Jordan Miles"
    assert payload["overview"]["name"] == "Jordan Miles"
    assert payload["resume_metadata"]["file_name"] == "jordan_miles_resume.pdf"
    assert len(payload["history"]) > 0
    assert len(payload["timeline"]) > 0
    assert len(payload["tasks"]) > 0
    assert len(payload["documents"]) > 0


def test_header_remains_synchronized_with_mock_data() -> None:
    view = _FakeView()
    controller = ApplicantWorkspaceController(view=view)

    controller.load_workspace()

    assert view.last_header_payload is not None
    assert view.last_header_payload["applicant_name"] == "Jordan Miles"
    assert view.overview_payload is not None
    assert view.overview_payload["name"] == "Jordan Miles"


def test_all_sections_are_pushed_to_view() -> None:
    view = _FakeView()
    controller = ApplicantWorkspaceController(view=view)

    controller.load_workspace()

    assert view.overview_payload is not None
    assert view.timeline_payload is not None and len(view.timeline_payload) > 0
    assert view.tasks_payload is not None and len(view.tasks_payload) > 0
    assert view.documents_payload is not None and len(view.documents_payload) > 0
    assert view.resume_metadata_payload is not None
    assert view.history_payload is not None and len(view.history_payload) > 0


def test_clearing_app_state_clears_workspace() -> None:
    view = _FakeView()
    controller = ApplicantWorkspaceController(view=view)
    state = AppState()

    controller.bind_app_state(state)
    state.set_selected_applicant(101)

    assert controller.get_applicant_summary()["applicant_name"] == "Jordan Miles"

    state.set_selected_applicant(None)

    assert view.clear_calls >= 1
    assert controller.get_applicant_summary()["applicant_name"] == "Placeholder Applicant"
    assert controller.get_timeline() == []
    assert controller.get_tasks() == []
    assert controller.get_documents() == []
