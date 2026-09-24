from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from api.schemas.applicants import ApplicantListResponse, ApplicantResponse
from api.schemas.responses import ErrorResponse
from database.connection import get_session
from models.applicant import Applicant
from services.applicant_service import ApplicantService
from utils.exceptions import BlackcrestError, BlackcrestNotFoundError

router = APIRouter(prefix="/applicants", tags=["applicants"])


def get_applicant_service() -> ApplicantService:
	"""Provide the applicant service for dependency injection."""
	return ApplicantService(session=get_session())


def _serialize_applicant(applicant: Applicant) -> ApplicantResponse:
	return ApplicantResponse.model_validate(applicant, from_attributes=True)


def _serialize_applicants(applicants: list[Applicant]) -> ApplicantListResponse:
	return ApplicantListResponse(root=[_serialize_applicant(applicant) for applicant in applicants])


def _error_response(status_code: int, detail: str) -> JSONResponse:
	return JSONResponse(status_code=status_code, content=ErrorResponse(detail=detail).model_dump())


def _handle_unexpected_error(exc: Exception) -> JSONResponse:
	return _error_response(status.HTTP_500_INTERNAL_SERVER_ERROR, "Applicant lookup failed")


@router.get(
	"/",
	response_model=ApplicantListResponse,
	responses={
		status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
	},
	summary="List applicants",
)
def list_applicants(
	service: Annotated[ApplicantService, Depends(get_applicant_service)],
) -> ApplicantListResponse | JSONResponse:
	try:
		applicants = service.list_applicants()
		return _serialize_applicants(applicants)
	except BlackcrestError:
		return _error_response(status.HTTP_500_INTERNAL_SERVER_ERROR, "Applicant lookup failed")
	except Exception:
		return _handle_unexpected_error(Exception())


@router.get(
	"/{applicant_id}",
	response_model=ApplicantResponse,
	responses={
		status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
		status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
	},
	summary="Get applicant",
)
def get_applicant(
	applicant_id: int,
	service: Annotated[ApplicantService, Depends(get_applicant_service)],
) -> ApplicantResponse | JSONResponse:
	try:
		applicant = service.get_applicant(applicant_id)
		if applicant is None:
			return _error_response(status.HTTP_404_NOT_FOUND, f"Applicant not found: {applicant_id}")
		return _serialize_applicant(applicant)
	except BlackcrestNotFoundError:
		return _error_response(status.HTTP_404_NOT_FOUND, f"Applicant not found: {applicant_id}")
	except BlackcrestError:
		return _error_response(status.HTTP_500_INTERNAL_SERVER_ERROR, "Applicant lookup failed")
	except Exception:
		return _handle_unexpected_error(Exception())