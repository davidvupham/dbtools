"""Constants and exit codes for dbtool CLI.

Exit codes follow the specification in technical-architecture.md.
"""

from __future__ import annotations

from enum import IntEnum


class ExitCode(IntEnum):
    """Standard exit codes for dbtool CLI.

    These codes enable scripting and CI/CD integration by providing
    consistent, meaningful return values.
    """

    SUCCESS = 0
    """Command completed successfully."""

    GENERAL_ERROR = 1
    """Unspecified failure."""

    AUTH_ERROR = 2
    """Authentication error - Vault token expired, Kerberos ticket invalid."""

    CONNECTION_ERROR = 3
    """Connection error - Database unreachable, network timeout."""

    PERMISSION_DENIED = 4
    """Permission denied - Insufficient Vault policy permissions."""

    INVALID_INPUT = 5
    """Invalid input - Malformed target name, missing required argument."""

    RESOURCE_NOT_FOUND = 6
    """Resource not found - Target database not in inventory."""


# Error message constants for consistent error reporting
class ErrorMessage:
    """Standard error message templates."""

    VAULT_AUTH_FAILED = "VAULT_AUTH_FAILED: {details}"
    TARGET_NOT_FOUND = "TARGET_NOT_FOUND: {target}"
    CONNECTION_TIMEOUT = "CONNECTION_TIMEOUT: {target}"
    PERMISSION_DENIED = "PERMISSION_DENIED: {resource}"
    DRIVER_NOT_FOUND = "DRIVER_NOT_FOUND: {driver}"
    INVALID_CONFIG = "INVALID_CONFIG: {details}"
    SECRET_NOT_FOUND = "SECRET_NOT_FOUND: {path}"
