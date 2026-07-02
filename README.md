# BlackcrestRecruitOS

## Project Overview
BlackcrestRecruitOS is a modular recruiting platform focused on applicant lifecycle management, resume processing, AI-assisted evaluation, scheduling, notifications, and reporting. Version 1 is frozen as a stable baseline with secure first-run administrator setup, centralized configuration, and automated regression coverage.

## Folder Structure
Top-level folders and responsibilities:

- bots: Bot-related extension surface.
- config: Environment-backed settings and feature validation.
- database: SQLAlchemy base metadata, engine/session helpers, schema initialization.
- desktop: CustomTkinter dashboard.
- examples: Launchers, sample data, and runnable demos.
- logs: Runtime log output.
- models: ORM domain models.
- services: Business logic and integration workflows.
- templates: Template assets.
- tests: Automated regression suite.
- utils: Cross-cutting helpers (logging, datetime policy, passwords, exceptions).

## Installation
Prerequisites:

- Python 3.13 compatible environment
- Windows PowerShell, macOS Terminal, or Linux shell

Setup steps (Windows PowerShell example):

1. Create and activate a virtual environment.

       py -3.13 -m venv .venv
       .\.venv\Scripts\Activate.ps1

2. Upgrade packaging tools.

       python -m pip install --upgrade pip setuptools wheel

3. Install dependencies.

       pip install -r requirements.txt

4. Create a local environment file.

       Copy-Item .env.example .env

5. Update .env values before running in non-local environments.

## Configuration
Configuration is loaded from environment variables via config/settings.py and .env.

Core runtime settings:

- APP_NAME
- APP_ENV (development, testing, staging, production)
- DEBUG
- SECRET_KEY
- DATABASE_PATH
- LOG_LEVEL
- LOG_DIR

AI settings:

- OPENAI_API_KEY
- OPENAI_MODEL

Notification settings:

- GMAIL_USERNAME
- GMAIL_PASSWORD
- RECRUITER_NOTIFICATION_EMAILS
- SCORE_NOTIFICATION_THRESHOLD
- GMAIL_RETRY_ATTEMPTS
- GMAIL_RETRY_DELAY_SECONDS

Notes:

- Features validate required settings at usage time.
- Application startup supports reduced mode when optional integrations are not configured.

## Running The Application
Start the main application:

    python main.py

Start the desktop dashboard directly:

    python examples/launch_dashboard.py

On first launch with an empty database, administrator bootstrap prompts for secure credential creation.

## Running Tests
Run the full regression suite:

    python -m pytest -q

Current baseline after latest stabilization work: 38 passed.

## Dashboard
The desktop dashboard (desktop/recruiting_dashboard.py) provides:

- Applicant search and filtering
- Sortable applicant table
- Applicant detail panel
- Pipeline and summary statistics
- Report generation and export actions

## Resume Processing
Resume processing services support:

- Text extraction from PDF, DOCX, and TXT
- Structured field parsing (name, email, phone, sections)
- Candidate record persistence for processed resumes

Primary modules:

- services/resume_processor.py
- services/applicant_importer.py

## AI Evaluation
AI evaluation is handled by services/resume_evaluator.py:

- Sends structured prompts to OpenAI
- Normalizes response into summary, strengths, weaknesses, interview questions, and hiring suggestion
- Persists evaluation records and captures failure states gracefully

## Reporting
Reporting is handled by services/reporting_service.py:

- Daily, weekly, monthly summary reports
- Applicant pipeline report
- Export support for CSV, XLSX, and PDF

## Notifications
Notifications are handled by services/gmail_notification_service.py:

- Threshold-based recruiter alerts
- Gmail SMTP SSL delivery
- Retry logic with configurable delay
- Event hook compatibility via score event handling

## Known Limitations
- SQLite is the Version 1 persistence profile (single-node/local-first).
- Desktop-first delivery; no production web API surface in Version 1.
- Authentication scope is limited to first-run administrator bootstrap.
- Calendar integration is currently a provider protocol seam without bundled providers.
- Notification provider scope is Gmail SMTP.
- AI output quality and determinism depend on external model behavior.

## Future Roadmap
Version 2 direction includes:

- Full authentication and role-based access control
- Concrete calendar provider adapters (Google/Outlook)
- Expanded notification channels
- Web/API surface for multi-user workflows
- Background job orchestration
- Stronger schema migration/versioning workflow
- Expanded analytics and AI explainability

## Additional Documentation
- VERSION_1_RELEASE.md
- ARCHITECTURE.md
- CHANGELOG.md
