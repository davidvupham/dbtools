"""
GDS Notification Service.

A multi-channel notification service for alert ingestion and delivery.
Supports email (SMTP), MIR3 emergency notifications, and extensible provider architecture.
"""

from gds_notification.exceptions import (
    GdsNotificationError,
    NotificationConfigError,
    NotificationConnectionError,
    NotificationDeliveryError,
    NotificationTimeoutError,
    NotificationValidationError,
)

__version__ = "0.1.0"

__all__ = [
    # Version
    "__version__",
    # Exceptions
    "GdsNotificationError",
    "NotificationConfigError",
    "NotificationConnectionError",
    "NotificationDeliveryError",
    "NotificationTimeoutError",
    "NotificationValidationError",
]
