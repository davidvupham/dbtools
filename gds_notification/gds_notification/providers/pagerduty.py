"""
PagerDuty notification provider.

This module provides a PagerDuty Events API v2 based notification provider
for incident alerting and on-call management.

For more information, see: https://developer.pagerduty.com/docs/events-api-v2/overview/
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from gds_notification.exceptions import (
    NotificationConfigError,
    NotificationConnectionError,
    NotificationDeliveryError,
    NotificationRateLimitError,
    NotificationTimeoutError,
)
from gds_notification.providers.base import (
    BaseNotificationProvider,
    Notification,
    NotificationPriority,
    NotificationResult,
)

logger = logging.getLogger(__name__)


class PagerDutySeverity(Enum):
    """PagerDuty event severity levels."""

    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class PagerDutyEventAction(Enum):
    """PagerDuty event actions."""

    TRIGGER = "trigger"
    ACKNOWLEDGE = "acknowledge"
    RESOLVE = "resolve"


@dataclass
class PagerDutyEventResult:
    """Result of a PagerDuty event submission.

    Attributes:
        status: HTTP status code from PagerDuty.
        message: Response message.
        dedup_key: Deduplication key for the event.
    """

    status: str
    message: str
    dedup_key: str | None = None


class PagerDutyProvider(BaseNotificationProvider):
    """PagerDuty notification provider using Events API v2.

    Sends incidents to PagerDuty for alerting and on-call management.
    Supports triggering, acknowledging, and resolving incidents.

    Args:
        routing_key: PagerDuty Events API v2 integration/routing key.
        api_url: PagerDuty Events API URL (default: https://events.pagerduty.com/v2/enqueue).
        timeout: Request timeout in seconds (default: 30).
        default_severity: Default severity for events (default: ERROR).
        source: Default source identifier (default: "gds_notification").

    Example:
        >>> provider = PagerDutyProvider(
        ...     routing_key="your-integration-key-here",
        ... )
        >>> notification = Notification(
        ...     recipient="database-alerts",  # Used as routing context
        ...     subject="High CPU on db-prod-01",
        ...     body="CPU usage exceeded 90% for 5 minutes",
        ...     priority=NotificationPriority.CRITICAL,
        ... )
        >>> result = provider.send(notification)
        >>> print(result.metadata.get("dedup_key"))
        alert-12345

    Note:
        This provider requires the `requests` library.
        Install with: pip install requests
    """

    EVENTS_API_URL = "https://events.pagerduty.com/v2/enqueue"

    def __init__(
        self,
        routing_key: str,
        api_url: str | None = None,
        timeout: float = 30.0,
        default_severity: PagerDutySeverity = PagerDutySeverity.ERROR,
        source: str = "gds_notification",
    ) -> None:
        """Initialize the PagerDuty provider."""
        super().__init__(name="pagerduty")

        if not routing_key:
            raise NotificationConfigError("PagerDuty routing key is required")

        self.routing_key = routing_key
        self.api_url = api_url or self.EVENTS_API_URL
        self.timeout = timeout
        self.default_severity = default_severity
        self.source = source

        # Lazy-load requests
        self._session: Any = None

    def _get_session(self) -> Any:
        """Get or create the HTTP session.

        Returns:
            requests.Session instance.

        Raises:
            NotificationConfigError: If requests is not installed.
        """
        if self._session is not None:
            return self._session

        try:
            import requests
        except ImportError as e:
            raise NotificationConfigError(
                "requests library is required for PagerDuty integration. "
                "Install with: pip install requests",
                details={"missing_package": "requests"},
            ) from e

        self._session = requests.Session()
        self._session.headers.update(
            {
                "Content-Type": "application/json",
            }
        )
        return self._session

    def _map_priority_to_severity(self, priority: NotificationPriority) -> PagerDutySeverity:
        """Map notification priority to PagerDuty severity.

        Args:
            priority: Notification priority.

        Returns:
            PagerDuty severity level.
        """
        priority_map = {
            NotificationPriority.LOW: PagerDutySeverity.INFO,
            NotificationPriority.NORMAL: PagerDutySeverity.WARNING,
            NotificationPriority.HIGH: PagerDutySeverity.ERROR,
            NotificationPriority.CRITICAL: PagerDutySeverity.CRITICAL,
            NotificationPriority.EMERGENCY: PagerDutySeverity.CRITICAL,
        }
        return priority_map.get(priority, self.default_severity)

    def _build_event_payload(
        self,
        notification: Notification,
        action: PagerDutyEventAction = PagerDutyEventAction.TRIGGER,
    ) -> dict[str, Any]:
        """Build the PagerDuty Events API v2 payload.

        Args:
            notification: The notification to convert.
            action: Event action (trigger, acknowledge, resolve).

        Returns:
            Dictionary payload for the Events API.
        """
        severity = self._map_priority_to_severity(notification.priority)

        payload: dict[str, Any] = {
            "routing_key": self.routing_key,
            "event_action": action.value,
        }

        # Use idempotency_id as dedup_key if provided
        if notification.idempotency_id:
            payload["dedup_key"] = notification.idempotency_id

        # For trigger events, include full payload
        if action == PagerDutyEventAction.TRIGGER:
            payload["payload"] = {
                "summary": notification.subject or "Alert",
                "severity": severity.value,
                "source": self.source,
                "component": notification.recipient,  # Use recipient as component
                "group": notification.alert_name or "alerts",
                "class": "gds_notification",
                "custom_details": {
                    "body": notification.body,
                    "alert_name": notification.alert_name,
                    "db_instance_id": notification.db_instance_id,
                    "priority": notification.priority.value,
                    **notification.metadata,
                },
            }

            # Add timestamp if available
            payload["payload"]["timestamp"] = datetime.utcnow().isoformat() + "Z"

        return payload

    def send(
        self,
        notification: Notification,
        action: PagerDutyEventAction = PagerDutyEventAction.TRIGGER,
    ) -> NotificationResult:
        """Send an event to PagerDuty.

        Args:
            notification: The notification to send.
            action: Event action (default: TRIGGER).

        Returns:
            NotificationResult with delivery status.

        Raises:
            NotificationConnectionError: If PagerDuty API is unreachable.
            NotificationDeliveryError: If event submission fails.
            NotificationTimeoutError: If operation times out.
            NotificationRateLimitError: If rate limited by PagerDuty.
        """
        import requests

        session = self._get_session()
        payload = self._build_event_payload(notification, action)

        logger.info(
            "Sending PagerDuty event",
            extra={
                "action": action.value,
                "severity": payload.get("payload", {}).get("severity"),
                "dedup_key": payload.get("dedup_key"),
            },
        )

        try:
            response = session.post(
                self.api_url,
                data=json.dumps(payload),
                timeout=self.timeout,
            )

            # Handle response
            if response.status_code == 202:
                # Success
                result_data = response.json()
                dedup_key = result_data.get("dedup_key")

                logger.info(
                    "PagerDuty event sent successfully",
                    extra={
                        "dedup_key": dedup_key,
                        "status": result_data.get("status"),
                    },
                )

                return self._create_success_result(
                    recipient=notification.recipient,
                    message_id=dedup_key,
                    metadata={
                        "dedup_key": dedup_key,
                        "status": result_data.get("status"),
                        "message": result_data.get("message"),
                        "action": action.value,
                    },
                )

            elif response.status_code == 429:
                # Rate limited
                retry_after = float(response.headers.get("Retry-After", 60))
                raise NotificationRateLimitError(
                    "PagerDuty rate limit exceeded",
                    retry_after_seconds=retry_after,
                )

            elif response.status_code == 400:
                # Bad request
                error_data = response.json()
                raise NotificationDeliveryError(
                    f"PagerDuty rejected event: {error_data.get('message', 'Bad request')}",
                    recipient=notification.recipient,
                    provider=self.name,
                    details=error_data,
                )

            else:
                # Other error
                raise NotificationDeliveryError(
                    f"PagerDuty API error: HTTP {response.status_code}",
                    recipient=notification.recipient,
                    provider=self.name,
                    details={"status_code": response.status_code, "body": response.text},
                )

        except requests.exceptions.Timeout as e:
            raise NotificationTimeoutError(
                f"PagerDuty request timed out: {e}",
                timeout_seconds=self.timeout,
            ) from e

        except requests.exceptions.ConnectionError as e:
            raise NotificationConnectionError(
                f"Failed to connect to PagerDuty: {e}",
                details={"api_url": self.api_url},
            ) from e

        except requests.exceptions.RequestException as e:
            raise NotificationDeliveryError(
                f"PagerDuty request failed: {e}",
                recipient=notification.recipient,
                provider=self.name,
            ) from e

    def trigger(self, notification: Notification) -> NotificationResult:
        """Trigger a new incident in PagerDuty.

        Args:
            notification: The notification to send.

        Returns:
            NotificationResult with delivery status.
        """
        return self.send(notification, action=PagerDutyEventAction.TRIGGER)

    def acknowledge(self, dedup_key: str) -> NotificationResult:
        """Acknowledge an existing incident.

        Args:
            dedup_key: The deduplication key of the incident to acknowledge.

        Returns:
            NotificationResult with delivery status.
        """
        notification = Notification(
            recipient="",
            subject="",
            body="",
            idempotency_id=dedup_key,
        )
        return self.send(notification, action=PagerDutyEventAction.ACKNOWLEDGE)

    def resolve(self, dedup_key: str) -> NotificationResult:
        """Resolve an existing incident.

        Args:
            dedup_key: The deduplication key of the incident to resolve.

        Returns:
            NotificationResult with delivery status.
        """
        notification = Notification(
            recipient="",
            subject="",
            body="",
            idempotency_id=dedup_key,
        )
        return self.send(notification, action=PagerDutyEventAction.RESOLVE)

    def send_bulk(
        self,
        notifications: list[Notification],
    ) -> list[NotificationResult]:
        """Send multiple events to PagerDuty.

        Note: PagerDuty Events API doesn't support batch operations,
        so this sends events sequentially.

        Args:
            notifications: List of notifications to send.

        Returns:
            List of NotificationResult for each notification.
        """
        results = []
        for notification in notifications:
            try:
                result = self.send(notification)
                results.append(result)
            except Exception as e:
                results.append(
                    self._create_failure_result(
                        recipient=notification.recipient,
                        error_message=str(e),
                        retry_after=60.0,
                    )
                )
        return results

    def health_check(self) -> bool:
        """Check if PagerDuty API is reachable.

        Note: The Events API doesn't have a dedicated health endpoint,
        so we just verify we can establish a connection.

        Returns:
            True if API is reachable, False otherwise.
        """
        try:
            import requests

            response = requests.head(
                self.api_url,
                timeout=5.0,
            )
            # Any response (even 405 Method Not Allowed) means API is up
            return response.status_code < 500
        except Exception as e:
            logger.warning(f"PagerDuty health check failed: {e}")
            return False

    def close(self) -> None:
        """Close the HTTP session and cleanup resources."""
        if self._session is not None:
            self._session.close()
            self._session = None
            logger.debug("PagerDuty HTTP session closed")

    def __enter__(self) -> "PagerDutyProvider":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit with cleanup."""
        self.close()
