from __future__ import annotations

import importlib

import pytest

from config.settings import Settings, get_settings
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
    "OPENAI_MODEL",
    "GMAIL_USERNAME",
    "GMAIL_PASSWORD",
    "RECRUITER_NOTIFICATION_EMAILS",
    "LOG_LEVEL",
]


def _clear_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in _ENV_KEYS:
        monkeypatch.delenv(key, raising=False)



def test_settings_load_default_secure_placeholders(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_env(monkeypatch)

    settings = get_settings(validate_required=False)

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
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o")
    monkeypatch.setenv("LOG_LEVEL", "debug")

    settings = get_settings(validate_required=False)

    assert settings.app_name == "RecruitOS V2"
    assert settings.app_env == "testing"
    assert settings.app_version == "2.1.0"
    assert settings.debug is True
    assert settings.database_url == "sqlite:///./override.db"
    assert settings.wix_api_key == "wix-key"
    assert settings.google_client_id == "client-id"
    assert settings.openai_api_key == "openai-key"
    assert settings.openai_model == "gpt-4o"
    assert settings.log_level == "DEBUG"


def test_validate_feature_settings_uses_tracked_settings_api(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_env(monkeypatch)
    monkeypatch.setenv("OPENAI_API_KEY", "secret-openai")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")
    monkeypatch.setenv("GMAIL_USERNAME", "recruiter@example.com")
    monkeypatch.setenv("GMAIL_PASSWORD", "smtp-secret")
    monkeypatch.setenv("RECRUITER_NOTIFICATION_EMAILS", "team@example.com")

    settings = Settings(validate_required=False)

    settings.validate_openai_settings()
    settings.validate_gmail_settings(require_recipients=True)
    settings.validate_feature_settings("gmail", profiles=("with_recipients",))


def test_missing_required_values_raise_config_error(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_env(monkeypatch)

    settings = Settings(validate_required=False)

    with pytest.raises(BlackcrestConfigError):
        settings.validate_openai_settings()

    with pytest.raises(BlackcrestConfigError):
        settings.validate_gmail_settings()

    with pytest.raises(BlackcrestConfigError):
        settings.validate_feature_settings("gmail", profiles=("with_recipients",))


def test_package_import_smoke() -> None:
    config_package = importlib.import_module("config")
    settings_module = importlib.import_module("config.settings")
    database_package = importlib.import_module("database")
    init_db_module = importlib.import_module("database.init_db")

    assert config_package.Settings is settings_module.Settings
    assert config_package.get_settings is settings_module.get_settings
    assert database_package.initialize_database is init_db_module.initialize_database
