from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any

from database.init_db import initialize_database
from services.applicant_service import ApplicantService
from utils.exceptions import BlackcrestInputError


class ApplicantImporter:
    """Minimal CSV importer for applicant records with validation and normalization."""

    def __init__(self, database_url: str | None = None) -> None:
        initialize_database(database_url)
        self.service = ApplicantService(database_url=database_url)

    @staticmethod
    def _normalize_name(value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = re.sub(r"\s+", " ", value.strip())
        return cleaned.title() if cleaned else None

    @staticmethod
    def _normalize_phone(value: str | None) -> str | None:
        if value is None:
            return None
        digits = re.sub(r"\D", "", value)
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        if len(digits) >= 7:
            return digits
        return None

    @staticmethod
    def _normalize_email(value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip().lower()
        return cleaned if cleaned and "@" in cleaned else None

    @staticmethod
    def _normalize_text(value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned if cleaned else None

    @staticmethod
    def _normalize_score(value: str | None) -> float | None:
        if value is None or value.strip() == "":
            return None
        try:
            score = float(value)
        except ValueError as exc:
            raise BlackcrestInputError("Score must be numeric") from exc
        if score < 0 or score > 100:
            raise BlackcrestInputError("Score must be between 0 and 100")
        return score

    def _is_duplicate(self, email: str | None, phone: str | None) -> bool:
        if email:
            existing = self.service.search_applicants(email)
            if existing:
                return True
        if phone:
            existing = self.service.search_applicants(phone)
            if existing:
                return True
        return False

    def import_from_csv(self, csv_path: str | Path) -> dict[str, int | list[str]]:
        path = Path(csv_path)
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {path}")

        statistics: dict[str, int | list[str]] = {
            "imported_count": 0,
            "skipped_count": 0,
            "duplicate_count": 0,
            "errors": [],
        }

        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                try:
                    normalized = self._normalize_row(row)
                    if self._is_duplicate(normalized.get("email"), normalized.get("phone")):
                        statistics["duplicate_count"] = int(statistics["duplicate_count"]) + 1
                        statistics["skipped_count"] = int(statistics["skipped_count"]) + 1
                        statistics["errors"].append(
                            f"Duplicate row for {normalized.get('email') or normalized.get('phone')}"
                        )
                        continue

                    self.service.create_applicant(**normalized)
                    statistics["imported_count"] = int(statistics["imported_count"]) + 1
                except ValueError as exc:
                    statistics["skipped_count"] = int(statistics["skipped_count"]) + 1
                    statistics["errors"].append(str(exc))

        return statistics

    def _normalize_row(self, row: dict[str, Any]) -> dict[str, Any]:
        name = self._normalize_name(row.get("name"))
        if not name:
            raise BlackcrestInputError("Name is required")

        phone = self._normalize_phone(row.get("phone"))
        email = self._normalize_email(row.get("email"))
        if not email:
            raise BlackcrestInputError("Valid email is required")

        score = self._normalize_score(row.get("score"))

        return {
            "name": name,
            "phone": phone,
            "email": email,
            "address": self._normalize_text(row.get("address")),
            "drivers_license_status": self._normalize_text(row.get("drivers_license_status")),
            "experience": self._normalize_text(row.get("experience")),
            "resume_location": self._normalize_text(row.get("resume_location")),
            "current_status": self._normalize_text(row.get("current_status")),
            "notes": self._normalize_text(row.get("notes")),
            "score": score,
        }
