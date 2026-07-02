from pathlib import Path

from database import initialize_database
from services.applicant_service import ApplicantService


def test_applicant_crud_and_search(tmp_path: Path) -> None:
    database_path = tmp_path / "applicants.db"
    initialize_database(str(database_path))

    service = ApplicantService(database_url=str(database_path))

    created = service.create_applicant(
        name="Jane Doe",
        phone="555-1234",
        email="jane@example.com",
        address="123 Main St",
        drivers_license_status="valid",
        experience="3 years",
        resume_location="/resumes/jane.pdf",
        current_status="new",
        notes="Strong candidate",
        score=91.5,
    )

    assert created.id is not None
    assert created.email == "jane@example.com"

    updated = service.edit_applicant(
        created.id,
        current_status="screened",
        notes="Updated note",
        score=95.0,
    )
    assert updated is not None
    assert updated.current_status == "screened"
    assert updated.notes == "Updated note"

    found = service.search_applicants("Jane")
    assert len(found) == 1

    all_applicants = service.list_applicants()
    assert len(all_applicants) == 1

    deleted = service.delete_applicant(created.id)
    assert deleted is True
    assert service.get_applicant(created.id) is None
