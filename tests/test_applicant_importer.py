from pathlib import Path

from services.applicant_importer import ApplicantImporter
from services.applicant_service import ApplicantService


def test_applicant_importer_handles_valid_and_invalid_rows(tmp_path: Path) -> None:
    csv_path = tmp_path / "applicants.csv"
    csv_path.write_text(
        "name,phone,email,address,drivers_license_status,experience,resume_location,current_status,notes,score\n"
        "Jane Doe, (555) 123-4567, JANE@EXAMPLE.COM, 123 Main St, valid, 3 years, /tmp/jane.pdf, new, Great fit, 91\n"
        "Bad Row, , , , , , , , ,\n"
        "John Smith, 555-7654, john@example.com, 456 Oak Ave, valid, 2 years, /tmp/john.pdf, reviewed, , 88\n",
        encoding="utf-8",
    )

    importer = ApplicantImporter(database_url=f"sqlite:///{tmp_path / 'import.db'}")
    stats = importer.import_from_csv(csv_path)

    assert stats["imported_count"] == 2
    assert stats["skipped_count"] == 1
    assert stats["duplicate_count"] == 0

    service = ApplicantService(database_url=f"sqlite:///{tmp_path / 'import.db'}")
    applicants = service.list_applicants()
    assert len(applicants) == 2

    duplicate_stats = importer.import_from_csv(csv_path)
    assert duplicate_stats["imported_count"] == 0
    assert duplicate_stats["skipped_count"] == 3
    assert duplicate_stats["duplicate_count"] == 2
