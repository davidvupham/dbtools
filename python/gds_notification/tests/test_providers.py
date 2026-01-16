"""Tests for notification providers."""

from unittest.mock import MagicMock, patch

import pytest
from gds_notification.exceptions import (
    NotificationConfigError,
    NotificationConnectionError,
    NotificationDeliveryError,
)
from gds_notification.providers.base import (
    Notification,
    NotificationPriority,
    NotificationResult,
    NotificationStatus,
)
from gds_notification.providers.smtp import SMTPProvider


class TestSMTPProvider:
    """Tests for SMTPProvider."""

    def test_init_requires_host(self):
        """Test that host is required."""
        with pytest.raises(NotificationConfigError, match="SMTP host is required"):
            SMTPProvider(host="")

    def test_init_rejects_tls_and_ssl(self):
        """Test that TLS and SSL cannot both be enabled."""
        with pytest.raises(NotificationConfigError, match="Cannot use both TLS and SSL"):
            SMTPProvider(host="smtp.example.com", use_tls=True, use_ssl=True)

    def test_init_success(self):
        """Test successful initialization."""
        provider = SMTPProvider(
            host="smtp.example.com",
            port=587,
            username="user",
            password="pass",
            from_address="alerts@example.com",
        )
        assert provider.name == "smtp"
        assert provider.host == "smtp.example.com"
        assert provider.port == 587
        assert provider.from_address == "alerts@example.com"

    def test_build_message(self, sample_notification):
        """Test email message building."""
        provider = SMTPProvider(
            host="smtp.example.com",
            from_address="alerts@example.com",
        )
        msg = provider._build_message(sample_notification)

        assert msg["From"] == "alerts@example.com"
        assert msg["To"] == sample_notification.recipient
        assert msg["Subject"] == sample_notification.subject
        assert msg["X-Idempotency-ID"] == sample_notification.idempotency_id
        assert msg["X-Alert-Name"] == sample_notification.alert_name

    def test_build_message_priority_headers(self):
        """Test priority headers in email message."""
        provider = SMTPProvider(host="smtp.example.com")

        # Test critical priority
        notification = Notification(
            recipient="test@example.com",
            subject="Critical",
            body="Critical message",
            priority=NotificationPriority.CRITICAL,
        )
        msg = provider._build_message(notification)
        assert msg["X-Priority"] == "1"
        assert msg["Importance"] == "urgent"

        # Test low priority
        notification.priority = NotificationPriority.LOW
        msg = provider._build_message(notification)
        assert msg["X-Priority"] == "5"
        assert msg["Importance"] == "non-urgent"

    @patch("gds_notification.providers.smtp.smtplib.SMTP")
    def test_send_success(self, mock_smtp_class, sample_notification):
        """Test successful email send."""
        mock_smtp = MagicMock()
        mock_smtp.__enter__ = MagicMock(return_value=mock_smtp)
        mock_smtp.__exit__ = MagicMock(return_value=False)
        mock_smtp_class.return_value = mock_smtp

        provider = SMTPProvider(
            host="smtp.example.com",
            port=587,
            use_tls=False,
        )
        result = provider.send(sample_notification)

        assert result.status == NotificationStatus.SENT
        assert result.recipient == sample_notification.recipient
        assert result.provider == "smtp"
        mock_smtp.send_message.assert_called_once()

    @patch("gds_notification.providers.smtp.smtplib.SMTP")
    def test_send_connection_failure(self, mock_smtp_class, sample_notification):
        """Test connection failure handling."""
        import smtplib

        mock_smtp_class.side_effect = smtplib.SMTPException("Connection refused")

        provider = SMTPProvider(host="smtp.example.com", use_tls=False)

        with pytest.raises(NotificationConnectionError, match="SMTP connection failed"):
            provider.send(sample_notification)

    @patch("gds_notification.providers.smtp.smtplib.SMTP")
    def test_send_recipient_refused(self, mock_smtp_class, sample_notification):
        """Test recipient refused handling."""
        import smtplib

        mock_smtp = MagicMock()
        mock_smtp.__enter__ = MagicMock(return_value=mock_smtp)
        mock_smtp.__exit__ = MagicMock(return_value=False)
        mock_smtp.send_message.side_effect = smtplib.SMTPRecipientsRefused(
            {"test@example.com": (550, "User unknown")}
        )
        mock_smtp_class.return_value = mock_smtp

        provider = SMTPProvider(host="smtp.example.com", use_tls=False)

        with pytest.raises(NotificationDeliveryError, match="Recipients refused"):
            provider.send(sample_notification)

    @patch("gds_notification.providers.smtp.smtplib.SMTP")
    def test_send_bulk_success(self, mock_smtp_class):
        """Test bulk email sending."""
        mock_smtp = MagicMock()
        mock_smtp.__enter__ = MagicMock(return_value=mock_smtp)
        mock_smtp.__exit__ = MagicMock(return_value=False)
        mock_smtp_class.return_value = mock_smtp

        provider = SMTPProvider(host="smtp.example.com", use_tls=False)

        notifications = [
            Notification(
                recipient=f"user{i}@example.com",
                subject="Bulk Test",
                body="Bulk message",
            )
            for i in range(3)
        ]

        results = provider.send_bulk(notifications)

        assert len(results) == 3
        assert all(r.status == NotificationStatus.SENT for r in results)
        assert mock_smtp.send_message.call_count == 3

    @patch("gds_notification.providers.smtp.smtplib.SMTP")
    def test_health_check_success(self, mock_smtp_class):
        """Test successful health check."""
        mock_smtp = MagicMock()
        mock_smtp.__enter__ = MagicMock(return_value=mock_smtp)
        mock_smtp.__exit__ = MagicMock(return_value=False)
        mock_smtp_class.return_value = mock_smtp

        provider = SMTPProvider(host="smtp.example.com", use_tls=False)
        assert provider.health_check() is True
        mock_smtp.noop.assert_called_once()

    @patch("gds_notification.providers.smtp.smtplib.SMTP")
    def test_health_check_failure(self, mock_smtp_class):
        """Test health check failure."""
        mock_smtp_class.side_effect = Exception("Connection failed")

        provider = SMTPProvider(host="smtp.example.com", use_tls=False)
        assert provider.health_check() is False


class TestNotificationResult:
    """Tests for NotificationResult."""

    def test_is_success_sent(self, success_result):
        """Test is_success for sent status."""
        assert success_result.is_success() is True

    def test_is_success_delivered(self):
        """Test is_success for delivered status."""
        result = NotificationResult(
            status=NotificationStatus.DELIVERED,
            recipient="test@example.com",
            provider="test",
        )
        assert result.is_success() is True

    def test_is_success_failed(self, failure_result):
        """Test is_success for failed status."""
        assert failure_result.is_success() is False

    def test_is_retriable_rate_limited(self):
        """Test is_retriable for rate limited status."""
        result = NotificationResult(
            status=NotificationStatus.RATE_LIMITED,
            recipient="test@example.com",
            provider="test",
            retry_after=60.0,
        )
        assert result.is_retriable() is True

    def test_is_retriable_failed_with_retry(self):
        """Test is_retriable for failed with retry_after."""
        result = NotificationResult(
            status=NotificationStatus.FAILED,
            recipient="test@example.com",
            provider="test",
            retry_after=30.0,
        )
        assert result.is_retriable() is True

    def test_is_retriable_failed_no_retry(self, failure_result):
        """Test is_retriable for failed without retry_after."""
        assert failure_result.is_retriable() is False
