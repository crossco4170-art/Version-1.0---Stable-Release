from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar

from dotenv import load_dotenv
from pydantic import Field, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from utils.exceptions import BlackcrestConfigError


load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")


class Settings(BaseSettings):
    """Centralized application settings loaded from environment variables."""

    FEATURE_REQUIREMENTS: ClassVar[dict[str, tuple[str, ...]]] = {
        "openai": ("openai_api_key", "openai_model"),
        "gmail": ("gmail_username", "gmail_password"),
    }

    FEATURE_OPTIONAL_REQUIREMENTS: ClassVar[dict[str, dict[str, tuple[str, ...]]]] = {
        "gmail": {
            "with_recipients": ("recruiter_notification_emails",),
        },
    }

    app_name: str = Field(default="Blackcrest Recruiting AI")
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=False)
    secret_key: str = Field(default="change-me")

    database_path: str = Field(default="./blackcrest.db", alias="DATABASE_PATH")
    database_url: str = Field(default="sqlite:///./blackcrest.db")

    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    gmail_username: str = Field(default="", alias="GMAIL_USERNAME")
    gmail_password: str = Field(default="", alias="GMAIL_PASSWORD")
    recruiter_notification_emails: str = Field(default="", alias="RECRUITER_NOTIFICATION_EMAILS")
    score_notification_threshold: float = Field(default=85.0, alias="SCORE_NOTIFICATION_THRESHOLD")
    gmail_retry_attempts: int = Field(default=3, alias="GMAIL_RETRY_ATTEMPTS")
    gmail_retry_delay_seconds: float = Field(default=2.0, alias="GMAIL_RETRY_DELAY_SECONDS")

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_dir: str = Field(default="logs", alias="LOG_DIR")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    @field_validator("app_env")
    @classmethod
    def validate_app_env(cls, value: str) -> str:
        allowed = {"development", "testing", "staging", "production"}
        if value not in allowed:
            raise BlackcrestConfigError(f"app_env must be one of {sorted(allowed)}")
        return value

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if value.upper() not in allowed:
            raise BlackcrestConfigError(f"log_level must be one of {sorted(allowed)}")
        return value.upper()

    @field_validator("database_path")
    @classmethod
    def validate_database_path(cls, value: str) -> str:
        if not value.strip():
            raise BlackcrestConfigError("database_path cannot be empty")
        return value

    @field_validator("score_notification_threshold")
    @classmethod
    def validate_score_notification_threshold(cls, value: float) -> float:
        if value < 0 or value > 100:
            raise BlackcrestConfigError("score_notification_threshold must be between 0 and 100")
        return value

    @field_validator("gmail_retry_attempts")
    @classmethod
    def validate_gmail_retry_attempts(cls, value: int) -> int:
        if value < 1:
            raise BlackcrestConfigError("gmail_retry_attempts must be at least 1")
        return value

    @field_validator("gmail_retry_delay_seconds")
    @classmethod
    def validate_gmail_retry_delay_seconds(cls, value: float) -> float:
        if value < 0:
            raise BlackcrestConfigError("gmail_retry_delay_seconds must be non-negative")
        return value

    def __init__(self, **data: Any) -> None:
        validate_required = data.pop("validate_required", False)
        super().__init__(**data)
        self.database_url = f"sqlite:///{self.database_path}"
        if validate_required:
            self.validate_required_settings()

    def validate_required_settings(self) -> None:
        self.validate_openai_settings()
        self.validate_gmail_settings(require_recipients=False)

    def validate_openai_settings(self) -> None:
        self.validate_feature_settings("openai")

    def validate_gmail_settings(self, require_recipients: bool = True) -> None:
        profiles = ("with_recipients",) if require_recipients else ()
        self.validate_feature_settings("gmail", profiles=profiles)

    def validate_feature_settings(self, feature: str, profiles: tuple[str, ...] = ()) -> None:
        key = feature.strip().lower()
        if key not in self.FEATURE_REQUIREMENTS:
            raise BlackcrestConfigError(f"Unknown feature for settings validation: {feature}")

        fields = list(self.FEATURE_REQUIREMENTS[key])
        feature_profiles = self.FEATURE_OPTIONAL_REQUIREMENTS.get(key, {})
        for profile in profiles:
            profile_key = profile.strip().lower()
            if profile_key not in feature_profiles:
                raise BlackcrestConfigError(f"Unknown validation profile '{profile}' for feature '{feature}'")
            fields.extend(feature_profiles[profile_key])

        required_fields = {field_name: getattr(self, field_name, "") for field_name in fields}
        self._validate_required_fields(required_fields)

    def _validate_required_fields(self, fields: dict[str, Any]) -> None:
        missing = [name for name, value in fields.items() if not str(value).strip()]
        if missing:
            raise BlackcrestConfigError("Missing required settings: " + ", ".join(missing))


def get_settings(validate_required: bool = False) -> Settings:
    """Build and return settings with optional strict required-field validation."""
    try:
        settings = Settings(validate_required=validate_required)
    except ValidationError as exc:
        raise BlackcrestConfigError(f"Invalid configuration: {exc}") from exc

    if validate_required:
        settings.validate_required_settings()
    return settings
