"""
MIR3 emergency notification provider.

This module provides a MIR3 SOAP API-based notification provider for sending
emergency notifications through the MIR3/OnSolve platform.

MIR3 supports multiple notification methods:
- Broadcast: Send message to all recipients simultaneously
- First Response: Stop notifications when first recipient responds
- Callout: Sequential notification until someone responds
- Bulletin Board: Post message for recipients to retrieve

For more information, see: https://www.onsolve.com/
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from gds_notification.exceptions import (
    NotificationConfigError,
    NotificationConnectionError,
    NotificationDeliveryError,
    NotificationTimeoutError,
)
from gds_notification.providers.base import (
    BaseNotificationProvider,
    Notification,
    NotificationPriority,
    NotificationResult,
)

logger = logging.getLogger(__name__)


class MIR3NotificationMethod(Enum):
    """MIR3 notification methods.

    Each method has different behavior for how recipients are notified
    and how responses are collected.
    """

    BROADCAST = "broadcast"  # Send to all recipients simultaneously
    FIRST_RESPONSE = "first_response"  # Stop when first recipient responds
    CALLOUT = "callout"  # Sequential notification until response
    BULLETIN_BOARD = "bulletin"  # Post for recipients to retrieve


@dataclass
class MIR3NotificationStatus:
    """Status of a MIR3 notification.

    Attributes:
        report_id: MIR3 notification report ID for tracking.
        status: Current notification status.
        sent_count: Number of recipients notified.
        responded_count: Number of recipients who responded.
        failed_count: Number of delivery failures.
        timestamp: Status check timestamp.
    """

    report_id: str
    status: str
    sent_count: int = 0
    responded_count: int = 0
    failed_count: int = 0
    timestamp: datetime | None = None


class MIR3Provider(BaseNotificationProvider):
    """MIR3 emergency notification provider.

    Sends notifications via MIR3 SOAP API for emergency/critical alerts.
    This provider is designed for high-priority notifications that require
    delivery confirmation and response tracking.

    Args:
        wsdl_url: MIR3 SOAP WSDL endpoint URL.
        username: MIR3 API username.
        password: MIR3 API password.
        default_method: Default notification method (default: BROADCAST).
        timeout: Request timeout in seconds (default: 60).
        response_options: Default response options for recipients.

    Example:
        >>> provider = MIR3Provider(
        ...     wsdl_url="https://mir3.example.com/ws/NotificationService?wsdl",
        ...     username="api_user",
        ...     password="api_secret",
        ...     default_method=MIR3NotificationMethod.BROADCAST,
        ... )
        >>> notification = Notification(
        ...     recipient="johndoe",  # MIR3 username
        ...     subject="Critical Alert",
        ...     body="Database server is down",
        ...     priority=NotificationPriority.EMERGENCY,
        ... )
        >>> result = provider.send(notification)
        >>> print(result.metadata.get("report_id"))
        12345

    Note:
        This provider requires the `zeep` library for SOAP communication.
        Install with: pip install zeep
    """

    def __init__(
        self,
        wsdl_url: str,
        username: str,
        password: str,
        default_method: MIR3NotificationMethod = MIR3NotificationMethod.BROADCAST,
        timeout: float = 60.0,
        response_options: list[str] | None = None,
    ) -> None:
        """Initialize the MIR3 provider."""
        super().__init__(name="mir3")

        if not wsdl_url:
            raise NotificationConfigError("MIR3 WSDL URL is required")
        if not username:
            raise NotificationConfigError("MIR3 username is required")
        if not password:
            raise NotificationConfigError("MIR3 password is required")

        self.wsdl_url = wsdl_url
        self.username = username
        self.password = password
        self.default_method = default_method
        self.timeout = timeout
        self.response_options = response_options or ["Acknowledge", "Escalate", "Ignore"]

        # Lazy-load SOAP client
        self._client: Any = None

    def _get_client(self) -> Any:
        """Get or create the SOAP client.

        Returns:
            Zeep SOAP client instance.

        Raises:
            NotificationConfigError: If zeep is not installed.
            NotificationConnectionError: If WSDL cannot be loaded.
        """
        if self._client is not None:
            return self._client

        try:
            from requests import Session
            from zeep import Client
            from zeep.transports import Transport
        except ImportError as e:
            raise NotificationConfigError(
                "zeep library is required for MIR3 integration. Install with: pip install zeep",
                details={"missing_package": "zeep"},
            ) from e

        try:
            session = Session()
            session.timeout = self.timeout
            transport = Transport(session=session, timeout=self.timeout)
            self._client = Client(wsdl=self.wsdl_url, transport=transport)
            logger.info(
                "MIR3 SOAP client initialized",
                extra={"wsdl_url": self.wsdl_url},
            )
            return self._client
        except Exception as e:
            raise NotificationConnectionError(
                f"Failed to load MIR3 WSDL: {e}",
                details={"wsdl_url": self.wsdl_url},
            ) from e

    def _map_priority_to_mir3(self, priority: NotificationPriority) -> str:
        """Map notification priority to MIR3 priority level.

        Args:
            priority: Notification priority.

        Returns:
            MIR3 priority string.
        """
        priority_map = {
            NotificationPriority.LOW: "Low",
            NotificationPriority.NORMAL: "Normal",
            NotificationPriority.HIGH: "High",
            NotificationPriority.CRITICAL: "Critical",
            NotificationPriority.EMERGENCY: "Emergency",
        }
        return priority_map.get(priority, "Normal")

    def _map_method_to_mir3(self, method: MIR3NotificationMethod) -> str:
        """Map notification method to MIR3 API method name.

        Args:
            method: Notification method.

        Returns:
            MIR3 API method name.
        """
        method_map = {
            MIR3NotificationMethod.BROADCAST: "sendBroadcast",
            MIR3NotificationMethod.FIRST_RESPONSE: "sendFirstResponse",
            MIR3NotificationMethod.CALLOUT: "sendCallout",
            MIR3NotificationMethod.BULLETIN_BOARD: "sendBulletin",
        }
        return method_map.get(method, "sendBroadcast")

    def send(
        self,
        notification: Notification,
        method: MIR3NotificationMethod | None = None,
    ) -> NotificationResult:
        """Send an emergency notification via MIR3.

        Args:
            notification: The notification to send.
            method: Notification method (overrides default).

        Returns:
            NotificationResult with delivery status and MIR3 report ID.

        Raises:
            NotificationConnectionError: If MIR3 API is unreachable.
            NotificationDeliveryError: If notification fails.
            NotificationTimeoutError: If operation times out.
        """
        use_method = method or self.default_method
        client = self._get_client()

        try:
            # Build SOAP request parameters
            request_params = {
                "username": self.username,
                "password": self.password,
                "notificationTitle": notification.subject or "Alert",
                "messageDescription": notification.alert_name or notification.subject or "Alert",
                "messageContent": notification.body or "",
                "recipientUsernames": notification.recipient,
                "responseOptions": ",".join(self.response_options),
                "priority": self._map_priority_to_mir3(notification.priority),
            }

            # Add idempotency tracking
            if notification.idempotency_id:
                request_params["externalId"] = notification.idempotency_id

            # Call appropriate MIR3 API method
            api_method = self._map_method_to_mir3(use_method)

            logger.info(
                "Sending MIR3 notification",
                extra={
                    "recipient": notification.recipient,
                    "method": use_method.value,
                    "priority": notification.priority.value,
                    "idempotency_id": notification.idempotency_id,
                },
            )

            # Use the generic service call pattern
            # MIR3 API typically returns a report ID on success
            response = self._call_mir3_service(client, api_method, request_params)

            report_id = self._extract_report_id(response)

            logger.info(
                "MIR3 notification sent successfully",
                extra={
                    "recipient": notification.recipient,
                    "report_id": report_id,
                },
            )

            return self._create_success_result(
                recipient=notification.recipient,
                message_id=report_id,
                metadata={
                    "report_id": report_id,
                    "method": use_method.value,
                    "priority": notification.priority.value,
                },
            )

        except TimeoutError as e:
            raise NotificationTimeoutError(
                f"MIR3 request timed out: {e}",
                timeout_seconds=self.timeout,
            ) from e

        except Exception as e:
            error_msg = f"MIR3 notification failed: {e}"
            logger.error(
                error_msg,
                extra={
                    "recipient": notification.recipient,
                    "error": str(e),
                },
            )
            raise NotificationDeliveryError(
                error_msg,
                recipient=notification.recipient,
                provider=self.name,
            ) from e

    def _call_mir3_service(
        self,
        client: Any,
        method_name: str,
        params: dict[str, Any],
    ) -> Any:
        """Call the MIR3 SOAP service.

        This method abstracts the SOAP call to allow for:
        1. Different MIR3 API versions
        2. Mocking in tests
        3. Error handling normalization

        Args:
            client: Zeep SOAP client.
            method_name: MIR3 API method name.
            params: Request parameters.

        Returns:
            SOAP response object.
        """
        # Get the service method dynamically
        service = client.service
        soap_method = getattr(service, method_name, None)

        if soap_method is None:
            # Fall back to generic notification service
            soap_method = getattr(service, "sendNotification", None)
            if soap_method is None:
                raise NotificationDeliveryError(
                    f"MIR3 API method not found: {method_name}",
                    provider=self.name,
                )

        return soap_method(**params)

    def _extract_report_id(self, response: Any) -> str:
        """Extract the notification report ID from MIR3 response.

        Args:
            response: SOAP response object.

        Returns:
            Report ID string.
        """
        # Handle different response formats
        if hasattr(response, "notificationReportId"):
            return str(response.notificationReportId)
        if hasattr(response, "reportId"):
            return str(response.reportId)
        if isinstance(response, dict):
            return str(
                response.get("notificationReportId") or response.get("reportId") or "unknown"
            )
        return str(response) if response else "unknown"

    def send_bulk(
        self,
        notifications: list[Notification],
        method: MIR3NotificationMethod | None = None,
    ) -> list[NotificationResult]:
        """Send emergency notifications to multiple recipients.

        MIR3 supports batch notifications, so this method combines
        recipients into a single API call for efficiency.

        Args:
            notifications: List of notifications to send.
            method: Notification method (overrides default).

        Returns:
            List of NotificationResult for each notification.
        """
        if not notifications:
            return []

        # Group by subject/body for efficient batching
        # (MIR3 can send same message to multiple recipients in one call)
        grouped: dict[tuple[str, str], list[Notification]] = {}
        for n in notifications:
            key = (n.subject or "", n.body or "")
            grouped.setdefault(key, []).append(n)

        results: list[NotificationResult] = []

        for (subject, body), group in grouped.items():
            # Combine recipients for batch send
            recipients = ",".join(n.recipient for n in group)

            # Use first notification as template
            template = Notification(
                recipient=recipients,
                subject=subject,
                body=body,
                priority=max(n.priority for n in group),
                alert_name=group[0].alert_name,
                idempotency_id=group[0].idempotency_id,
            )

            try:
                result = self.send(template, method=method)
                # Create individual results for each recipient
                for n in group:
                    results.append(
                        NotificationResult(
                            status=result.status,
                            recipient=n.recipient,
                            provider=self.name,
                            message_id=result.message_id,
                            metadata=result.metadata.copy(),
                        )
                    )
            except Exception as e:
                # Individual failures for each recipient
                for n in group:
                    results.append(
                        self._create_failure_result(
                            recipient=n.recipient,
                            error_message=str(e),
                            retry_after=60.0,
                        )
                    )

        return results

    def get_notification_status(
        self,
        report_id: str,
    ) -> MIR3NotificationStatus:
        """Check the status of a sent notification.

        Args:
            report_id: MIR3 notification report ID.

        Returns:
            MIR3NotificationStatus with delivery details.

        Raises:
            NotificationConnectionError: If MIR3 API is unreachable.
            NotificationDeliveryError: If status check fails.
        """
        client = self._get_client()

        try:
            response = client.service.getNotificationStatus(
                username=self.username,
                password=self.password,
                notificationReportId=report_id,
            )

            return MIR3NotificationStatus(
                report_id=report_id,
                status=getattr(response, "status", "unknown"),
                sent_count=getattr(response, "sentCount", 0),
                responded_count=getattr(response, "respondedCount", 0),
                failed_count=getattr(response, "failedCount", 0),
                timestamp=datetime.utcnow(),
            )

        except Exception as e:
            raise NotificationDeliveryError(
                f"Failed to get MIR3 notification status: {e}",
                provider=self.name,
                details={"report_id": report_id},
            ) from e

    def health_check(self) -> bool:
        """Check if MIR3 API is reachable.

        Returns:
            True if API responds, False otherwise.
        """
        try:
            # Attempt to load the WSDL (which verifies connectivity)
            self._get_client()
            return True
        except Exception as e:
            logger.warning(f"MIR3 health check failed: {e}")
            return False

    def close(self) -> None:
        """Close the SOAP client and cleanup resources."""
        if self._client is not None:
            # Zeep clients are generally stateless, but cleanup transport
            if hasattr(self._client, "transport") and hasattr(self._client.transport, "session"):
                self._client.transport.session.close()
            self._client = None
            logger.debug("MIR3 SOAP client closed")

    def __enter__(self) -> "MIR3Provider":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit with cleanup."""
        self.close()
