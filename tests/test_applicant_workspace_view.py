from __future__ import annotations

import tkinter as tk
import pytest
import customtkinter as customtkinter

from views.applicant_workspace_view import ApplicantWorkspaceView, OVERVIEW, RESUME, AI_REVIEW, DOCUMENTS, HISTORY

def _s(codes): return str().join(chr(i) for i in codes)
def _make_view():
 try: root = customtkinter.CTk()
 except tk.TclError as exc: pytest.skip(str(exc))
 root.grid_columnconfigure(0, weight=1)
 root.grid_rowconfigure(0, weight=1)
 view = ApplicantWorkspaceView(root)
 view.grid(row=0, column=0, sticky=tk.NSEW)
 root.update_idletasks()
 return root, view
def _dispose(root): root.destroy()

def test_workspace_loads(): root, view = _make_view(); assert view.winfo_exists() == 1; _dispose(root)
def test_three_panel_layout(): root, view = _make_view(); assert view.left_panel.winfo_exists() == 1 and view.center_panel.winfo_exists() == 1 and view.right_panel.winfo_exists() == 1; _dispose(root)
def test_header_exists(): root, view = _make_view(); assert view.header_frame.winfo_exists() == 1 and view.applicant_name_label.winfo_exists() == 1 and view.pipeline_stage_label.winfo_exists() == 1 and view.assigned_recruiter_label.winfo_exists() == 1 and view.job_order_label.winfo_exists() == 1 and view.client_label.winfo_exists() == 1 and view.location_label.winfo_exists() == 1 and view.applied_date_label.winfo_exists() == 1; _dispose(root)
def test_tabs_exist(): root, view = _make_view(); names = set(view.workspace_tabs._tab_dict.keys()); assert names == {OVERVIEW, RESUME, AI_REVIEW, DOCUMENTS, HISTORY}; _dispose(root)
def test_right_panel_placeholders_exist(): root, view = _make_view(); assert view.ai_recommendation_placeholder.winfo_exists() == 1 and view.match_percentage_placeholder.winfo_exists() == 1 and view.confidence_placeholder.winfo_exists() == 1 and view.pipeline_controls_placeholder.winfo_exists() == 1 and view.quick_actions_placeholder.winfo_exists() == 1; _dispose(root)
def test_layout_resizes(): root, view = _make_view(); w0 = view.winfo_width(); h0 = view.winfo_height(); root.geometry(_s([49,52,53,48,120,57,48,48])); root.update_idletasks(); assert view.winfo_width() >= w0 and view.winfo_height() >= h0; _dispose(root)
