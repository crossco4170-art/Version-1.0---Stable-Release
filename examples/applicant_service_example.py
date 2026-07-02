from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from database import initialize_database
from services.applicant_service import ApplicantService


def main() -> None:
    """Minimal example showing the ApplicantService in action."""
    database_path = Path("./example_applicants.db")
    initialize_database(str(database_path))

    service = ApplicantService(database_url=str(database_path))

    created = service.create_applicant(
        name="Alice Johnson",
        phone="555-0100",
        email="alice@example.com",
        address="100 Main Street",
        drivers_license_status="valid",
        experience="5 years",
        resume_location="/tmp/alice.pdf",
        current_status="new",
        notes="Good fit",
        score=88.0,
    )
    print("Created applicant:", created.name, created.email)

    fetched = service.get_applicant(created.id)
    print("Retrieved applicant:", fetched.name if fetched else None)

    updated = service.edit_applicant(created.id, current_status="screened", notes="Updated note")
    print("Updated applicant status:", updated.current_status if updated else None)

    applicants = service.list_applicants()
    print("Applicant count:", len(applicants))

    deleted = service.delete_applicant(created.id)
    print("Deleted applicant:", deleted)


if __name__ == "__main__":
    main()
