"""Custom exceptions for gds_liquibase package."""


class LiquibaseError(Exception):
    """Base exception for all Liquibase-related errors."""

    pass


class ConfigurationError(LiquibaseError):
    """Raised when there's an issue with Liquibase configuration."""

    pass


class ExecutionError(LiquibaseError):
    """Raised when Liquibase command execution fails."""

    pass


class ValidationError(LiquibaseError):
    """Raised when changelog validation fails."""

    pass


class ChangelogNotFoundError(LiquibaseError):
    """Raised when a changelog file cannot be found."""

    pass


class LiquibaseNotFoundError(LiquibaseError):
    """Raised when Liquibase executable is not found."""

    pass
