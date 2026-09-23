from __future__ import annotations

from datetime import datetime

from app.app_state import AppState
from controllers.applicant_workspace_controller import ApplicantWorkspaceController
from models.applicant import ApplicantPipelineStage
from models.client import Client
from models.job_order import JobOrder
from models.organization import Organization, OrganizationStatus
from services.applicant_service import ApplicantService
from tests.helpers import build_test_session
from utils.exceptions import BlackcrestInputError


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


def _seed_applicant_record(tmp_path, *, name: str = "Riley Chen", email: str = "riley@example.com"):
    session = build_test_session(tmp_path / "workspace_controller_real.db")
    service = ApplicantService(session=session)

    organization = Organization(
        name="Greater Connections Staffing",
        legal_name="Greater Connections Staffing LLC",
        status=OrganizationStatus.ACTIVE,
    )
    session.add(organization)
    session.commit()

    client = Client(organization_id=organization.id, company_name="USPS")
    session.add(client)
    session.commit()

    job_order = JobOrder(
        organization_id=organization.id,
        client_id=client.id,
        title="Carrier Associate",
        job_code="USPS-CA-100",
    )
    session.add(job_order)
    session.commit()

    applicant = service.create_applicant(
        organization_id=organization.id,
        client_id=client.id,
        job_order_id=job_order.id,
        name=name,
        first_name=name.split()[0],
        last_name=name.split()[-1],
        email=email,
        phone="(414) 555-0101",
        city="Milwaukee",
        state="WI",
        resume_filename=f"{name.lower().replace(' ', '_')}.pdf",
        resume_path=f"/tmp/{name.lower().replace(' ', '_')}.pdf",
        pipeline_stage=ApplicantPipelineStage.UNDER_REVIEW,
        applied_at=datetime(2026, 7, 5, 9, 30, 0),
        address="123 Alder St",
        current_status="UNDER_REVIEW",
        notes="Real applicant data",
        score=88.0,
    )

    return service, applicant


def test_controller_loads_selected_applicant_from_real_service(tmp_path) -> None:
    service, applicant = _seed_applicant_record(tmp_path)
    state = AppState()
    state.set_selected_applicant(applicant.id)
    view = _FakeView()

    controller = ApplicantWorkspaceController(view=view, app_state=state, app_service=service)

    payload = controller.load_workspace()

    assert payload["applicant_summary"]["applicant_name"] == applicant.name
    assert payload["overview"]["name"] == applicant.name
    assert payload["resume_metadata"]["file_name"] == applicant.resume_filename
    assert payload["overview"]["pipeline_stage"] == applicant.pipeline_stage.value
    assert view.last_header_payload is not None
    assert view.last_header_payload["applicant_name"] == applicant.name


def test_controller_refreshes_when_selected_applicant_changes(tmp_path) -> None:
    service, first = _seed_applicant_record(tmp_path, name="Riley Chen", email="riley@example.com")
    second_service, second = _seed_applicant_record(
        tmp_path,
        name="Sam Park",
        email="sam@example.com",
    )
    state = AppState()
    view = _FakeView()
    controller = ApplicantWorkspaceController(view=view, app_state=state, app_service=service)

    state.set_selected_applicant(second.id)
    controller.refresh_workspace()

    assert controller.get_applicant_summary()["applicant_name"] == second.name
    assert view.last_header_payload["applicant_name"] == second.name


def test_controller_clears_workspace_when_selection_is_none(tmp_path) -> None:
    service, applicant = _seed_applicant_record(tmp_path)
    state = AppState()
    view = _FakeView()
    controller = ApplicantWorkspaceController(view=view, app_state=state, app_service=service)

    state.set_selected_applicant(applicant.id)
    state.set_selected_applicant(None)

    assert controller.get_applicant_summary()["applicant_name"] == "Placeholder Applicant"
    assert controller.get_timeline() == []
    assert controller.get_tasks() == []
    assert controller.get_documents() == []
    assert view.clear_calls >= 1


def test_controller_handles_missing_applicant_gracefully(tmp_path) -> None:
    service, _ = _seed_applicant_record(tmp_path)
    state = AppState()
    state.set_selected_applicant(999999)
    view = _FakeView()
    controller = ApplicantWorkspaceController(view=view, app_state=state, app_service=service)

    payload = controller.refresh_workspace()

    assert payload["applicant_summary"]["applicant_name"] == "Applicant Not Found"
    assert payload["overview"]["error"].startswith("Applicant 999999")


def test_controller_handles_retrieval_error_cleanly(tmp_path) -> None:
    class _ExplodingService:
        def get_applicant(self, applicant_id: int):
            raise BlackcrestInputError("invalid applicant id")

    state = AppState()
    state.set_selected_applicant(42)
    view = _FakeView()
    controller = ApplicantWorkspaceController(view=view, app_state=state, app_service=_ExplodingService())

    payload = controller.refresh_workspace()

    assert payload["applicant_summary"]["applicant_name"] == "Workspace unavailable"
    assert payload["overview"]["error"] == "invalid applicant id"


def test_controller_default_service_uses_preinitialized_database(tmp_path, monkeypatch) -> None:
    service, applicant = _seed_applicant_record(tmp_path)
    monkeypatch.setattr(
        "controllers.applicant_workspace_controller.ApplicantService",
        lambda: ApplicantService(session=service.session),
    )
    state = AppState()
    state.set_selected_applicant(applicant.id)

    controller = ApplicantWorkspaceController(app_state=state)

    assert controller.get_applicant_summary()["applicant_name"] == applicant.name
