"""Pytest configuration and fixtures for gds_notification tests."""

from unittest.mock import MagicMock

import pytest
from gds_notification.providers.base import (
    Notification,
    NotificationPriority,
    NotificationResult,
    NotificationStatus,
)


@pytest.fixture
def sample_notification() -> Notification:
    """Create a sample notification for testing."""
    return Notification(
        recipient="test@example.com",
        subject="Test Alert",
        body="This is a test alert message.",
        body_html="<p>This is a test alert message.</p>",
        priority=NotificationPriority.NORMAL,
        alert_name="TestAlert",
        db_instance_id=42,
        idempotency_id="test-12345",
    )


@pytest.fixture
def critical_notification() -> Notification:
    """Create a critical priority notification for testing."""
    return Notification(
        recipient="oncall@example.com",
        subject="CRITICAL: Database Down",
        body="Production database is unresponsive. Immediate action required.",
        priority=NotificationPriority.CRITICAL,
        alert_name="DatabaseDown",
        db_instance_id=1,
        idempotency_id="critical-alert-001",
    )


@pytest.fixture
def mock_smtp_server():
    """Create a mock SMTP server for testing."""
    mock = MagicMock()
    mock.send_message = MagicMock()
    mock.noop = MagicMock()
    mock.__enter__ = MagicMock(return_value=mock)
    mock.__exit__ = MagicMock(return_value=False)
    return mock


@pytest.fixture
def mock_requests_session():
    """Create a mock requests session for testing."""
    mock = MagicMock()
    mock.post = MagicMock()
    mock.headers = {}
    return mock


@pytest.fixture
def mock_zeep_client():
    """Create a mock Zeep SOAP client for testing."""
    mock = MagicMock()
    mock.service = MagicMock()
    mock.service.sendBroadcast = MagicMock()
    mock.service.sendNotification = MagicMock()
    mock.service.getNotificationStatus = MagicMock()
    return mock


@pytest.fixture
def success_result() -> NotificationResult:
    """Create a successful notification result for testing."""
    return NotificationResult(
        status=NotificationStatus.SENT,
        recipient="test@example.com",
        provider="test",
        message_id="msg-12345",
    )


@pytest.fixture
def failure_result() -> NotificationResult:
    """Create a failed notification result for testing."""
    return NotificationResult(
        status=NotificationStatus.FAILED,
        recipient="test@example.com",
        provider="test",
        error_message="Test error",
    )
