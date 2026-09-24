from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class WixResume:
    file_id: str
    file_name: str
    file_url: str
    content_type: str = "application/octet-stream"
    size_bytes: int = 0

    def to_dict(self) -> dict[str, object]:
        return dict(asdict(self))

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "WixResume":
        return cls(
            file_id=str(payload.get("file_id", "")),
            file_name=str(payload.get("file_name", "")),
            file_url=str(payload.get("file_url", "")),
            content_type=str(payload.get("content_type", "application/octet-stream")),
            size_bytes=int(payload.get("size_bytes", 0) or 0),
        )


@dataclass(slots=True)
class WixApplicant:
    applicant_id: str
    form_id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    submitted_at: str = ""
    resume: WixResume | None = None
    raw_fields: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        payload = dict(asdict(self))
        payload["resume"] = self.resume.to_dict() if self.resume is not None else None
        payload["raw_fields"] = dict(self.raw_fields)
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "WixApplicant":
        resume_payload = payload.get("resume")
        resume = WixResume.from_dict(resume_payload) if isinstance(resume_payload, dict) else None
        return cls(
            applicant_id=str(payload.get("applicant_id", "")),
            form_id=str(payload.get("form_id", "")),
            first_name=str(payload.get("first_name", "")),
            last_name=str(payload.get("last_name", "")),
            email=str(payload.get("email", "")),
            phone=str(payload.get("phone", "")),
            submitted_at=str(payload.get("submitted_at", "")),
            resume=resume,
            raw_fields=dict(payload.get("raw_fields", {})),
        )


@dataclass(slots=True)
class WixWebhookEvent:
    event_type: str
    entity_id: str
    triggered_at: str
    signature: str
    payload: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        output = dict(asdict(self))
        output["payload"] = dict(self.payload)
        return output

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "WixWebhookEvent":
        return cls(
            event_type=str(payload.get("event_type", "")),
            entity_id=str(payload.get("entity_id", "")),
            triggered_at=str(payload.get("triggered_at", "")),
            signature=str(payload.get("signature", "")),
            payload=dict(payload.get("payload", {})),
        )