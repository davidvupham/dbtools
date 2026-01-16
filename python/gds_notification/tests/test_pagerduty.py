"""Tests for PagerDuty provider."""

import json
from unittest.mock import MagicMock, patch

import pytest
from gds_notification.exceptions import (
    NotificationConfigError,
    NotificationDeliveryError,
    NotificationRateLimitError,
    NotificationTimeoutError,
)
from gds_notification.providers.base import (
    NotificationPriority,
    NotificationStatus,
)
from gds_notification.providers.pagerduty import (
    PagerDutyProvider,
    PagerDutySeverity,
)


class TestPagerDutyProvider:
    """Tests for PagerDutyProvider."""

    def test_init_requires_routing_key(self):
        """Test that routing key is required."""
        with pytest.raises(NotificationConfigError, match="routing key is required"):
            PagerDutyProvider(routing_key="")

    def test_init_success(self):
        """Test successful initialization."""
        provider = PagerDutyProvider(
            routing_key="test-routing-key",
            timeout=60,
            default_severity=PagerDutySeverity.WARNING,
        )
        assert provider.name == "pagerduty"
        assert provider.routing_key == "test-routing-key"
        assert provider.timeout == 60
        assert provider.default_severity == PagerDutySeverity.WARNING

    def test_priority_mapping(self):
        """Test priority to severity mapping."""
        provider = PagerDutyProvider(routing_key="test-key")

        assert (
            provider._map_priority_to_severity(NotificationPriority.LOW) == PagerDutySeverity.INFO
        )
        assert (
            provider._map_priority_to_severity(NotificationPriority.NORMAL)
            == PagerDutySeverity.WARNING
        )
        assert (
            provider._map_priority_to_severity(NotificationPriority.HIGH) == PagerDutySeverity.ERROR
        )
        assert (
            provider._map_priority_to_severity(NotificationPriority.CRITICAL)
            == PagerDutySeverity.CRITICAL
        )
        assert (
            provider._map_priority_to_severity(NotificationPriority.EMERGENCY)
            == PagerDutySeverity.CRITICAL
        )

    def test_build_event_payload(self, sample_notification):
        """Test event payload building."""
        provider = PagerDutyProvider(routing_key="test-key")
        payload = provider._build_event_payload(sample_notification)

        assert payload["routing_key"] == "test-key"
        assert payload["event_action"] == "trigger"
        assert payload["dedup_key"] == sample_notification.idempotency_id
        assert payload["payload"]["summary"] == sample_notification.subject
        assert payload["payload"]["severity"] == "warning"
        assert payload["payload"]["source"] == "gds_notification"

    def test_send_success(self, sample_notification):
        """Test successful event send."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.json.return_value = {
            "status": "success",
            "message": "Event processed",
            "dedup_key": "test-12345",
        }
        mock_session.post.return_value = mock_response

        provider = PagerDutyProvider(routing_key="test-key")
        provider._session = mock_session

        result = provider.send(sample_notification)

        assert result.status == NotificationStatus.SENT
        assert result.metadata["dedup_key"] == "test-12345"
        mock_session.post.assert_called_once()

    def test_send_rate_limited(self, sample_notification):
        """Test rate limiting handling."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "120"}
        mock_session.post.return_value = mock_response

        provider = PagerDutyProvider(routing_key="test-key")
        provider._session = mock_session

        with pytest.raises(NotificationRateLimitError) as exc_info:
            provider.send(sample_notification)

        assert exc_info.value.retry_after_seconds == 120.0

    def test_send_bad_request(self, sample_notification):
        """Test bad request handling."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Invalid routing key"}
        mock_session.post.return_value = mock_response

        provider = PagerDutyProvider(routing_key="test-key")
        provider._session = mock_session

        with pytest.raises(NotificationDeliveryError, match="rejected event"):
            provider.send(sample_notification)

    def test_send_timeout(self, sample_notification):
        """Test timeout handling."""
        import requests

        mock_session = MagicMock()
        mock_session.post.side_effect = requests.exceptions.Timeout("Timeout")

        provider = PagerDutyProvider(routing_key="test-key")
        provider._session = mock_session

        with pytest.raises(NotificationTimeoutError):
            provider.send(sample_notification)

    def test_trigger_method(self, sample_notification):
        """Test trigger convenience method."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.json.return_value = {"status": "success", "dedup_key": "key-1"}
        mock_session.post.return_value = mock_response

        provider = PagerDutyProvider(routing_key="test-key")
        provider._session = mock_session

        result = provider.trigger(sample_notification)

        assert result.is_success()
        # Verify event_action is trigger
        call_args = mock_session.post.call_args
        payload = json.loads(call_args[1]["data"])
        assert payload["event_action"] == "trigger"

    def test_acknowledge_method(self):
        """Test acknowledge convenience method."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.json.return_value = {"status": "success", "dedup_key": "key-1"}
        mock_session.post.return_value = mock_response

        provider = PagerDutyProvider(routing_key="test-key")
        provider._session = mock_session

        result = provider.acknowledge("key-1")

        assert result.is_success()
        call_args = mock_session.post.call_args
        payload = json.loads(call_args[1]["data"])
        assert payload["event_action"] == "acknowledge"
        assert payload["dedup_key"] == "key-1"

    def test_resolve_method(self):
        """Test resolve convenience method."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.json.return_value = {"status": "success", "dedup_key": "key-1"}
        mock_session.post.return_value = mock_response

        provider = PagerDutyProvider(routing_key="test-key")
        provider._session = mock_session

        result = provider.resolve("key-1")

        assert result.is_success()
        call_args = mock_session.post.call_args
        payload = json.loads(call_args[1]["data"])
        assert payload["event_action"] == "resolve"

    def test_context_manager(self):
        """Test context manager usage."""
        with PagerDutyProvider(routing_key="test-key") as provider:
            assert provider.name == "pagerduty"
        # Session should be closed after exit
        assert provider._session is None

    def test_health_check_success(self):
        """Test successful health check."""
        import requests as real_requests

        with patch.object(real_requests, "head") as mock_head:
            mock_response = MagicMock()
            mock_response.status_code = 405  # Method not allowed is OK
            mock_head.return_value = mock_response

            provider = PagerDutyProvider(routing_key="test-key")
            assert provider.health_check() is True

    def test_health_check_failure(self):
        """Test health check failure."""
        import requests as real_requests

        with patch.object(real_requests, "head", side_effect=Exception("Connection failed")):
            provider = PagerDutyProvider(routing_key="test-key")
            assert provider.health_check() is False
