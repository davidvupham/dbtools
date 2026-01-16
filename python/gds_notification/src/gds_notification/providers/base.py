"""
Base notification provider interface and data models.

This module defines the protocol (interface) for notification providers
and common data structures used across all provider implementations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Protocol, runtime_checkable


class NotificationStatus(Enum):
    """Status of a notification delivery attempt."""

    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"
    RATE_LIMITED = "rate_limited"
    BLACKOUT = "blackout"


class NotificationPriority(Enum):
    """Priority level for notifications."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class NotificationResult:
    """Result of a notification delivery attempt.

    Attributes:
        status: The delivery status.
        recipient: The recipient address/identifier.
        provider: The provider name used for delivery.
        message_id: Provider-specific message identifier.
        timestamp: When the notification was sent.
        error_message: Error message if delivery failed.
        retry_after: Seconds to wait before retry (for rate limiting).
        metadata: Additional provider-specific metadata.
    """

    status: NotificationStatus
    recipient: str
    provider: str
    message_id: str | None = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    error_message: str | None = None
    retry_after: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_success(self) -> bool:
        """Return True if notification was successfully sent or delivered."""
        return self.status in (NotificationStatus.SENT, NotificationStatus.DELIVERED)

    def is_retriable(self) -> bool:
        """Return True if the failure is potentially retriable."""
        return self.status == NotificationStatus.RATE_LIMITED or (
            self.status == NotificationStatus.FAILED and self.retry_after is not None
        )


@dataclass
class Notification:
    """Notification payload to be sent.

    Attributes:
        recipient: The recipient address/identifier.
        subject: The notification subject.
        body: The notification body text.
        body_html: Optional HTML body for email notifications.
        priority: Priority level of the notification.
        alert_name: Name of the alert that triggered this notification.
        db_instance_id: Database instance ID if applicable.
        idempotency_id: Unique ID for deduplication.
        metadata: Additional notification metadata.
    """

    recipient: str
    subject: str
    body: str
    body_html: str | None = None
    priority: NotificationPriority = NotificationPriority.NORMAL
    alert_name: str | None = None
    db_instance_id: int | None = None
    idempotency_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class NotificationProvider(Protocol):
    """Protocol for notification providers.

    All notification providers must implement this interface to be
    usable by the notification service worker.
    """

    @property
    def name(self) -> str:
        """Return the provider name."""
        ...

    def send(
        self,
        notification: Notification,
    ) -> NotificationResult:
        """Send a notification to a single recipient.

        Args:
            notification: The notification to send.

        Returns:
            NotificationResult with delivery status.

        Raises:
            NotificationConnectionError: If connection to provider fails.
            NotificationDeliveryError: If delivery fails.
            NotificationTimeoutError: If operation times out.
        """
        ...

    def send_bulk(
        self,
        notifications: list[Notification],
    ) -> list[NotificationResult]:
        """Send notifications to multiple recipients.

        Default implementation calls send() for each notification.
        Providers may override for batch optimization.

        Args:
            notifications: List of notifications to send.

        Returns:
            List of NotificationResult for each notification.
        """
        ...

    def health_check(self) -> bool:
        """Check if the provider is healthy and available.

        Returns:
            True if provider is available, False otherwise.
        """
        ...


class BaseNotificationProvider(ABC):
    """Abstract base class for notification providers.

    Provides common functionality and default implementations
    for notification providers.
    """

    def __init__(self, name: str) -> None:
        """Initialize the provider.

        Args:
            name: The provider name.
        """
        self._name = name

    @property
    def name(self) -> str:
        """Return the provider name."""
        return self._name

    @abstractmethod
    def send(
        self,
        notification: Notification,
    ) -> NotificationResult:
        """Send a notification to a single recipient."""
        pass

    def send_bulk(
        self,
        notifications: list[Notification],
    ) -> list[NotificationResult]:
        """Send notifications to multiple recipients.

        Default implementation calls send() for each notification.
        Override in subclass for batch optimization.
        """
        results = []
        for notification in notifications:
            result = self.send(notification)
            results.append(result)
        return results

    def health_check(self) -> bool:
        """Check if the provider is healthy.

        Default implementation returns True. Override for actual health checks.
        """
        return True

    def _create_success_result(
        self,
        recipient: str,
        message_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> NotificationResult:
        """Create a successful notification result."""
        return NotificationResult(
            status=NotificationStatus.SENT,
            recipient=recipient,
            provider=self.name,
            message_id=message_id,
            metadata=metadata or {},
        )

    def _create_failure_result(
        self,
        recipient: str,
        error_message: str,
        retry_after: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> NotificationResult:
        """Create a failed notification result."""
        return NotificationResult(
            status=NotificationStatus.FAILED,
            recipient=recipient,
            provider=self.name,
            error_message=error_message,
            retry_after=retry_after,
            metadata=metadata or {},
        )
