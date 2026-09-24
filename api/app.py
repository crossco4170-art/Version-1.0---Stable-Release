from __future__ import annotations

from fastapi import FastAPI

from config.settings import get_settings
from api.routes import api_router, health_router
from database.init_db import initialize_database

API_TITLE = "Blackcrest RecruitOS API"
API_VERSION = "2.0"


def create_app() -> FastAPI:
    """Build the FastAPI application for RecruitOS Version 2."""
    app = FastAPI(
        title=API_TITLE,
        version=API_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    app.include_router(api_router)
    app.include_router(health_router)

    @app.on_event("startup")
    def _startup_initialize_database() -> None:
        settings = get_settings(validate_required=False)
        initialize_database(settings.database_url)

    return app


app = create_app()