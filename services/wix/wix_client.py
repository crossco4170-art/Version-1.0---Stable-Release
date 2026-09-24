from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from config.secrets import get_optional, validate_required
from config.settings import Settings, get_settings
from utils.exceptions import BlackcrestConfigError, BlackcrestIntegrationError, BlackcrestInputError


class WixClient:
    """Structured Wix API client backed by environment-loaded configuration."""

    BASE_URL = "https://www.wixapis.com"
    REQUIRED_SECRET_NAMES = (
        "WIX_API_KEY",
        "WIX_SITE_ID",
        "WIX_ACCOUNT_ID",
        "WIX_WEBHOOK_SECRET",
    )

    def __init__(
        self,
        *,
        settings: Settings | None = None,
        urlopen_fn: Callable[..., Any] | None = None,
    ) -> None:
        self.settings = settings or get_settings(validate_required=False)
        self.urlopen_fn = urlopen_fn or urlopen

        self.wix_api_key = str(get_optional("WIX_API_KEY", self.settings.wix_api_key) or "")
        self.wix_site_id = str(get_optional("WIX_SITE_ID", self.settings.wix_site_id) or "")
        self.wix_account_id = str(get_optional("WIX_ACCOUNT_ID", self.settings.wix_account_id) or "")
        self.wix_webhook_secret = str(get_optional("WIX_WEBHOOK_SECRET", self.settings.wix_webhook_secret) or "")

        self.missing_required_secrets = self._find_missing_required_secrets()

    def health_check(self) -> dict[str, object]:
        if self.missing_required_secrets:
            return {
                "ok": False,
                "service": "wix",
                "missing_required_secrets": list(self.missing_required_secrets),
            }

        site_info = self.get_site_info()
        return {
            "ok": True,
            "service": "wix",
            "site_id": self.wix_site_id,
            "site_name": site_info.get("site_name", ""),
        }

    def get_site_info(self) -> dict[str, object]:
        self._ensure_credentials()
        payload = self._request_json("GET", f"{self.BASE_URL}/site-properties/v4/properties")
        site_info = payload.get("properties", payload)
        if not isinstance(site_info, dict):
            raise BlackcrestIntegrationError("Wix site info response is invalid")
        return {
            "site_id": str(site_info.get("siteId", self.wix_site_id)),
            "site_name": str(site_info.get("displayName", "")),
            "raw": dict(site_info),
        }

    def list_forms(self) -> list[dict[str, object]]:
        self._ensure_credentials()
        payload = self._request_json("GET", f"{self.BASE_URL}/forms/v4/forms")
        forms = payload.get("forms", [])
        if not isinstance(forms, list):
            raise BlackcrestIntegrationError("Wix forms response is invalid")
        return [dict(item) for item in forms if isinstance(item, dict)]

    def get_form(self, form_id: str) -> dict[str, object]:
        if not form_id or not form_id.strip():
            raise BlackcrestInputError("form_id is required")

        self._ensure_credentials()
        payload = self._request_json("GET", f"{self.BASE_URL}/forms/v4/forms/{form_id.strip()}")
        form = payload.get("form", payload)
        if not isinstance(form, dict):
            raise BlackcrestIntegrationError("Wix form response is invalid")
        return dict(form)

    def download_file(self, file_url: str) -> bytes:
        if not file_url or not file_url.strip():
            raise BlackcrestInputError("file_url is required")

        self._ensure_credentials()
        request = Request(file_url.strip(), headers=self._build_headers())
        try:
            with self.urlopen_fn(request, timeout=30) as response:
                content = response.read()
        except HTTPError as exc:
            raise BlackcrestIntegrationError(f"Wix file download failed with status {exc.code}") from exc
        except URLError as exc:
            raise BlackcrestIntegrationError(f"Wix file download failed: {exc.reason}") from exc

        if not isinstance(content, bytes):
            raise BlackcrestIntegrationError("Wix file download returned invalid content")
        return content

    def verify_webhook(self, signature: str, body: bytes | str) -> bool:
        self._ensure_credentials()
        body_bytes = body.encode("utf-8") if isinstance(body, str) else body
        computed = hmac.new(
            self.wix_webhook_secret.encode("utf-8"),
            body_bytes,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(signature.strip().lower(), computed.lower())

    def _request_json(self, method: str, url: str) -> dict[str, object]:
        request = Request(url, method=method.upper(), headers=self._build_headers())
        try:
            with self.urlopen_fn(request, timeout=30) as response:
                payload = response.read().decode("utf-8")
        except HTTPError as exc:
            raise BlackcrestIntegrationError(f"Wix API request failed with status {exc.code}") from exc
        except URLError as exc:
            raise BlackcrestIntegrationError(f"Wix API request failed: {exc.reason}") from exc

        try:
            decoded = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise BlackcrestIntegrationError("Wix API returned invalid JSON") from exc

        if not isinstance(decoded, dict):
            raise BlackcrestIntegrationError("Wix API returned an unexpected payload")
        return decoded

    def _build_headers(self) -> dict[str, str]:
        return {
            "Authorization": self.wix_api_key,
            "wix-site-id": self.wix_site_id,
            "wix-account-id": self.wix_account_id,
            "Accept": "application/json",
        }

    def _ensure_credentials(self) -> None:
        if self.missing_required_secrets:
            raise BlackcrestConfigError(
                "Missing required Wix configuration: " + ", ".join(self.missing_required_secrets)
            )

    def _find_missing_required_secrets(self) -> list[str]:
        try:
            validate_required(*self.REQUIRED_SECRET_NAMES)
        except BlackcrestConfigError:
            pass

        mapping = {
            "WIX_API_KEY": self.wix_api_key,
            "WIX_SITE_ID": self.wix_site_id,
            "WIX_ACCOUNT_ID": self.wix_account_id,
            "WIX_WEBHOOK_SECRET": self.wix_webhook_secret,
        }
        return [name for name, value in mapping.items() if not value.strip()]