# SPEC-001: Applicant Intake Pipeline

Status: Draft
Version: 2.0
Last Updated: 2026-07-02
Product: Blackcrest RecruitOS
Organization: Greater Connections Staffing
Client: USPS
Primary Job: Rural Carrier Associate / Delivery Driver

## 1. Purpose
Define the Version 2 engineering specification for the Applicant Intake Pipeline in Blackcrest RecruitOS. This specification standardizes how applicants from greaterconnect.com (Wix application form) are ingested, enriched, reviewed, advanced through recruiting stages, and submitted to USPS.

## 2. Business Goals
- Increase qualified applicant throughput for USPS Rural Carrier Associate and Delivery Driver hiring.
- Reduce recruiter administrative effort between application receipt and submission to USPS.
- Improve applicant data quality and consistency before recruiter review.
- Provide transparent stage-level visibility from application to hire.
- Ensure compliance-ready auditability for staffing operations.

## Architecture Foundation
Blackcrest RecruitOS Version 2 is built on the Version 1 foundation.

This specification reuses the existing platform capabilities below. These systems are to be extended, not replaced:
- Resume Parser
- Resume Evaluator
- Interview Scheduler
- Reporting Engine
- Gmail Notification Service
- Authentication
- Configuration System
- Password Hashing
- Test Framework

## 3. Actors
- Applicant: submits application on greaterconnect.com using Wix form.
- Recruiter: reviews applicants, conducts interviews, and submits candidates to USPS.
- Recruiting Manager: monitors funnel health and operational performance.
- USPS Reviewer: evaluates submitted candidates.
- System Services: ingestion, parsing, AI summarization, workflow orchestration, logging, and reporting.

## 4. Functional Requirements
- FR-1 Ingestion from Source: system shall ingest applications submitted via greaterconnect.com Wix form.
- FR-2 Candidate Creation: system shall create a candidate profile for each accepted application.
- FR-3 Resume Parsing: system shall parse resume content and extract structured candidate attributes.
- FR-4 AI Candidate Summary: system shall generate a concise candidate summary for recruiter decision support.
- FR-5 Stage Management: system shall assign and maintain each candidate's current pipeline stage.
- FR-6 Recruiter Review Support: system shall present candidate profile, parsed resume insights, and AI summary in a single review context.
- FR-7 Interview Tracking: system shall record recruiter phone interview outcomes and notes.
- FR-8 Client Submission: system shall support recruiter submission of selected candidates to USPS.
- FR-9 USPS Decision Tracking: system shall record USPS review outcomes, offers, and hires.
- FR-10 Error Visibility: system shall provide actionable intake and processing error statuses.
- FR-11 Manual Correction: authorized recruiters shall be able to correct non-locked applicant fields.
- FR-12 Duplicate Handling: system shall detect likely duplicates and require explicit recruiter resolution.

### Applicant Profile Requirements
The applicant profile shall include structured qualification fields used for reporting and recruiter workflow, not free-text notes:
- Driver License Status
- Driving Record Received
- Driving Record Approved
- Delivery Experience (Months)
- Age Verified (21+)
- High School Diploma/HSED
- Background Check Status
- Drug Test Status
- Can Lift 50 lbs
- Recruiter Qualification Decision

### Feature IDs
These IDs are referenced during implementation and testing:
- AIP-001 Import Applicant
- AIP-002 Duplicate Detection
- AIP-003 Resume Processing
- AIP-004 AI Review
- AIP-005 Recruiter Review
- AIP-006 Phone Interview
- AIP-007 Submit to USPS
- AIP-008 USPS Review Tracking
- AIP-009 Reporting
- AIP-010 Audit Logging

## 5. Non-Functional Requirements
- Availability: intake and review workflows must be available during recruiter operating hours.
- Performance: newly submitted Wix applications should be visible in RecruitOS within operationally acceptable latency.
- Reliability: accepted applicant records must persist without data loss.
- Observability: pipeline stage changes and processing failures must be traceable.
- Scalability: design must support growth in applicant volume across multiple USPS requisitions.
- Usability: recruiter screens must minimize clicks for review and stage advancement.
- Maintainability: services and entities should support extension for additional client workflows.

## 6. Applicant Pipeline Stages
The pipeline shall support these canonical stages:
1. Application Received
2. Imported
3. Resume Processing
4. AI Review Complete
5. Recruiter Review
6. Phone Interview
7. Submitted to USPS
8. USPS Review
9. Offer
10. Hired

Each stage transition shall capture timestamp, actor, and reason code (where applicable).

## 7. Data Flow
1. Applicant submits Wix form on greaterconnect.com.
2. Intake connector retrieves new applications.
3. Intake service validates and normalizes inbound data.
4. Candidate profile is created and assigned to initial stage.
5. Resume parser extracts structured data and enriches profile.
6. AI service generates recruiter-facing summary.
7. Recruiter reviews candidate and records phone interview result.
8. Recruiter submits qualified candidate to USPS.
9. USPS review decision is recorded.
10. Offer and hire outcomes are finalized and logged.

## 8. Required Database Entities
- Organization: top-level tenant boundary.
- User: authenticated user account within an organization.
- Role: authorization role for access and workflow control.
- Client: customer account under an organization.
- JobOrder: requisition under a client.
- Applicant: core candidate identity and contact data.
- ApplicationSource: source metadata (greaterconnect.com, Wix form identifiers).
- ResumeDocument: resume file/text metadata and parse status.
- ResumeParseResult: structured extraction output and parser diagnostics.
- AICandidateSummary: generated summary, confidence indicators, and generation metadata.
- PipelineStageHistory: stage transitions with actor, timestamp, and reason.
- RecruiterReview: recruiter decision notes and review outcomes.
- PhoneInterview: interview date, interviewer, notes, disposition.
- ClientSubmission: submission payload, submitted timestamp, submission status.
- ClientReviewOutcome: USPS review decisions, comments, and dates.
- OfferRecord: offer status and key terms snapshot.
- HireRecord: hire confirmation and effective date.
- ValidationIssue: field-level validation issues and resolution state.
- ActivityLog: immutable operational audit events.

Required hierarchy:
Organization
	↓
Client
	↓
JobOrder
	↓
Applicant

Every Applicant record shall contain `organization_id`, `client_id`, and `job_order_id` to support future multi-tenant SaaS deployment.

## 9. Required Services
- Intake Connector Service: collects new applications from Wix source.
- Applicant Intake Service: validates, normalizes, and persists applicant data.
- Duplicate Detection Service: evaluates candidate collision risk.
- Resume Processing Service: stores and parses resume artifacts.
- AI Summary Service: generates structured recruiter summary.
- Pipeline Orchestration Service: enforces stage transitions and business rules.
- Recruiter Workflow Service: supports review, interview, and client submission actions.
- Client Outcome Service: records USPS review, offer, and hire outcomes.
- Reporting Service: aggregates funnel and operational metrics.
- Audit Logging Service: records immutable event history.

## 10. Required Desktop UI Screens
- Recruiter Dashboard: displays Today's Applicants, Waiting for Review, Phone Interviews, Submitted to USPS, Offers, Hires, AI Alerts, Recruiter Tasks, and Notifications.
- Intake Queue Screen: newly imported applicants and processing state.
- Candidate Review Screen: candidate profile, parsed resume, AI summary, and validation issues.
- Interview Screen: phone interview scheduling metadata and interview outcome capture.
- Submission Screen: USPS submission preparation and confirmation.
- Pipeline Board/List Screen: stage-based view of candidate progression.
- Candidate Detail Timeline Screen: chronological history of key events.
- Reporting Dashboard Screen: stage conversion metrics and recruiter productivity indicators.
- Error Resolution Screen: intake/parsing exceptions with remediation actions.

## 11. AI Responsibilities
- Resume Summary
- Candidate Strengths
- Potential Concerns
- Missing Information
- Qualification Checklist
- Suggested Interview Questions
- Suggested Recruiter Notes
- Suggested Follow-up Email
- Highlight role alignment signals for Rural Carrier Associate / Delivery Driver criteria.
- Provide explainable summary components with source references to applicant data fields.

AI never makes hiring decisions.
Recruiters always make hiring decisions.

## 12. Recruiter Responsibilities
- Review candidate profile completeness and AI summary quality.
- Conduct phone interviews and record objective outcomes.
- Resolve duplicate and validation conflicts.
- Determine whether to submit candidates to USPS.
- Maintain accurate notes and stage progression updates.
- Confirm final offer/hire status when provided by USPS.

## 13. Validation Rules
- Required identity/contact fields must be present before profile creation.
- Email and phone fields must pass format validation.
- Source records must include traceable external submission identifiers.
- Duplicate checks must run before advancing beyond Imported to RecruitOS stage.
- Candidates cannot be moved to Submitted to USPS without completed recruiter review.
- Candidates cannot move to Offer without USPS review outcome.
- Candidates cannot move to Hired without offer state present.

## 14. Reporting Requirements
- Intake Volume: applications received by day/week/month.
- Source Quality: accepted vs rejected records from Wix source.
- Pipeline Conversion: stage-to-stage conversion rates.
- Time-in-Stage: median and percentile durations per stage.
- Recruiter Throughput: reviewed, interviewed, and submitted counts per recruiter.
- USPS Outcomes: review pass rate, offer rate, and hire rate.
- Exception Metrics: duplicate incidence, parse failures, validation errors.

## 15. Audit Logging Requirements
- Log all stage transitions with actor, timestamp, and prior/new state.
- Log all recruiter actions that alter candidate disposition.
- Log all AI summary generation events with model/version metadata.
- Log all validation and duplicate resolution decisions.
- Preserve immutable event history for compliance and post-incident analysis.
- Support filtered retrieval by candidate, date range, actor, and event type.

## 16. Security Requirements
- Enforce role-based access for recruiter and manager capabilities.
- Protect applicant PII in transit and at rest.
- Restrict access to client submission and outcome records by role.
- Maintain least-privilege service permissions for ingestion and processing components.
- Require authenticated sessions for all desktop workflow actions.
- Log security-relevant events such as failed access attempts and privilege-sensitive actions.

## 17. Acceptance Criteria
- Applications submitted through greaterconnect.com Wix forms appear in intake queue with source traceability.
- Resume parsing completes with visible status and extracted fields for recruiter review.
- AI summary is generated and displayed on candidate review screen.
- Recruiter can complete phone interview step and advance qualified candidates.
- Recruiter can submit candidate to USPS and system records submission metadata.
- USPS review outcomes can be captured and reflected in pipeline stages.
- Offer and hire states can be recorded with complete timeline history.
- Reporting surfaces core funnel and exception metrics.
- Audit logs show end-to-end candidate lifecycle events.

## 18. Future Enhancements
- Multi-client tenant support beyond USPS.
- Configurable pipeline templates by role and client.
- Bi-directional client portal integrations for submission and feedback.
- Automated interview scheduling integrations.
- Advanced AI screening explainability and bias monitoring controls.
- SLA alerting for stalled candidates and aging pipeline stages.
- Mobile recruiter companion views for field operations.

## Change Log
- 2.0 (2026-07-02): Replaced initial draft with Version 2 engineering specification for Greater Connections Staffing and USPS applicant intake workflow.

## Sprint 1 Implementation Stories
- Story 1.1 Organization Foundation
- Story 1.2 Client Management
- Story 1.3 Job Orders
- Story 1.4 Applicant Management
- Story 1.5 Applicant Intake Service
- Story 1.6 Recruiter Dashboard
- Story 1.7 Recruiter Workflow
