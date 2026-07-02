from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.applicant_importer import ApplicantImporter


def main() -> None:
    """Minimal demonstration of importing sample applicant data from CSV."""
    csv_path = Path(__file__).with_name("sample_applicants.csv")
    database_path = Path(__file__).with_name("demo_applicants.db")

    importer = ApplicantImporter(database_url=f"sqlite:///{database_path}")
    results = importer.import_from_csv(csv_path)

    print("Imported count:", results["imported_count"])
    print("Skipped count:", results["skipped_count"])
    print("Duplicate count:", results["duplicate_count"])
    if results["errors"]:
        print("Errors:")
        for error in results["errors"]:
            print("-", error)


if __name__ == "__main__":
    main()
