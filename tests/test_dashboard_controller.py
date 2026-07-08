from __future__ import annotations

from controllers.dashboard_controller import DashboardController

def test_controller_initializes(): controller=DashboardController(); assert controller is not None
def test_dashboard_loads(): controller=DashboardController(); payload=controller.load_dashboard(); assert len(payload)==2

def test_refresh_works(): controller=DashboardController(); first=controller.load_dashboard(); refreshed=controller.refresh_dashboard(); assert first.keys()==refreshed.keys()
def test_widget_data_structure(): controller=DashboardController(); widgets=controller.get_widget_data(); expected=dict(todays_applicants=0, daily_tasks=0, applicant_queue=0, ai_priority_queue=0, notifications=0, recruiter_metrics=0, hiring_metrics=0); assert set(widgets.keys())==set(expected.keys())
def test_summary_data_structure(): controller=DashboardController(); summary=controller.get_today_summary(); expected=dict(todays_applicants=0, daily_tasks=0, follow_ups_due=0, interviews_today=0); assert set(summary.keys())==set(expected.keys())
