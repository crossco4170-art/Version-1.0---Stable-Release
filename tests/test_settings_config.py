from __future__ import annotations

import pytest

from config.secrets import get_required, mask_secret, validate_required
from config.settings import Settings
from utils.exceptions import BlackcrestConfigError


_ENV_KEYS = [
    "APP_NAME",
    "APP_ENV",
    "APP_VERSION",
    "DEBUG",
    "DATABASE_URL",
    "DATABASE_PATH",
    "WIX_API_KEY",
    "WIX_SITE_ID",
    "WIX_ACCOUNT_ID",
    "WIX_WEBHOOK_SECRET",
    "GOOGLE_CLIENT_ID",
    "GOOGLE_CLIENT_SECRET",
    "GOOGLE_REFRESH_TOKEN",
    "OPENAI_API_KEY",
    "LOG_LEVEL",
]


def _clear_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in _ENV_KEYS:
        monkeypatch.delenv(key, raising=False)



def test_settings_load_default_secure_placeholders(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_env(monkeypatch)

    settings = Settings(validate_required=False)

    assert settings.app_name == "BlackcrestRecruitOS"
    assert settings.app_env == "development"
    assert settings.app_version == "v2.0-shell"
    assert settings.debug is False
    assert settings.database_url == "sqlite:///./blackcrest.db"
    assert settings.wix_api_key == ""
    assert settings.google_client_id == ""
    assert settings.openai_api_key == ""
    assert settings.log_level == "INFO"



def test_settings_environment_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_env(monkeypatch)
    monkeypatch.setenv("APP_NAME", "RecruitOS V2")
    monkeypatch.setenv("APP_ENV", "testing")
    monkeypatch.setenv("APP_VERSION", "2.1.0")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./override.db")
    monkeypatch.setenv("WIX_API_KEY", "wix-key")
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "client-id")
    monkeypatch.setenv("OPENAI_API_KEY", "openai-key")
    monkeypatch.setenv("LOG_LEVEL", "debug")

    settings = Settings(validate_required=False)

    assert settings.app_name == "RecruitOS V2"
    assert settings.app_env == "testing"
    assert settings.app_version == "2.1.0"
    assert settings.debug is True
    assert settings.database_url == "sqlite:///./override.db"
    assert settings.wix_api_key == "wix-key"
    assert settings.google_client_id == "client-id"
    assert settings.openai_api_key == "openai-key"
    assert settings.log_level == "DEBUG"



def test_validate_required_returns_required_values(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_env(monkeypatch)
    monkeypatch.setenv("OPENAI_API_KEY", "secret-openai")
    monkeypatch.setenv("WIX_API_KEY", "secret-wix")

    values = validate_required("OPENAI_API_KEY", "WIX_API_KEY")

    assert values == {
        "OPENAI_API_KEY": "secret-openai",
        "WIX_API_KEY": "secret-wix",
    }



def test_mask_secret_hides_secret_content() -> None:
    assert mask_secret(None) is None
    assert mask_secret("") == ""
    assert mask_secret("abcd") == "****"
    assert mask_secret("abcdefghijkl") == "ab********kl"



def test_missing_required_values_raise_config_error(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_env(monkeypatch)

    with pytest.raises(BlackcrestConfigError):
        get_required("OPENAI_API_KEY")

    with pytest.raises(BlackcrestConfigError):
        validate_required("OPENAI_API_KEY", "WIX_API_KEY")
