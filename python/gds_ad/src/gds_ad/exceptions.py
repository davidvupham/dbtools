"""
Exception classes for gds_active_directory package.

This module defines a hierarchy of exceptions for different error scenarios,
enabling precise error handling and better debugging.
"""


class ActiveDirectoryError(Exception):
    """
    Base exception for all Active Directory-related errors.

    This is the parent class for all custom exceptions in the package,
    allowing users to catch all package-specific errors with a single handler.

    Example:
        try:
            client.get_user_group_membership("jdoe")
        except ActiveDirectoryError as e:
            logger.error(f"AD operation failed: {e}")
    """

    pass


class ADConnectionError(ActiveDirectoryError):
    """
    Exception raised for LDAP connection failures.

    Raised when:
    - LDAP server is unreachable
    - Network timeout occurs
    - DNS resolution fails
    - TLS/SSL handshake fails

    Example:
        try:
            client.connect()
        except ADConnectionError as e:
            logger.error(f"Cannot connect to AD: {e}")
    """

    pass


class ADAuthenticationError(ActiveDirectoryError):
    """
    Exception raised for authentication/bind failures.

    Raised when:
    - Credentials are invalid
    - Account is locked or disabled
    - Kerberos ticket is expired or invalid

    Example:
        try:
            client.connect()
        except ADAuthenticationError as e:
            logger.error(f"Authentication failed: {e}")
    """

    pass


class ADSearchError(ActiveDirectoryError):
    """
    Exception raised for search/query failures.

    Raised when:
    - Search base DN is invalid
    - Search filter syntax is invalid
    - Insufficient permissions to search

    Example:
        try:
            groups = client.get_user_group_membership("jdoe")
        except ADSearchError as e:
            logger.error(f"Search failed: {e}")
    """

    pass


class ADModificationError(ActiveDirectoryError):
    """
    Exception raised for modification failures.

    Raised when:
    - Insufficient permissions to modify
    - Target object does not exist
    - Constraint violation (e.g., removing from non-member group)

    Example:
        try:
            client.remove_user_group_membership("jdoe", ["SQL_Admin"])
        except ADModificationError as e:
            logger.error(f"Modification failed: {e}")
    """

    pass


class ADConfigurationError(ActiveDirectoryError):
    """
    Exception raised for configuration errors.

    Raised when:
    - Required configuration is missing
    - Invalid configuration values provided
    - Server address is malformed

    Example:
        try:
            client = ActiveDirectoryClient(server="invalid")
        except ADConfigurationError as e:
            logger.error(f"Configuration error: {e}")
    """

    pass


class ADObjectNotFoundError(ActiveDirectoryError):
    """
    Exception raised when an AD object is not found.

    Raised when:
    - User does not exist
    - Group does not exist
    - DN is invalid

    Example:
        try:
            groups = client.get_user_group_membership("nonexistent")
        except ADObjectNotFoundError as e:
            logger.error(f"Object not found: {e}")
    """

    pass
