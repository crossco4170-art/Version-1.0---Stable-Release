# SPEC-003 Recruiter Dashboard

## 1. Purpose
Define the recruiter-facing dashboard for Blackcrest RecruitOS Version 2, optimized for Greater Connections Staffing recruiters managing USPS hiring pipelines, while preserving reusable architecture patterns for future clients and industries.

## 2. Business Goals
- Increase recruiter throughput from intake to submission.
- Reduce time-to-first-action on new applicants.
- Improve quality and consistency of candidate progression decisions.
- Provide clear operational visibility across requisitions, stages, and bottlenecks.
- Enable deterministic AI-assisted decisions without replacing recruiter judgment.

## 3. Primary Users
### Primary Role
- USPS-focused Recruiter (Greater Connections Staffing):
  - Reviews high-volume driver and logistics applicants.
  - Prioritizes candidates for phone screen, client submission, hold, or rejection.
  - Tracks daily outreach and follow-up commitments.

### Secondary Roles
- Recruiting Lead:
  - Monitors team productivity and queue health.
  - Identifies blockers and coaching opportunities.
- Operations/Admin:
  - Audits workflow adherence and SLA performance.

## 4. Dashboard Layout
The dashboard uses a three-column information architecture with persistent top navigation.

### Header Bar
- Organization/client selector (default: Greater Connections Staffing -> USPS).
- Global search.
- Notification indicator.
- User actions (profile, settings, sign out).

### Left Column (Action Queue)
- Daily tasks panel.
- High-priority alerts.
- Quick filters.

### Center Column (Operational Work Surface)
- Applicant queue grid/list.
- Candidate detail preview drawer.
- Stage actions and status transitions.

### Right Column (Decision Intelligence)
- AI recommendation panel.
- Match rationale and requirement gaps.
- Recruiter notes and next-step checklist.

## 5. Navigation
### Primary Navigation
- Dashboard
- Applicants
- Job Orders
- Interviews
- Submissions
- Reports

### USPS Recruiter Shortcuts
- New USPS Applicants
- Phone Screen Today
- Ready for Client
- Missing CDL/Background Check
- Follow-ups Due

### Reusability Rule
Navigation labels and route groups must support client-specific aliases (for example USPS-specific queues) without changing core route architecture.

## 6. Dashboard Widgets
Required widgets:
- New Applicants (last 24h)
- Awaiting Recruiter Review
- Ready for Phone Screen
- Ready for Client Submission
- On Hold
- SLA Risk (aging candidates)
- Interviews Today
- Tasks Due Today

Widget behaviors:
- Click-through opens filtered applicant queue.
- Counts are tenant-scoped and refresh on interval.
- Threshold-based color states (normal, warning, critical).

## 7. Applicant Queue
Queue requirements:
- Default sort: newest actionable applicants first.
- Stage-based tabs: New, Review, Phone Screen, Client Review, Hold, Closed.
- USPS-fit columns (configurable by client profile):
  - Name
  - Job Order
  - AI Match Score
  - Recommendation
  - Confidence
  - CDL status
  - Background Check status
  - Last Recruiter Action
  - Days in Stage
- Bulk actions:
  - Advance stage
  - Hold
  - Assign recruiter
  - Add task
- Row-level action menu:
  - Open profile
  - Schedule outreach
  - Add note
  - View AI rationale

## 8. AI Recommendation Panel
Panel scope:
- Consumes deterministic pipeline outputs from matching, scoring, recommendation, and summary services.

Required fields:
- Recommendation level
- Confidence
- Top strengths
- Missing requirements
- Hard requirement failures
- Unknown requirements
- Deterministic recruiter summary

Behavior rules:
- Hard failures prominently displayed at top.
- Unknown requirements shown as uncertainty indicators, not automatic rejection.
- Panel must expose factor-level traceability for audit.
- Recruiter can override recommendation with required reason capture.

## 9. Recruiter Productivity Metrics
Daily and weekly recruiter metrics:
- Applicants reviewed per day
- Time-to-first-action
- Phone screens scheduled/completed
- Follow-up completion rate
- Queue aging reduction
- Recommendations overridden (count and percentage)

Usage:
- Supports coaching and workload balancing.
- Trends visible by recruiter and team roll-up.

## 10. Hiring Metrics
USPS-focused hiring funnel metrics:
- Applicant-to-phone-screen conversion
- Phone-screen-to-client-submission conversion
- Submission-to-interview conversion
- Interview-to-offer conversion
- Offer acceptance rate
- Time-to-fill by job order

Reusable design:
- Metrics must map to configurable funnel stage definitions per client.

## 11. Notifications
Notification channels (in-app for this spec):
- New high-priority applicants
- SLA nearing breach
- Missing required documents (CDL, background check artifacts)
- Interview reminders
- Follow-up tasks overdue

Notification rules:
- Priority tiers: High, Medium, Low
- Deduplicated alerts for repeated events
- Role- and queue-scoped delivery

## 12. Daily Tasks
Task panel requirements:
- Auto-generated tasks from pipeline events.
- Manual recruiter task creation.
- Due-date and overdue grouping.
- One-click completion with optional notes.

USPS examples:
- Verify CDL details
- Request background check update
- Confirm schedule availability
- Submit candidate packet to client contact

## 13. Search and Filters
Global and queue-specific filtering:
- Name, email, phone
- Job order and location
- Pipeline stage
- Recommendation level
- Confidence range
- Hard requirement failures present/absent
- Missing requirement type
- Assigned recruiter
- Date ranges (applied, last activity, stage updated)

Behavior:
- Saved filter presets per recruiter.
- URL/state persistence for shareable views.
- Filter logic must remain deterministic and auditable.

## 14. Performance Requirements
Target performance thresholds:
- Dashboard initial load: <= 2.5 seconds at p95.
- Queue filter/sort response: <= 800 ms at p95.
- Widget refresh latency: <= 2 seconds after data update.
- Pagination/virtualized queue rendering for high-volume days.

Operational constraints:
- Multi-tenant isolation must not degrade response consistency.
- Graceful degradation when AI detail payloads are temporarily unavailable.

## 15. Security
Security requirements:
- Role-based access control for recruiter, lead, and admin views.
- Tenant isolation by organization/client scope.
- Audit trail for stage changes, recommendation overrides, and notes.
- Sensitive candidate data masking where required by role.
- Session and access controls aligned with existing platform authentication standards.

Compliance posture:
- Preserve immutable logs for decision and action traceability.
- Enforce least-privilege visibility in shared team workflows.

## 16. Acceptance Criteria
- Recruiters can view and act on USPS candidate queues without leaving dashboard workflow.
- Deterministic AI recommendation data is displayed with explanation and confidence.
- Hard requirement failures are clearly visible and actionable.
- Daily tasks and notifications drive same-day follow-up execution.
- Search and filters support high-volume queue triage.
- Metrics are available for recruiter productivity and hiring funnel outcomes.
- Architecture supports future client-specific adaptations without redesign.

## 17. Future Enhancements
- Multi-client dashboard themes and terminology overlays.
- SLA forecasting and staffing recommendation alerts.
- Calendar integration for one-click interview scheduling.
- Recruiter performance benchmarking with trend diagnostics.
- Scenario views comparing recommendation policy changes.
- Mobile-optimized workflow for field recruiters.

## 18. Sprint Breakdown
### Sprint 1: Foundation Dashboard Shell
- Core layout (header, queue surface, intelligence panel).
- Navigation and tenant/client context controls.
- Baseline applicant queue and stage tabs.

### Sprint 2: AI Visibility and Queue Actions
- Integrate AI recommendation panel fields.
- Add queue row actions and bulk stage actions.
- Add hard-failure and missing-requirement indicators.

### Sprint 3: Tasks, Notifications, and Filters
- Daily task panel and task lifecycle.
- Notification center with priority tiers.
- Advanced search/filter set and saved views.

### Sprint 4: Metrics and Optimization
- Recruiter productivity dashboards.
- Hiring funnel metrics.
- Performance hardening and SLA monitoring.
- UAT with Greater Connections Staffing USPS recruiting team.
