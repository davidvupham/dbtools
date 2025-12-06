"""
Custom exceptions for the gds_notification package.

This module defines a hierarchy of exceptions for handling
notification-related errors in a consistent manner.
"""


class GdsNotificationError(Exception):
    """Base exception for gds_notification package.

    All custom exceptions in this package inherit from this class,
    allowing consumers to catch all package-specific errors with
    a single except clause.

    Attributes:
        message: The error message.
        details: Optional dictionary with additional error context.
    """

    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} - Details: {self.details}"
        return self.message


class NotificationConnectionError(GdsNotificationError):
    """Raised when connection to a notification provider fails.

    This includes scenarios such as:
    - SMTP server unreachable
    - MIR3 API endpoint unavailable
    - Network connectivity issues
    - Authentication failures
    """

    pass


class NotificationDeliveryError(GdsNotificationError):
    """Raised when notification delivery fails.

    This includes scenarios such as:
    - Recipient rejected
    - Provider returned error
    - Message format invalid for provider
    - Quota exceeded
    """

    def __init__(
        self,
        message: str,
        recipient: str | None = None,
        provider: str | None = None,
        details: dict | None = None,
    ) -> None:
        super().__init__(message, details)
        self.recipient = recipient
        self.provider = provider


class NotificationTimeoutError(GdsNotificationError):
    """Raised when a notification operation times out.

    This includes scenarios such as:
    - Connection timeout
    - Send timeout
    - Response timeout from provider
    """

    def __init__(
        self,
        message: str,
        timeout_seconds: float | None = None,
        details: dict | None = None,
    ) -> None:
        super().__init__(message, details)
        self.timeout_seconds = timeout_seconds


class NotificationConfigError(GdsNotificationError):
    """Raised when notification configuration is invalid.

    This includes scenarios such as:
    - Missing required configuration
    - Invalid credentials format
    - Unsupported provider type
    - Invalid provider endpoint
    """

    pass


class NotificationValidationError(GdsNotificationError):
    """Raised when notification payload validation fails.

    This includes scenarios such as:
    - Missing required fields
    - Invalid recipient format
    - Message content too large
    - Invalid priority level
    """

    def __init__(
        self,
        message: str,
        field: str | None = None,
        value: str | None = None,
        details: dict | None = None,
    ) -> None:
        super().__init__(message, details)
        self.field = field
        self.value = value


class NotificationRateLimitError(GdsNotificationError):
    """Raised when provider rate limits are exceeded.

    This includes scenarios such as:
    - Too many requests per minute
    - Daily quota exceeded
    - Burst limit reached
    """

    def __init__(
        self,
        message: str,
        retry_after_seconds: float | None = None,
        details: dict | None = None,
    ) -> None:
        super().__init__(message, details)
        self.retry_after_seconds = retry_after_seconds
