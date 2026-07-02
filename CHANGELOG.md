# Changelog

All notable changes to this project are documented in this file.

## [1.0.0] - 2026-07-01

### Release Type
- Version 1 freeze release.
- Documentation and stability baseline finalized.
- No behavior changes introduced as part of the freeze declaration.

### Added
- AI resume evaluation service with persisted evaluation records.
- Gmail threshold-based recruiter notification service with retry handling.
- Interview scheduling and rescheduling orchestration service.
- Reporting service for daily, weekly, monthly, and applicant pipeline summaries.
- CSV, XLSX, and PDF report export support.
- Desktop recruiting dashboard with search, filter, sorting, detail view, pipeline metrics, and reporting actions.
- Event hook seam for candidate score workflows.
- Applicant import and resume processing workflows.
- Secure first-run administrator bootstrap workflow.
- Password hashing and verification utility based on scrypt.

### Changed
- Centralized settings model expanded with feature-scoped validation interfaces.
- Database session lifecycle standardized through shared connection helpers.
- Datetime persistence policy standardized to UTC naive storage utilities.
- Application startup flow now includes database initialization and first-run admin bootstrap check.

### Security
- Removed insecure default administrator credential seeding.
- Enforced explicit first-run administrator creation when no admin exists.
- Persisted administrator credentials as salted scrypt hashes.

### Testing
- Regression suite status on release freeze: 32 passed, 0 failed.
- Test coverage includes settings, schema, services, scheduler, notifications, reporting, AI, datetime policy, importer/processor, and bootstrap security.

### Known Limitations
- SQLite persistence model for Version 1.
- Desktop-first operation without production API server.
- Gmail-only notification channel.
- Calendar provider implementation not bundled.
- Full RBAC and enterprise auth not yet implemented.

### Upgrade and Deployment Notes
- Use Python environment compatible with project requirements.
- Configure runtime and feature credentials in .env.
- Run tests before deployment promotion.
- Run application and complete first-run admin bootstrap if needed.

## [Unreleased]

### Planned for Version 2
- Full authentication and role-based authorization.
- Concrete calendar provider adapters.
- Expanded notification channels and provider abstraction.
- API/web delivery surface for multi-user workflows.
- Background job processing and advanced operational controls.
- Enhanced analytics, dashboards, and AI explainability.
