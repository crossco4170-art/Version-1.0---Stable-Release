from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime

from utils.exceptions import BlackcrestInputError


@dataclass(slots=True)
class ResumeProfile:
    """Structured applicant profile extracted from resume text."""

    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    city: str | None = None
    state: str | None = None
    skills: list[str] = field(default_factory=list)
    employers: list[str] = field(default_factory=list)
    job_titles: list[str] = field(default_factory=list)
    employment_dates: list[str] = field(default_factory=list)
    years_experience: int = 0
    education: list[str] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)
    licenses: list[str] = field(default_factory=list)
    delivery_experience: bool = False
    management_experience: bool = False
    cdl: bool = False
    military: bool = False


class ResumeParser:
    """Deterministic, offline parser for extracting recruiting signals from resumes."""

    _EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
    _PHONE_PATTERN = re.compile(r"(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}")
    _YEAR_PATTERN = re.compile(r"\b(19\d{2}|20\d{2})\b")
    _EXPERIENCE_PATTERN = re.compile(r"\b(\d{1,2})\+?\s+years?\b", re.IGNORECASE)

    _KNOWN_SKILLS = (
        "python",
        "sql",
        "excel",
        "forklift",
        "logistics",
        "warehouse",
        "route planning",
        "dispatch",
        "customer service",
        "leadership",
        "team management",
        "inventory",
        "safety compliance",
        "dot compliance",
        "power bi",
        "tableau",
    )

    _JOB_TITLE_HINTS = (
        "manager",
        "supervisor",
        "coordinator",
        "driver",
        "associate",
        "specialist",
        "technician",
        "analyst",
        "recruiter",
        "director",
        "lead",
    )

    def parse(self, resume_text: str) -> ResumeProfile:
        if not isinstance(resume_text, str):
            raise BlackcrestInputError("Resume text must be a string")

        cleaned = resume_text.strip()
        if not cleaned:
            return ResumeProfile()

        lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
        lower_text = cleaned.lower()

        profile = ResumeProfile(
            full_name=self._extract_full_name(lines),
            email=self._extract_email(cleaned),
            phone=self._extract_phone(cleaned),
            city=None,
            state=None,
        )

        profile.city, profile.state = self._extract_city_state(lines, cleaned)
        profile.skills = self._extract_skills(lines, lower_text)
        profile.education = self._extract_education(lines)
        profile.certifications = self._extract_certifications(lines)
        profile.licenses = self._extract_licenses(lines)
        profile.employers, profile.job_titles, profile.employment_dates = self._extract_employment(lines, cleaned)
        profile.years_experience = self._extract_years_experience(cleaned, profile.employment_dates)

        profile.delivery_experience = self._contains_any(
            lower_text,
            "delivery",
            "courier",
            "route",
            "last-mile",
            "last mile",
            "logistics",
            "package handling",
        )
        profile.management_experience = self._contains_any(
            lower_text,
            "manager",
            "managed",
            "management",
            "supervisor",
            "team lead",
            "director",
        )
        profile.cdl = self._contains_any(lower_text, "cdl", "commercial driver license")
        profile.military = self._contains_any(
            lower_text,
            "military",
            "veteran",
            "army",
            "navy",
            "air force",
            "marine corps",
            "marines",
            "coast guard",
        )

        return profile

    def _extract_full_name(self, lines: list[str]) -> str | None:
        for line in lines[:5]:
            match = re.match(r"^(?:name)\s*:\s*(.+)$", line, flags=re.IGNORECASE)
            if match:
                candidate = match.group(1).strip()
                return candidate if self._looks_like_name(candidate) else None

        for line in lines[:8]:
            if self._looks_like_name(line):
                return line
        return None

    def _extract_email(self, text: str) -> str | None:
        match = self._EMAIL_PATTERN.search(text)
        return match.group(0).lower() if match else None

    def _extract_phone(self, text: str) -> str | None:
        match = self._PHONE_PATTERN.search(text)
        return match.group(0).strip() if match else None

    def _extract_city_state(self, lines: list[str], text: str) -> tuple[str | None, str | None]:
        for line in lines:
            city_state_match = re.search(
                r"\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\s*,\s*([A-Z]{2})\b",
                line,
            )
            if city_state_match:
                return city_state_match.group(1).strip(), city_state_match.group(2).strip()

            location_match = re.match(
                r"^(?:location|city)\s*:\s*([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)(?:\s*,\s*([A-Z]{2}))?",
                line,
                flags=re.IGNORECASE,
            )
            if location_match:
                city = location_match.group(1).strip()
                state = location_match.group(2).strip() if location_match.group(2) else None
                return city, state

        compact_match = re.search(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*,\s*([A-Z]{2})\b", text)
        if compact_match:
            return compact_match.group(1).strip(), compact_match.group(2).strip()

        return None, None

    def _extract_skills(self, lines: list[str], lower_text: str) -> list[str]:
        collected: list[str] = []

        for line in lines:
            match = re.match(r"^(?:skills?|technical skills?)\s*:\s*(.+)$", line, flags=re.IGNORECASE)
            if match:
                for token in re.split(r",|\|", match.group(1)):
                    cleaned = token.strip()
                    if cleaned:
                        collected.append(cleaned)

        for skill in self._KNOWN_SKILLS:
            if skill in lower_text:
                collected.append(skill.title())

        return self._unique_preserve_order(collected)

    def _extract_education(self, lines: list[str]) -> list[str]:
        results: list[str] = []
        for line in lines:
            if re.match(r"^(?:education)\s*:\s*(.+)$", line, flags=re.IGNORECASE):
                value = line.split(":", 1)[1].strip()
                if value:
                    results.append(value)
                continue
            if self._contains_any(
                line.lower(),
                "university",
                "college",
                "bachelor",
                "master",
                "associate",
                "high school",
                "mba",
                "b.s.",
                "b.a.",
                "m.s.",
                "diploma",
            ):
                results.append(line)
        return self._unique_preserve_order(results)

    def _extract_certifications(self, lines: list[str]) -> list[str]:
        results: list[str] = []
        for line in lines:
            match = re.match(r"^(?:certifications?|certificates?)\s*:\s*(.+)$", line, flags=re.IGNORECASE)
            if match:
                tokens = re.split(r",|\|", match.group(1))
                results.extend([token.strip() for token in tokens if token.strip()])
                continue
            if "certified" in line.lower() or "certification" in line.lower():
                results.append(line)
        return self._unique_preserve_order(results)

    def _extract_licenses(self, lines: list[str]) -> list[str]:
        results: list[str] = []
        for line in lines:
            match = re.match(r"^(?:licenses?|license)\s*:\s*(.+)$", line, flags=re.IGNORECASE)
            if match:
                tokens = re.split(r",|\|", match.group(1))
                results.extend([token.strip() for token in tokens if token.strip()])
                continue
            if "license" in line.lower() or "licensed" in line.lower() or "cdl" in line.lower():
                results.append(line)
        return self._unique_preserve_order(results)

    def _extract_employment(self, lines: list[str], text: str) -> tuple[list[str], list[str], list[str]]:
        employers: list[str] = []
        job_titles: list[str] = []
        employment_dates: list[str] = []

        for line in lines:
            if re.match(r"^(?:employer|company)\s*:\s*(.+)$", line, flags=re.IGNORECASE):
                employers.append(line.split(":", 1)[1].strip())

            if re.match(r"^(?:title|job title|position)\s*:\s*(.+)$", line, flags=re.IGNORECASE):
                job_titles.append(line.split(":", 1)[1].strip())

            combined_match = re.match(r"^(.+?)\s+-\s+(.+?)\s*\((.+)\)$", line)
            if combined_match:
                possible_title = combined_match.group(1).strip()
                possible_employer = combined_match.group(2).strip()
                possible_date = combined_match.group(3).strip()

                if self._looks_like_job_title(possible_title):
                    job_titles.append(possible_title)
                employers.append(possible_employer)
                employment_dates.append(possible_date)

            date_matches = re.findall(
                r"\b(?:19\d{2}|20\d{2})\s*[-/]\s*(?:present|current|19\d{2}|20\d{2})\b",
                line,
                flags=re.IGNORECASE,
            )
            for match in date_matches:
                employment_dates.append(match)

        for line in lines:
            if self._looks_like_job_title(line):
                job_titles.append(line)

        if not employment_dates:
            inline_dates = re.findall(
                r"\b(?:19\d{2}|20\d{2})\s*[-/]\s*(?:present|current|19\d{2}|20\d{2})\b",
                text,
                flags=re.IGNORECASE,
            )
            employment_dates.extend(inline_dates)

        return (
            self._unique_preserve_order([e for e in employers if e]),
            self._unique_preserve_order([t for t in job_titles if t]),
            self._unique_preserve_order([d for d in employment_dates if d]),
        )

    def _extract_years_experience(self, text: str, employment_dates: list[str]) -> int:
        explicit_years = [int(match) for match in self._EXPERIENCE_PATTERN.findall(text)]
        explicit = max(explicit_years) if explicit_years else 0

        derived = 0
        current_year = datetime.now(UTC).year
        for date_span in employment_dates:
            years = [int(value) for value in self._YEAR_PATTERN.findall(date_span)]
            if not years:
                continue
            start_year = min(years)
            end_year = max(years)
            if re.search(r"present|current", date_span, flags=re.IGNORECASE):
                end_year = max(end_year, current_year)
            if end_year >= start_year:
                derived = max(derived, end_year - start_year)

        return max(explicit, derived)

    def _contains_any(self, text: str, *terms: str) -> bool:
        lowered = text.lower()
        return any(term.lower() in lowered for term in terms)

    def _looks_like_name(self, candidate: str) -> bool:
        if not candidate or len(candidate) > 80:
            return False
        if any(char.isdigit() for char in candidate):
            return False
        tokens = [token for token in re.split(r"\s+", candidate.strip()) if token]
        if len(tokens) < 2 or len(tokens) > 4:
            return False
        disallowed = {
            "resume",
            "experience",
            "education",
            "skills",
            "summary",
            "objective",
            "certifications",
            "licenses",
        }
        return all(token.lower().strip(",:") not in disallowed for token in tokens)

    def _looks_like_job_title(self, line: str) -> bool:
        lowered = line.lower()
        if len(line) > 120:
            return False
        return any(hint in lowered for hint in self._JOB_TITLE_HINTS)

    def _unique_preserve_order(self, items: list[str]) -> list[str]:
        seen: set[str] = set()
        output: list[str] = []
        for item in items:
            cleaned = item.strip()
            if not cleaned:
                continue
            key = cleaned.lower()
            if key in seen:
                continue
            seen.add(key)
            output.append(cleaned)
        return output
