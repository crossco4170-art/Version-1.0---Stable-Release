# BlackcrestRecruitOS Version 1 Release

Release date: 2026-07-01
Release type: Version 1 freeze (documentation finalization, no behavior changes)

## Release Objective
This release freezes BlackcrestRecruitOS Version 1 as a stable baseline. The focus is preserving current behavior while publishing complete release documentation for operations, support, and future planning.

## Completed Features
- Core applicant lifecycle services for create, edit, list, and status tracking.
- Resume ingestion and processing support (PDF, DOCX, TXT) via importer and processor services.
- AI resume evaluation pipeline with persisted evaluation records and graceful API failure handling.
- Event hook boundary for candidate score events to decouple future integrations.
- Gmail notification service with threshold-based delivery, retries, and structured logging.
- Interview scheduling and rescheduling workflow with applicant status updates.
- Calendar integration protocol seam for future provider implementations.
- Reporting engine for daily, weekly, monthly, and pipeline reports.
- Multi-format report export support (CSV, XLSX, PDF).
- Desktop dashboard with filtering, sorting, details panel, pipeline view, summary statistics, and report actions.
- Centralized environment configuration with feature-scoped validation.
- Unified database session handling and schema initialization path.
- UTC datetime policy standardization for persisted application timestamps.
- Secure first-run administrator bootstrap with interactive setup and hashed password storage.
- Automated test coverage across configuration, services, reporting, scheduler, notifications, AI, datetime policy, importer, and bootstrap security.

## Folder Structure Overview
Top-level layout:

- bots: bot-related modules and extension surface.
- config: application settings and validation.
- database: SQLAlchemy base, connection/session, and schema initialization.
- desktop: CustomTkinter user interface.
- examples: runnable usage examples and demo assets.
- logs: runtime logs.
- models: ORM domain entities.
- services: business logic and integration services.
- templates: template assets.
- tests: automated test suite.
- utils: shared helpers (logging, datetime policy, password hashing).

## Technology Stack
- Language/runtime: Python (project target 3.13 compatibility).
- ORM/data: SQLAlchemy 2.x with SQLite.
- Configuration: pydantic-settings + python-dotenv.
- AI integration: OpenAI Python SDK.
- Notifications: smtplib with Gmail SMTP over SSL.
- Desktop UI: CustomTkinter.
- Report export: CSV (stdlib), openpyxl (XLSX), reportlab (PDF).
- Resume parsing: PyPDF2, python-docx.
- Quality/tooling: pytest, ruff, mypy.

## Configuration Requirements
Environment variables are loaded from .env using centralized settings.

Global runtime:
- APP_NAME
- APP_ENV (development, testing, staging, production)
- DEBUG
- SECRET_KEY
- DATABASE_PATH
- LOG_LEVEL
- LOG_DIR

AI feature requirements:
- OPENAI_API_KEY
- OPENAI_MODEL

Notification feature requirements:
- GMAIL_USERNAME
- GMAIL_PASSWORD
- RECRUITER_NOTIFICATION_EMAILS
- SCORE_NOTIFICATION_THRESHOLD
- GMAIL_RETRY_ATTEMPTS
- GMAIL_RETRY_DELAY_SECONDS

Notes:
- Version 1 supports startup in reduced mode when optional integration credentials are not configured.
- Feature-level validation is enforced at usage boundaries (for example, AI and Gmail services).

## Test Summary
Validation baseline for this freeze:
- Full regression suite executed on 2026-07-01.
- Result: 32 tests passed, 0 failed.
- Scope includes settings, database schema, services, scheduling, reporting, notifications, AI evaluation, datetime policy, import/processing, and admin bootstrap security.

## Security Features
- First-run administrator bootstrap requires explicit username and password when no admin exists.
- No insecure default administrator credentials are seeded.
- Administrator passwords are stored as scrypt hashes with per-password salt.
- Password verification uses constant-time comparison.
- Feature credentials are sourced from environment configuration, not hardcoded constants.
- Structured logging is available for startup and integration behavior observability.

## Known Limitations
- SQLite is used as the Version 1 persistence layer and is not a distributed multi-node database strategy.
- Desktop-first delivery; no production web API surface in Version 1.
- Authentication scope is limited to initial admin bootstrap, without full RBAC or SSO.
- Calendar integration is a protocol seam only; no built-in Google/Outlook adapter yet.
- Notification channel is Gmail SMTP only.
- AI output quality and determinism depend on external model behavior and prompt quality.
- Operational migrations/versioned schema evolution tooling is limited in Version 1.

## Deployment Checklist
- Confirm Python environment version and activate virtual environment.
- Install dependencies from requirements.txt.
- Copy .env.example to .env and replace all placeholder values.
- Set a non-default SECRET_KEY value.
- Set DATABASE_PATH to the intended persistent storage location.
- Configure OPENAI and Gmail variables only for features that will be enabled.
- Verify write permissions for database and logs directories.
- Run full tests before release promotion.
- Start the application with python main.py.
- Complete first-run admin bootstrap prompt if no admin account exists.
- Validate desktop dashboard launch using example launcher if required.
- Validate report export permissions for CSV/XLSX/PDF targets.
- Define backup and retention policy for database and logs.

## Version 2 Roadmap
- Introduce full authentication and role-based access control.
- Add concrete calendar provider integrations (Google/Outlook).
- Expand notification channels (email providers and chat/webhook options).
- Introduce web/API interface and multi-user workflow support.
- Add background job orchestration for long-running tasks.
- Strengthen schema migration/versioning workflow.
- Add richer analytics dashboards and historical trend reporting.
- Extend AI-assisted ranking and explainability capabilities.

## Freeze Statement
Version 1 is frozen as of this document date. This release documentation reflects the current implementation and does not introduce application behavior changes.
