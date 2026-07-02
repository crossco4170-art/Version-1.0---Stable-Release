from __future__ import annotations

from datetime import UTC, datetime


def utc_now_naive() -> datetime:
    """Return current UTC time as a timezone-naive datetime for DB storage."""
    return datetime.now(UTC).replace(tzinfo=None)


def as_utc_naive(value: datetime) -> datetime:
    """Normalize datetime to UTC naive form for consistent storage and comparisons."""
    if value.tzinfo is None:
        return value
    return value.astimezone(UTC).replace(tzinfo=None)
