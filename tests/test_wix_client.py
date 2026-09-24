from __future__ import annotations

import hashlib
import hmac
import json

import pytest

from config.settings import Settings
from services.wix import WixApplicant, WixClient, WixResume, WixWebhookEvent
from utils.exceptions import BlackcrestConfigError


class _FakeResponse:
    def __init__(self, payload: bytes) -> None:
        self._payload = payload

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False

    def read(self) -> bytes:
        return self._payload


def _clear_wix_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in ("WIX_API_KEY", "WIX_SITE_ID", "WIX_ACCOUNT_ID", "WIX_WEBHOOK_SECRET"):
        monkeypatch.delenv(key, raising=False)


def _build_client(monkeypatch: pytest.MonkeyPatch) -> WixClient:
    _clear_wix_env(monkeypatch)
    monkeypatch.setenv("WIX_API_KEY", "test-api-key")
    monkeypatch.setenv("WIX_SITE_ID", "site-123")
    monkeypatch.setenv("WIX_ACCOUNT_ID", "account-456")
    monkeypatch.setenv("WIX_WEBHOOK_SECRET", "secret-789")
    return WixClient(settings=Settings(validate_required=False))


def test_constructor_loads_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _build_client(monkeypatch)

    assert client.wix_api_key == "test-api-key"
    assert client.wix_site_id == "site-123"
    assert client.wix_account_id == "account-456"
    assert client.wix_webhook_secret == "secret-789"
    assert client.missing_required_secrets == []


def test_missing_credentials_are_recorded(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_wix_env(monkeypatch)
    client = WixClient(settings=Settings(validate_required=False))

    assert client.missing_required_secrets == [
        "WIX_API_KEY",
        "WIX_SITE_ID",
        "WIX_ACCOUNT_ID",
        "WIX_WEBHOOK_SECRET",
    ]

    with pytest.raises(BlackcrestConfigError):
        client.get_site_info()


def test_webhook_verification(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _build_client(monkeypatch)
    body = b'{"event":"form_submission"}'
    signature = hmac.new(b"secret-789", body, hashlib.sha256).hexdigest()

    assert client.verify_webhook(signature, body) is True
    assert client.verify_webhook("bad-signature", body) is False


def test_model_serialization() -> None:
    resume = WixResume(
        file_id="file-1",
        file_name="resume.pdf",
        file_url="https://cdn.example.com/resume.pdf",
        content_type="application/pdf",
        size_bytes=2048,
    )
    applicant = WixApplicant(
        applicant_id="app-1",
        form_id="form-1",
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
        phone="555-0100",
        submitted_at="2026-07-08T10:00:00Z",
        resume=resume,
        raw_fields={"city": "Milwaukee"},
    )
    event = WixWebhookEvent(
        event_type="form.submitted",
        entity_id="app-1",
        triggered_at="2026-07-08T10:00:00Z",
        signature="sig-123",
        payload={"formId": "form-1"},
    )

    assert WixResume.from_dict(resume.to_dict()) == resume
    assert WixApplicant.from_dict(applicant.to_dict()) == applicant
    assert WixWebhookEvent.from_dict(event.to_dict()) == event


def test_health_check_reports_missing_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_wix_env(monkeypatch)
    client = WixClient(settings=Settings(validate_required=False))

    result = client.health_check()

    assert result["ok"] is False
    assert result["service"] == "wix"
    assert "WIX_API_KEY" in result["missing_required_secrets"]


def test_health_check_uses_structured_site_info(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = json.dumps({"properties": {"siteId": "site-123", "displayName": "RecruitOS Site"}}).encode("utf-8")
    client = _build_client(monkeypatch)
    client.urlopen_fn = lambda request, timeout=30: _FakeResponse(payload)

    result = client.health_check()

    assert result == {
        "ok": True,
        "service": "wix",
        "site_id": "site-123",
        "site_name": "RecruitOS Site",
    }