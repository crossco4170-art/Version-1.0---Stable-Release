from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from database.init_db import initialize_database
from services.applicant_service import ApplicantService
from utils.exceptions import BlackcrestDependencyError, BlackcrestInputError


class ResumeProcessor:
    """Parse resume files into structured fields and persist candidate summaries."""

    def __init__(self, database_url: str | None = None) -> None:
        initialize_database(database_url)
        self.service = ApplicantService(database_url=database_url)

    def process_resume(self, resume_path: str | Path) -> dict[str, Any]:
        path = Path(resume_path)
        if not path.exists():
            raise FileNotFoundError(f"Resume file not found: {path}")

        text = self._extract_text(path)
        data = self._parse_text(text)

        payload = {
            "name": data.get("name"),
            "phone": data.get("phone"),
            "email": data.get("email"),
            "experience": data.get("experience"),
            "skills": data.get("skills", []),
            "education": data.get("education", []),
            "employment_history": data.get("employment_history", []),
            "source_type": data.get("source_type", "text"),
            "raw_text": text,
        }

        self._store_result(payload)
        return payload

    def _extract_text(self, path: Path) -> str:
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            return self._extract_pdf_text(path)
        if suffix == ".docx":
            return self._extract_docx_text(path)
        if suffix == ".txt":
            try:
                return path.read_text(encoding="utf-8")
            except UnicodeDecodeError as exc:
                raise BlackcrestInputError(f"Unable to read text resume file: {path}") from exc
        raise BlackcrestInputError(
            f"Unsupported resume file type '{suffix or '<none>'}'. Only .pdf, .docx, and .txt files are supported."
        )

    def _extract_pdf_text(self, path: Path) -> str:
        try:
            import PyPDF2  # type: ignore
        except ImportError as exc:
            raise BlackcrestDependencyError(
                "PyPDF2 is required to process PDF resumes. Install it from requirements.txt."
            ) from exc

        try:
            reader = PyPDF2.PdfReader(str(path))
            pages = [page.extract_text() or "" for page in reader.pages]
            extracted = "\n".join(pages).strip()
        except Exception as exc:
            raise BlackcrestInputError(f"Unable to process PDF resume '{path}': {exc}") from exc

        if not extracted:
            raise BlackcrestInputError(f"No text could be extracted from PDF resume '{path}'.")
        return extracted

    def _extract_docx_text(self, path: Path) -> str:
        try:
            import docx  # type: ignore
        except ImportError as exc:
            raise BlackcrestDependencyError(
                "python-docx is required to process DOCX resumes. Install it from requirements.txt."
            ) from exc

        try:
            document = docx.Document(str(path))
            paragraphs = [paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()]
            extracted = "\n".join(paragraphs).strip()
        except Exception as exc:
            raise BlackcrestInputError(f"Unable to process DOCX resume '{path}': {exc}") from exc

        if not extracted:
            raise BlackcrestInputError(f"No text could be extracted from DOCX resume '{path}'.")
        return extracted

    def _parse_text(self, text: str) -> dict[str, Any]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        name = self._find_value(lines, ["name"])
        phone = self._find_phone(lines)
        email = self._find_email(lines)
        experience = self._find_section(lines, "experience")
        skills = self._find_list(lines, "skills")
        education = self._find_list(lines, "education")
        employment_history = self._find_list(lines, "employment history")

        if not name and lines:
            name = lines[0]

        return {
            "name": name,
            "phone": phone,
            "email": email,
            "experience": experience,
            "skills": skills,
            "education": education,
            "employment_history": employment_history,
            "source_type": "text",
        }

    def _find_value(self, lines: list[str], labels: list[str]) -> str | None:
        pattern = re.compile(rf"^(?:{'|'.join(labels)})\s*:\s*(.+)$", re.IGNORECASE)
        for line in lines:
            match = pattern.match(line)
            if match:
                return match.group(1).strip()
        return None

    def _find_phone(self, lines: list[str]) -> str | None:
        pattern = re.compile(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
        for line in lines:
            match = pattern.search(line)
            if match:
                return match.group(0)
        return None

    def _find_email(self, lines: list[str]) -> str | None:
        pattern = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
        for line in lines:
            match = pattern.search(line)
            if match:
                return match.group(0)
        return None

    def _find_section(self, lines: list[str], label: str) -> str | None:
        pattern = re.compile(rf"^{re.escape(label)}\s*:\s*(.+)$", re.IGNORECASE)
        for line in lines:
            match = pattern.match(line)
            if match:
                return match.group(1).strip()
        return None

    def _find_list(self, lines: list[str], label: str) -> list[str]:
        pattern = re.compile(rf"^{re.escape(label)}\s*:\s*(.+)$", re.IGNORECASE)
        for line in lines:
            match = pattern.match(line)
            if match:
                content = match.group(1).strip()
                return [item.strip() for item in content.split(",") if item.strip()]
        return []

    def _store_result(self, payload: dict[str, Any]) -> None:
        if not payload.get("name"):
            return

        self.service.create_applicant(
            name=payload["name"],
            phone=payload.get("phone"),
            email=payload.get("email"),
            experience=json.dumps(payload.get("employment_history", [])),
            notes=json.dumps(payload),
            current_status="resume_processed",
        )
