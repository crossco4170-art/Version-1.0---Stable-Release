from __future__ import annotations

from fastapi import APIRouter

API_PREFIX = "/api/v1"

from api.routes._common import PlaceholderResponse, create_placeholder_router

from api.routes.applicants import router as applicants_router
from api.routes.clients import router as clients_router
from api.routes.health import router as health_router
from api.routes.interviews import router as interviews_router
from api.routes.job_orders import router as job_orders_router
from api.routes.organizations import router as organizations_router
from api.routes.reports import router as reports_router

api_router = APIRouter(prefix=API_PREFIX)
api_router.include_router(applicants_router)
api_router.include_router(organizations_router)
api_router.include_router(clients_router)
api_router.include_router(job_orders_router)
api_router.include_router(interviews_router)
api_router.include_router(reports_router)

__all__ = [
	"API_PREFIX",
	"PlaceholderResponse",
	"api_router",
	"applicants_router",
	"clients_router",
	"create_placeholder_router",
	"health_router",
	"interviews_router",
	"job_orders_router",
	"organizations_router",
	"reports_router",
]