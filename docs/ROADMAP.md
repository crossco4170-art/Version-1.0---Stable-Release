# Blackcrest RecruitOS Roadmap

## Vision
Blackcrest RecruitOS evolves from a stable Version 1 baseline into a multi-tenant recruiting platform with structured intake workflows, organization-aware data ownership, and production-ready operations.

## Current Release Focus
- Harden multi-tenant ownership across applicant intake and lifecycle workflows.
- Keep service-layer behavior fully covered by milestone-level tests.
- Maintain green regression coverage while shipping each story in small commits.

## Milestone Status

### R2.1 Organization Foundation
- [x] Story 1.1A Organization Model
- [x] Story 1.1B Organization Service
- [x] Story 1.1C Organization Lifecycle

### R2.2 Client Management
- [x] Story 2.2A Client Model
- [x] Story 2.2B Client Service

### R2.3 Job Order Management
- [x] Story 2.3A Job Order Model
- [x] Story 2.3B Job Order Service
- [x] Story 2.3C Job Order Lifecycle

### R2.4 Applicant Intake Pipeline
- [x] Story 2.4A Applicant Model Integration
- [x] Story 2.4B Applicant Intake Service
- [x] Story 2.4C Wix Applicant Import Service
- [x] Story 2.4C.1 Applicant Composite Uniqueness (email + job_order_id)
- [ ] Story 2.4D AI Review
- [ ] Story 2.4E Recruiter Review
- [ ] Story 2.4F USPS Submission Workflow

## Next Milestones
### R2.5 Recruiter Workflow
- Recruiter tasking and review workflows
- Interview flow alignment
- Submission tracking to client

### R2.6 Reporting and Operations
- Tenant-aware reporting views
- Operational health checks and alerts
- Documentation and runbook updates

## Success Criteria
- Domain ownership enforced at organization boundaries.
- Lifecycle workflows covered by automated tests.
- Regression suite remains green for each milestone.
