"""Tests for exception classes."""

import pytest
from gds_notification.exceptions import (
    GdsNotificationError,
    NotificationConfigError,
    NotificationConnectionError,
    NotificationDeliveryError,
    NotificationRateLimitError,
    NotificationTimeoutError,
    NotificationValidationError,
)


class TestGdsNotificationError:
    """Tests for base exception class."""

    def test_basic_message(self):
        """Test exception with basic message."""
        error = GdsNotificationError("Test error")
        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.details == {}

    def test_with_details(self):
        """Test exception with details."""
        error = GdsNotificationError("Test error", details={"key": "value"})
        assert "Test error" in str(error)
        assert "key" in str(error)
        assert error.details == {"key": "value"}

    def test_inheritance(self):
        """Test all exceptions inherit from base."""
        assert issubclass(NotificationConfigError, GdsNotificationError)
        assert issubclass(NotificationConnectionError, GdsNotificationError)
        assert issubclass(NotificationDeliveryError, GdsNotificationError)
        assert issubclass(NotificationTimeoutError, GdsNotificationError)
        assert issubclass(NotificationValidationError, GdsNotificationError)
        assert issubclass(NotificationRateLimitError, GdsNotificationError)


class TestNotificationDeliveryError:
    """Tests for delivery error class."""

    def test_with_recipient_and_provider(self):
        """Test error with recipient and provider."""
        error = NotificationDeliveryError(
            "Delivery failed",
            recipient="test@example.com",
            provider="smtp",
        )
        assert error.recipient == "test@example.com"
        assert error.provider == "smtp"

    def test_without_recipient(self):
        """Test error without recipient."""
        error = NotificationDeliveryError("Delivery failed")
        assert error.recipient is None
        assert error.provider is None


class TestNotificationTimeoutError:
    """Tests for timeout error class."""

    def test_with_timeout_seconds(self):
        """Test error with timeout value."""
        error = NotificationTimeoutError(
            "Connection timed out",
            timeout_seconds=30.0,
        )
        assert error.timeout_seconds == 30.0

    def test_without_timeout_seconds(self):
        """Test error without timeout value."""
        error = NotificationTimeoutError("Connection timed out")
        assert error.timeout_seconds is None


class TestNotificationValidationError:
    """Tests for validation error class."""

    def test_with_field_and_value(self):
        """Test error with field and value."""
        error = NotificationValidationError(
            "Invalid recipient",
            field="recipient",
            value="invalid-email",
        )
        assert error.field == "recipient"
        assert error.value == "invalid-email"

    def test_without_field(self):
        """Test error without field."""
        error = NotificationValidationError("Validation failed")
        assert error.field is None
        assert error.value is None


class TestNotificationRateLimitError:
    """Tests for rate limit error class."""

    def test_with_retry_after(self):
        """Test error with retry after."""
        error = NotificationRateLimitError(
            "Rate limit exceeded",
            retry_after_seconds=120.0,
        )
        assert error.retry_after_seconds == 120.0

    def test_without_retry_after(self):
        """Test error without retry after."""
        error = NotificationRateLimitError("Rate limit exceeded")
        assert error.retry_after_seconds is None


class TestExceptionCatching:
    """Tests for exception catching behavior."""

    def test_catch_all_with_base(self):
        """Test catching all exceptions with base class."""
        exceptions = [
            NotificationConfigError("config"),
            NotificationConnectionError("connection"),
            NotificationDeliveryError("delivery"),
            NotificationTimeoutError("timeout"),
            NotificationValidationError("validation"),
            NotificationRateLimitError("rate limit"),
        ]

        for exc in exceptions:
            try:
                raise exc
            except GdsNotificationError as e:
                assert e.message is not None
            except Exception:
                pytest.fail(f"Exception {type(exc).__name__} not caught by base class")

    def test_catch_specific(self):
        """Test catching specific exceptions."""
        with pytest.raises(NotificationDeliveryError):
            raise NotificationDeliveryError("Delivery failed")

        with pytest.raises(NotificationTimeoutError):
            raise NotificationTimeoutError("Timeout")
