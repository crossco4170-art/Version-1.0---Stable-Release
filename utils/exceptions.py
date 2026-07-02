from __future__ import annotations


class BlackcrestError(Exception):
    """Base exception for application-specific failures."""


class BlackcrestInputError(ValueError, BlackcrestError):
    """Raised when user-provided or workflow input is invalid."""


class BlackcrestConfigError(BlackcrestInputError):
    """Raised for invalid or missing application configuration."""


class BlackcrestDependencyError(RuntimeError, BlackcrestError):
    """Raised when an optional third-party dependency is unavailable."""


class BlackcrestIntegrationError(RuntimeError, BlackcrestError):
    """Raised for external integration and API response failures."""


class BlackcrestNotFoundError(BlackcrestInputError):
    """Raised when a requested domain record cannot be found."""


class BlackcrestAuthError(BlackcrestInputError):
    """Raised for administrator bootstrap and credential input errors."""
