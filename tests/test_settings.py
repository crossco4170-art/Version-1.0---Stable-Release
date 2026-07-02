import pytest

from config.settings import Settings, get_settings


def test_settings_loads_defaults_without_feature_credentials(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GMAIL_USERNAME", raising=False)
    monkeypatch.delenv("GMAIL_PASSWORD", raising=False)
    monkeypatch.setenv("DATABASE_PATH", "./tmp.db")
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("LOG_LEVEL", "INFO")

    settings = get_settings()

    assert settings.database_path == "./tmp.db"
    assert settings.openai_api_key == ""
    assert settings.gmail_username == ""


def test_feature_specific_validation_methods(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GMAIL_USERNAME", raising=False)
    monkeypatch.delenv("GMAIL_PASSWORD", raising=False)
    monkeypatch.delenv("RECRUITER_NOTIFICATION_EMAILS", raising=False)
    monkeypatch.setenv("DATABASE_PATH", "./tmp.db")
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("LOG_LEVEL", "INFO")

    settings = Settings(validate_required=False)

    with pytest.raises(ValueError):
        settings.validate_openai_settings()

    with pytest.raises(ValueError):
        settings.validate_gmail_settings()


def test_reusable_feature_validation_interface(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GMAIL_USERNAME", raising=False)
    monkeypatch.delenv("GMAIL_PASSWORD", raising=False)
    monkeypatch.delenv("RECRUITER_NOTIFICATION_EMAILS", raising=False)
    monkeypatch.setenv("DATABASE_PATH", "./tmp.db")
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("LOG_LEVEL", "INFO")

    settings = Settings(validate_required=False)

    with pytest.raises(ValueError):
        settings.validate_feature_settings("openai")

    with pytest.raises(ValueError):
        settings.validate_feature_settings("gmail")

    with pytest.raises(ValueError):
        settings.validate_feature_settings("gmail", profiles=("with_recipients",))

    with pytest.raises(ValueError):
        settings.validate_feature_settings("calendar")


def test_get_settings_uses_environment(monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", "./tmp.db")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("GMAIL_USERNAME", "user@example.com")
    monkeypatch.setenv("GMAIL_PASSWORD", "secret")
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("LOG_LEVEL", "INFO")

    settings = get_settings()

    assert settings.database_path == "./tmp.db"
    assert settings.openai_api_key == "test-openai-key"
    assert settings.gmail_username == "user@example.com"
    assert settings.gmail_password == "secret"
    assert settings.app_env == "development"
    assert settings.log_level == "INFO"
