"""
SMTP email notification provider.

This module provides an SMTP-based notification provider for sending
email notifications through any SMTP server.
"""

import logging
import smtplib
import ssl
from email.message import EmailMessage

from gds_notification.exceptions import (
    NotificationConfigError,
    NotificationConnectionError,
    NotificationDeliveryError,
    NotificationTimeoutError,
)
from gds_notification.providers.base import (
    BaseNotificationProvider,
    Notification,
    NotificationResult,
)

logger = logging.getLogger(__name__)


class SMTPProvider(BaseNotificationProvider):
    """SMTP email notification provider.

    Sends email notifications via SMTP with support for TLS encryption
    and authentication.

    Args:
        host: SMTP server hostname.
        port: SMTP server port (default: 587 for TLS, 465 for SSL).
        username: Optional SMTP authentication username.
        password: Optional SMTP authentication password.
        from_address: Email address to send from.
        use_tls: Use STARTTLS encryption (default: True).
        use_ssl: Use SSL/TLS encryption (default: False).
        timeout: Connection timeout in seconds (default: 30).
        debug_level: SMTP debug level (0=off, 1=basic, 2=verbose).

    Example:
        >>> provider = SMTPProvider(
        ...     host="smtp.example.com",
        ...     port=587,
        ...     username="alerts@example.com",
        ...     password="secret",
        ...     from_address="alerts@example.com",
        ... )
        >>> notification = Notification(
        ...     recipient="user@example.com",
        ...     subject="Alert: High CPU",
        ...     body="CPU usage exceeded 90%",
        ... )
        >>> result = provider.send(notification)
        >>> print(result.status)
        NotificationStatus.SENT
    """

    def __init__(
        self,
        host: str,
        port: int = 587,
        username: str | None = None,
        password: str | None = None,
        from_address: str = "alerts@example.com",
        use_tls: bool = True,
        use_ssl: bool = False,
        timeout: float = 30.0,
        debug_level: int = 0,
    ) -> None:
        """Initialize the SMTP provider."""
        super().__init__(name="smtp")

        if not host:
            raise NotificationConfigError("SMTP host is required")
        if use_tls and use_ssl:
            raise NotificationConfigError("Cannot use both TLS and SSL")

        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.from_address = from_address
        self.use_tls = use_tls
        self.use_ssl = use_ssl
        self.timeout = timeout
        self.debug_level = debug_level

    def _create_connection(self) -> smtplib.SMTP | smtplib.SMTP_SSL:
        """Create and return an SMTP connection.

        Returns:
            Connected SMTP client.

        Raises:
            NotificationConnectionError: If connection fails.
            NotificationTimeoutError: If connection times out.
        """
        try:
            if self.use_ssl:
                context = ssl.create_default_context()
                smtp = smtplib.SMTP_SSL(
                    host=self.host,
                    port=self.port,
                    timeout=self.timeout,
                    context=context,
                )
            else:
                smtp = smtplib.SMTP(
                    host=self.host,
                    port=self.port,
                    timeout=self.timeout,
                )

            smtp.set_debuglevel(self.debug_level)

            if self.use_tls:
                context = ssl.create_default_context()
                smtp.starttls(context=context)

            if self.username and self.password:
                smtp.login(self.username, self.password)

            return smtp

        except TimeoutError as e:
            raise NotificationTimeoutError(
                f"SMTP connection timed out: {self.host}:{self.port}",
                timeout_seconds=self.timeout,
            ) from e
        except smtplib.SMTPAuthenticationError as e:
            raise NotificationConnectionError(
                f"SMTP authentication failed: {e}",
                details={"host": self.host, "username": self.username},
            ) from e
        except smtplib.SMTPException as e:
            raise NotificationConnectionError(
                f"SMTP connection failed: {e}",
                details={"host": self.host, "port": self.port},
            ) from e
        except OSError as e:
            raise NotificationConnectionError(
                f"Network error connecting to SMTP: {e}",
                details={"host": self.host, "port": self.port},
            ) from e

    def _build_message(self, notification: Notification) -> EmailMessage:
        """Build an EmailMessage from a Notification.

        Args:
            notification: The notification to convert.

        Returns:
            EmailMessage ready to send.
        """
        msg = EmailMessage()
        msg["From"] = self.from_address
        msg["To"] = notification.recipient
        msg["Subject"] = notification.subject or "Alert"

        # Add custom headers for tracking
        if notification.idempotency_id:
            msg["X-Idempotency-ID"] = notification.idempotency_id
        if notification.alert_name:
            msg["X-Alert-Name"] = notification.alert_name
        if notification.db_instance_id:
            msg["X-DB-Instance-ID"] = str(notification.db_instance_id)

        # Set priority headers
        priority_map = {
            "low": ("5", "non-urgent"),
            "normal": ("3", "normal"),
            "high": ("2", "urgent"),
            "critical": ("1", "urgent"),
            "emergency": ("1", "urgent"),
        }
        priority_num, importance = priority_map.get(notification.priority.value, ("3", "normal"))
        msg["X-Priority"] = priority_num
        msg["Importance"] = importance

        # Set body content
        msg.set_content(notification.body or "")
        if notification.body_html:
            msg.add_alternative(notification.body_html, subtype="html")

        return msg

    def send(
        self,
        notification: Notification,
    ) -> NotificationResult:
        """Send an email notification.

        Args:
            notification: The notification to send.

        Returns:
            NotificationResult with delivery status.

        Raises:
            NotificationConnectionError: If SMTP connection fails.
            NotificationDeliveryError: If email delivery fails.
            NotificationTimeoutError: If operation times out.
        """
        msg = self._build_message(notification)

        try:
            with self._create_connection() as smtp:
                smtp.send_message(msg)
                logger.info(
                    "Email sent successfully",
                    extra={
                        "recipient": notification.recipient,
                        "subject": notification.subject,
                        "idempotency_id": notification.idempotency_id,
                    },
                )
                return self._create_success_result(
                    recipient=notification.recipient,
                    message_id=notification.idempotency_id,
                    metadata={
                        "from": self.from_address,
                        "subject": notification.subject,
                    },
                )

        except smtplib.SMTPRecipientsRefused as e:
            error_msg = f"Recipients refused: {e.recipients}"
            logger.warning(
                "Email delivery failed - recipients refused",
                extra={"recipient": notification.recipient, "error": str(e)},
            )
            raise NotificationDeliveryError(
                error_msg,
                recipient=notification.recipient,
                provider=self.name,
            ) from e

        except smtplib.SMTPDataError as e:
            logger.warning(
                "Email delivery failed - data error",
                extra={"recipient": notification.recipient, "error": str(e)},
            )
            raise NotificationDeliveryError(
                f"SMTP data error: {e}",
                recipient=notification.recipient,
                provider=self.name,
            ) from e

        except smtplib.SMTPException as e:
            logger.error(
                "Email delivery failed",
                extra={"recipient": notification.recipient, "error": str(e)},
            )
            raise NotificationDeliveryError(
                f"SMTP error: {e}",
                recipient=notification.recipient,
                provider=self.name,
            ) from e

    def send_bulk(
        self,
        notifications: list[Notification],
    ) -> list[NotificationResult]:
        """Send multiple email notifications efficiently.

        Uses a single SMTP connection for all messages.

        Args:
            notifications: List of notifications to send.

        Returns:
            List of NotificationResult for each notification.
        """
        if not notifications:
            return []

        results: list[NotificationResult] = []

        try:
            with self._create_connection() as smtp:
                for notification in notifications:
                    try:
                        msg = self._build_message(notification)
                        smtp.send_message(msg)
                        results.append(
                            self._create_success_result(
                                recipient=notification.recipient,
                                message_id=notification.idempotency_id,
                            )
                        )
                    except smtplib.SMTPException as e:
                        results.append(
                            self._create_failure_result(
                                recipient=notification.recipient,
                                error_message=str(e),
                            )
                        )

        except (NotificationConnectionError, NotificationTimeoutError):
            # Connection-level failure - mark all remaining as failed
            for notification in notifications[len(results) :]:
                results.append(
                    self._create_failure_result(
                        recipient=notification.recipient,
                        error_message="SMTP connection failed",
                        retry_after=60.0,
                    )
                )

        return results

    def health_check(self) -> bool:
        """Check if SMTP server is reachable.

        Returns:
            True if connection succeeds, False otherwise.
        """
        try:
            with self._create_connection() as smtp:
                smtp.noop()
            return True
        except Exception as e:
            logger.warning(f"SMTP health check failed: {e}")
            return False
