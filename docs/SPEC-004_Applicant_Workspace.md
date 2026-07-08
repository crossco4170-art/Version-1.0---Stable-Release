# SPEC-004 Applicant Workspace

## 1. Purpose
Define the Applicant Workspace experience for Blackcrest RecruitOS Version 2, focused on helping recruiters review, progress, and submit candidates efficiently with deterministic AI support and auditable workflow actions.

## 2. Scope
In scope:
- Applicant-centric workspace layout and workflow orchestration.
- Candidate profile review, stage movement, and action tracking.
- Deterministic AI insights display (match, recommendation, summary) from existing services.
- Recruiter collaboration notes and task visibility.

Out of scope:
- New AI model training.
- External API integrations not already approved.
- Authentication or authorization redesign.

## 3. Business Goals
- Reduce time-to-decision for each applicant.
- Improve recruiter consistency in stage transitions.
- Increase submission quality to client.
- Ensure clear auditability for applicant actions and decisions.

## 4. Primary Users
- Recruiter (primary)
- Recruiting Lead (secondary)
- Operations/Admin (secondary, read/audit heavy)

## 5. Workspace Layout
- Header: applicant identity, stage, owner, and quick actions.
- Left panel: timeline, tasks, and communication log.
- Center panel: resume, profile details, and evaluation artifacts.
- Right panel: AI insights, requirement fit, recommendation, and summary.

## 6. Core Workflow
1. Open applicant from queue/search.
2. Review profile and resume details.
3. Inspect deterministic AI outputs.
4. Perform next workflow action (advance, hold, reject, schedule).
5. Log rationale and notes.
6. Persist state and activity history.

## 7. Data Dependencies
- Applicant
- Job Order
- Client
- Organization
- AI outputs:
  - MatchResult
  - Recommendation
  - Recruiter Summary

## 8. AI Insights Panel
Display only deterministic outputs from existing pipeline:
- Match percentage
- Confidence
- Requirement matches/gaps
- Hard requirement failures
- Recommendation
- Recruiter summary

## 9. Stage Actions
- Advance stage
- Move to hold
- Re-open for review
- Mark closed/rejected
- Escalate to lead review

Each action requires:
- Actor identity
- Timestamp
- Optional reason (required for override/exception paths)

## 10. Notes and Collaboration
- Structured recruiter notes
- Internal-only comments
- Mention/assignment support (future-ready)
- Immutable action audit entries

## 11. Search and Filtering in Workspace Context
- Within-applicant sections: resume, notes, timeline, AI rationale
- Cross-applicant filters: stage, recommendation, confidence, owner, SLA risk

## 12. Performance Requirements
- Applicant workspace open: <= 2.5s p95
- Action commit response: <= 800ms p95
- Timeline refresh after action: <= 1.5s p95

## 13. Security and Audit
- Tenant isolation by organization/client scope
- Role-based view and action permissions
- Full audit trail for stage movement and overrides
- Sensitive data visibility restricted by role

## 14. Acceptance Criteria
- Recruiter can complete end-to-end applicant review from one workspace.
- Deterministic AI outputs are visible and traceable.
- Hard requirement failures are clearly surfaced.
- Stage transitions are persisted with audit records.
- Workspace supports USPS-style high-volume recruiting while remaining client-agnostic.

## 15. Risks and Constraints
- High-volume queue pressure may impact responsiveness.
- Data quality gaps in resumes can reduce confidence.
- Workflow consistency depends on clear required-action policies.

## 16. Future Enhancements
- Side-by-side applicant comparison.
- Interview scheduling shortcuts inside workspace.
- Policy-driven override reason templates.
- Workspace personalization presets.

## 17. Sprint Breakdown
### Sprint 1
- Workspace shell, applicant header, and core profile panels.

### Sprint 2
- Deterministic AI insights panel and action controls.

### Sprint 3
- Notes/collaboration and timeline audit hardening.

### Sprint 4
- Performance optimization and UAT stabilization.

### Sprint 5
- UX polish
- Accessibility
- Performance tuning
- Bug fixing
- User Acceptance Testing

## 18. Detailed Applicant Header Specification
The applicant header is a persistent top workspace strip and must remain visible while recruiters navigate applicant sub-sections.

Header fields:
- Applicant full name
- Applicant ID
- Current pipeline stage
- Stage aging indicator (days in stage)
- Assigned recruiter
- Primary job order reference
- Location (city/state)
- Last activity timestamp

Header quick actions:
- Advance stage
- Move to hold
- Add note
- Create task
- Open communication log

Behavior requirements:
- Header data must update immediately after stage changes or assignment updates.
- Stage aging must be visually distinguishable for SLA-risk records.
- Action availability must respect role permissions and tenant boundaries.

## 19. Resume Viewer and Parsed Resume Profile
The workspace must include a dual-view resume section to support both raw document review and structured AI extraction verification.

Resume Viewer requirements:
- Inline resume preview for text and supported document formats.
- Download resume action.
- Source metadata (filename, upload timestamp, uploader/source).

Parsed ResumeProfile requirements:
- Contact details (name, email, phone, city, state)
- Skills
- Previous employers
- Job titles
- Employment dates
- Years of experience
- Education
- Certifications
- Licenses
- Delivery experience
- Management experience
- CDL indicator
- Military indicator

Verification workflow:
- Recruiter can compare parsed fields against raw resume content.
- Mismatch notes can be captured in recruiter notes/activity timeline.

## 20. Expanded AI Intelligence Panel
The AI panel must display deterministic outputs from the existing pipeline and remain fully explainable.

Required fields:
- Match %
- Recommendation
- Confidence
- Strengths
- Preferred Matches
- Missing Requirements
- Unknown Requirements
- Hard Requirement Failures
- Requirement Breakdown
- Recruiter Summary

Requirement Breakdown format:
- Requirement name
- Required vs preferred flag
- Candidate value
- Expected value
- Matched status
- Requirement confidence
- Notes/evidence

Display rules:
- Hard Requirement Failures appear at top with high severity.
- Unknown Requirements must be called out as uncertainty, not automatic rejection.
- Recommendation must always align with deterministic recommendation engine output.
- Recruiter Summary must be deterministic template output with no generative variability.

## 21. Dedicated Applicant Timeline (Timestamped Events)
The workspace must include an immutable, timestamped timeline of applicant lifecycle events and recruiter actions.

Minimum timeline event sequence:
- Application Submitted
- Resume Parsed
- AI Evaluated
- Recruiter Reviewed
- Phone Screen
- Submitted to Client
- Client Interview
- Offer
- Hire

Event entry requirements:
- Event type
- Event timestamp (UTC)
- Actor (system/recruiter/admin)
- Event notes/details
- Related entity reference (job order, task, interview, submission)

Timeline behavior:
- New events append in chronological order and support reverse-chronological display.
- Timeline entries are immutable; corrections are additive events.
- Filters support event type, actor, and date range.

## 22. Documents and Attachments (USPS Recruiting)
The workspace must provide a dedicated documents section for operational recruiting artifacts.

Supported document groups:
- Resume (current and historical versions)
- Background check documents
- Driver's license documents
- Driving record documents
- Drug test documents
- Interview artifacts (notes, forms)
- Client submission packet artifacts

Document capabilities:
- Upload
- Download
- Version visibility
- Document type tagging
- Timestamped audit metadata

USPS workflow requirement:
- USPS-critical compliance documents (driver's license, driving record, drug test, background check) must be easy to identify and review before client submission.

## 23. Communication History
The workspace must include a communication history panel for candidate and internal communications.

Communication record types:
- Phone call logs
- SMS notes (metadata and summary)
- Email logs (metadata and summary)
- Internal team communications related to applicant progression

Communication fields:
- Timestamp
- Direction (inbound/outbound/internal)
- Actor/sender
- Channel
- Subject/summary
- Outcome/next step

Behavior requirements:
- Communication history should be searchable and filterable by channel/date/actor.
- Recruiters should be able to link communications to tasks or timeline events.

## 24. Client Submission History
The workspace must capture each client submission event and status transition.

Submission fields:
- Submission timestamp
- Submitted by
- Target client contact
- Submission package version
- Submission status (submitted, acknowledged, interview requested, rejected, accepted)
- Client feedback notes

Behavior requirements:
- Maintain immutable submission audit history.
- Allow multiple submissions per applicant across different job orders when valid.
- Show latest submission state prominently in workspace overview.

## 25. Recruiter Tasks
The workspace must provide a task system for applicant-specific execution management.

Task fields:
- Task title
- Task type
- Priority
- Due date/time
- Assigned recruiter
- Status (open, in progress, completed, blocked)
- Completion notes

Task behaviors:
- Create tasks directly from AI gaps or timeline events.
- Support recurring follow-up tasks.
- Highlight overdue tasks in workspace header and timeline context.
- Task completion must generate timeline activity entries.

## 26. Workspace Navigation Blueprint
Applicant Workspace

----------------------------------------------------
Overview | Resume | AI Review | Documents | History
----------------------------------------------------

Overview
---------
Applicant Summary
Pipeline Stage
Current Tasks

Resume
-------
PDF Viewer
Parsed Resume

AI Review
---------
Match %
Recommendation
Confidence
Requirement Breakdown

Documents
---------
Resume
Driver's License
Driving Record
Drug Test
Background Check

History
-------
Timeline
Notes
Communications
Submissions

## 27. Primary Action Menu
The Applicant Workspace must expose a primary action menu for high-frequency recruiter actions.

Required primary actions:
- Move Stage
- Schedule Interview
- Submit to USPS
- Add Note
- Create Task
- Send Email
- More...

Behavior requirements:
- Actions must be available from the workspace header and applicant quick-action controls.
- Action availability must be role- and stage-aware.
- Each action must create a timestamped timeline event on completion.
- "More..." opens less-frequent actions without cluttering the primary menu.
