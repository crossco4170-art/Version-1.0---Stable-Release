from __future__ import annotations

def _build_today_summary(): return dict(todays_applicants=0, daily_tasks=0, follow_ups_due=0, interviews_today=0)
def _build_widget_data(): return dict(todays_applicants=dict(value=0, items=[]), daily_tasks=dict(value=0, items=[]), applicant_queue=dict(value=0, items=[]), ai_priority_queue=dict(value=0, items=[]), notifications=dict(value=0, items=[]), recruiter_metrics=dict(value=dict()), hiring_metrics=dict(value=dict()))
class DashboardController: ...
def _init(self): self._today_summary=_build_today_summary(); self._widgets=_build_widget_data()
def _load_dashboard(self): self._today_summary=_build_today_summary(); self._widgets=_build_widget_data(); return dict(today_summary=self._today_summary, widgets=self._widgets)
def _refresh_dashboard(self): return self.load_dashboard()
def _get_today_summary(self): return dict(self._today_summary)
def _get_widget_data(self): return dict(self._widgets)
DashboardController.__init__=_init
DashboardController.load_dashboard=_load_dashboard
DashboardController.refresh_dashboard=_refresh_dashboard
DashboardController.get_today_summary=_get_today_summary
DashboardController.get_widget_data=_get_widget_data
