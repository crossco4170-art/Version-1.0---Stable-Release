# Blackcrest Recruiting AI Architecture

Version: 1 (frozen)
Last updated: 2026-07-01

## System Architecture
Blackcrest Recruiting AI uses a modular, service-oriented Python architecture with a desktop UI, shared configuration boundary, SQLAlchemy data layer, and optional external integrations for AI and notifications.

Primary characteristics:
- Service layer boundaries around domain workflows.
- ORM-backed persistence with centralized session management.
- Feature-scoped configuration validation at runtime boundaries.
- Optional integration seams that fail safely when not configured.
- UTC timestamp policy for consistent persisted datetime behavior.

## High-Level Architecture Diagram
    +---------------------+
    |     Configuration   |
    |  config/settings.py |
    +----------+----------+
               |
               v
    +---------------------+          +----------------------+
    |     Desktop UI      |--------->|       Services       |
    | recruiting_dashboard|          | services/*.py        |
    +---------------------+          +----+---+---+----+----+
                                          |   |   |    |
                                          |   |   |    |
                                          |   |   |    +-------------------+
                                          |   |   |                        |
                                          v   v   v                        v
                                +-----------+ +-----------+       +----------------+
                                | Scheduling| | Reporting |       | Notifications  |
                                | interview | | reporting |       | Gmail SMTP     |
                                +-----+-----+ +-----+-----+       +--------+-------+
                                      |             |                       |
                                      |             |                       |
                                      v             v                       v
                                +--------------------------------------------------+
                                |                  Database                        |
                                | SQLite + SQLAlchemy models and sessions          |
                                +------------------------+-------------------------+
                                                         |
                                                         v
                                             +----------------------+
                                             |     AI Modules       |
                                             | resume evaluator     |
                                             | OpenAI integration   |
                                             +----------------------+

## Layer Breakdown
- Presentation layer
  - Desktop UI built with CustomTkinter for operator workflows.
  - UI delegates business operations to service interfaces.

- Application/service layer
  - Domain services implement applicant management, interview scheduling, reporting, notifications, resume processing, and bootstrap flows.
  - Services coordinate models, validation, and integration boundaries.

- Data layer
  - SQLAlchemy models define applicants, interviews, clients, job orders, admin users, status, logs, and resume evaluations.
  - Session access is centralized through database connection helpers.

- Integration layer
  - OpenAI client for resume evaluation.
  - Gmail SMTP for recruiter notifications.
  - Calendar provider protocol for future external calendar implementations.

- Configuration and cross-cutting layer
  - Environment-backed settings and validators.
  - Logging configuration.
  - Datetime policy utility and password hashing utility.

## Core Runtime Flow
- Startup flow
  - main.py loads settings and logging.
  - Database schema initialization runs.
  - First-run admin bootstrap runs only when no administrator exists.

- Applicant evaluation flow
  - Resume text is extracted/processed.
  - AI evaluator requests structured output from OpenAI.
  - Evaluation result is normalized and persisted.

- Notification flow
  - Candidate score events or direct applicant checks are evaluated against threshold.
  - Gmail settings and recipients are validated.
  - Message delivery retries are attempted with configured delay.

- Scheduling flow
  - Interview scheduler validates input and applicant existence.
  - Interview record is created or updated.
  - Applicant status is synchronized.
  - Optional calendar provider hook is invoked.

- Reporting flow
  - Reporting service aggregates applicants/interviews by period or pipeline.
  - Exports are generated to CSV, XLSX, or PDF.

## Folder Structure Overview
- config: settings model and validation logic.
- database: base metadata, engine/session helpers, initialization.
- models: ORM entities for recruiting domain.
- services: business and integration services.
- desktop: operational desktop dashboard.
- utils: shared policy and utility modules.
- tests: unit/integration-oriented regression coverage.
- examples: launchers and sample assets.

## Technology Stack
- Python, SQLAlchemy, SQLite.
- pydantic-settings and python-dotenv.
- OpenAI SDK.
- CustomTkinter.
- openpyxl and reportlab.
- PyPDF2 and python-docx.
- pytest, ruff, mypy.

## Configuration Requirements
Required by environment and feature usage:
- Core runtime: APP_ENV, DATABASE_PATH, LOG_LEVEL, LOG_DIR, SECRET_KEY.
- AI feature: OPENAI_API_KEY, OPENAI_MODEL.
- Notifications feature: GMAIL_USERNAME, GMAIL_PASSWORD, RECRUITER_NOTIFICATION_EMAILS, SCORE_NOTIFICATION_THRESHOLD, GMAIL_RETRY_ATTEMPTS, GMAIL_RETRY_DELAY_SECONDS.

## Security Features
- First-run administrator bootstrap with interactive credential capture.
- No default administrator credentials.
- Scrypt password hashing with salted hashes.
- Constant-time password hash verification.
- Environment-based secret and credential loading.

## Known Limitations
- Single-node SQLite deployment profile in Version 1.
- Desktop application interface only.
- Limited authentication scope beyond bootstrap.
- Calendar integration is interface-only (no bundled provider implementation).
- Notification provider scope is currently Gmail SMTP.
