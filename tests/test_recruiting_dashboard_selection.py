from __future__ import annotations

from app.app_state import AppState
from controllers.applicant_workspace_controller import ApplicantWorkspaceController
from desktop.recruiting_dashboard import RecruitingDashboard
from tests.test_applicant_workspace_controller import _FakeView, _seed_applicant_record


def _queue(service, state, on_selected):
    queue = RecruitingDashboard.__new__(RecruitingDashboard)
    queue.applicant_service = service
    queue.app_state = state
    queue.on_applicant_selected = on_selected
    return queue


def test_queue_loads_real_applicants_and_selects_into_app_state(tmp_path) -> None:
    service, first = _seed_applicant_record(tmp_path, name="Riley Chen", email="riley@example.com")
    state = AppState()
    opened: list[int] = []
    queue = _queue(service, state, opened.append)

    applicants = service.list_applicants()
    queue.select_applicant(first.id)

    assert [applicant.id for applicant in applicants] == [first.id]
    assert state.get_selected_applicant() == first.id
    assert opened == [first.id]


def test_real_queue_selection_hydrates_and_switches_workspace(tmp_path) -> None:
    service, first = _seed_applicant_record(tmp_path, name="Riley Chen", email="riley@example.com")
    _, second = _seed_applicant_record(tmp_path, name="Sam Park", email="sam@example.com")
    state = AppState()
    view = _FakeView()
    opened: list[int] = []
    controller = ApplicantWorkspaceController(view=view, app_state=state, app_service=service)
    queue = _queue(service, state, opened.append)

    queue.select_applicant(first.id)
    assert state.get_selected_applicant() == first.id
    assert controller.get_applicant_summary()["applicant_name"] == first.name

    queue.select_applicant(second.id)
    assert state.get_selected_applicant() == second.id
    assert controller.get_applicant_summary()["applicant_name"] == second.name

    state.set_selected_applicant(None)
    assert controller.get_applicant_summary()["applicant_name"] == "Placeholder Applicant"
    assert opened == [first.id, second.id]