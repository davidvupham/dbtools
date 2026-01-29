"""Tests for MIR3 provider."""

from unittest.mock import MagicMock, patch

import pytest

from gds_notification.exceptions import (
    NotificationConfigError,
)
from gds_notification.providers.base import (
    NotificationPriority,
    NotificationStatus,
)
from gds_notification.providers.mir3 import (
    MIR3NotificationMethod,
    MIR3NotificationStatus,
    MIR3Provider,
)


class TestMIR3Provider:
    """Tests for MIR3Provider."""

    def test_init_requires_wsdl_url(self):
        """Test that WSDL URL is required."""
        with pytest.raises(NotificationConfigError, match="WSDL URL is required"):
            MIR3Provider(wsdl_url="", username="user", password="pass")

    def test_init_requires_username(self):
        """Test that username is required."""
        with pytest.raises(NotificationConfigError, match="username is required"):
            MIR3Provider(wsdl_url="http://example.com", username="", password="pass")

    def test_init_requires_password(self):
        """Test that password is required."""
        with pytest.raises(NotificationConfigError, match="password is required"):
            MIR3Provider(wsdl_url="http://example.com", username="user", password="")

    def test_init_success(self):
        """Test successful initialization."""
        provider = MIR3Provider(
            wsdl_url="http://example.com/wsdl",
            username="user",
            password="pass",
            default_method=MIR3NotificationMethod.FIRST_RESPONSE,
            timeout=120,
        )
        assert provider.name == "mir3"
        assert provider.wsdl_url == "http://example.com/wsdl"
        assert provider.username == "user"
        assert provider.default_method == MIR3NotificationMethod.FIRST_RESPONSE
        assert provider.timeout == 120

    def test_priority_mapping(self):
        """Test priority to MIR3 priority mapping."""
        provider = MIR3Provider(
            wsdl_url="http://example.com",
            username="user",
            password="pass",
        )

        assert provider._map_priority_to_mir3(NotificationPriority.LOW) == "Low"
        assert provider._map_priority_to_mir3(NotificationPriority.NORMAL) == "Normal"
        assert provider._map_priority_to_mir3(NotificationPriority.HIGH) == "High"
        assert provider._map_priority_to_mir3(NotificationPriority.CRITICAL) == "Critical"
        assert provider._map_priority_to_mir3(NotificationPriority.EMERGENCY) == "Emergency"

    def test_method_mapping(self):
        """Test notification method to API method mapping."""
        provider = MIR3Provider(
            wsdl_url="http://example.com",
            username="user",
            password="pass",
        )

        assert provider._map_method_to_mir3(MIR3NotificationMethod.BROADCAST) == "sendBroadcast"
        assert (
            provider._map_method_to_mir3(MIR3NotificationMethod.FIRST_RESPONSE)
            == "sendFirstResponse"
        )
        assert provider._map_method_to_mir3(MIR3NotificationMethod.CALLOUT) == "sendCallout"
        assert provider._map_method_to_mir3(MIR3NotificationMethod.BULLETIN_BOARD) == "sendBulletin"

    def test_extract_report_id_from_object(self):
        """Test report ID extraction from response object."""
        provider = MIR3Provider(
            wsdl_url="http://example.com",
            username="user",
            password="pass",
        )

        # Test notificationReportId attribute
        mock_response = MagicMock()
        mock_response.notificationReportId = "12345"
        assert provider._extract_report_id(mock_response) == "12345"

    def test_extract_report_id_from_dict(self):
        """Test report ID extraction from dict response."""
        provider = MIR3Provider(
            wsdl_url="http://example.com",
            username="user",
            password="pass",
        )

        response = {"notificationReportId": "dict-12345"}
        assert provider._extract_report_id(response) == "dict-12345"

        response = {"reportId": "dict-67890"}
        assert provider._extract_report_id(response) == "dict-67890"

    def test_send_success(self, sample_notification):
        """Test successful MIR3 notification send."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.notificationReportId = "mir3-12345"
        mock_client.service.sendBroadcast.return_value = mock_response

        provider = MIR3Provider(
            wsdl_url="http://example.com/wsdl",
            username="user",
            password="pass",
        )
        # Inject mock client directly
        provider._client = mock_client

        result = provider.send(sample_notification)

        assert result.status == NotificationStatus.SENT
        assert result.metadata["report_id"] == "mir3-12345"
        mock_client.service.sendBroadcast.assert_called_once()

    def test_send_with_method_override(self, sample_notification):
        """Test send with method override."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.notificationReportId = "mir3-callout-123"
        mock_client.service.sendCallout.return_value = mock_response

        provider = MIR3Provider(
            wsdl_url="http://example.com/wsdl",
            username="user",
            password="pass",
        )
        provider._client = mock_client

        result = provider.send(sample_notification, method=MIR3NotificationMethod.CALLOUT)

        assert result.is_success()
        assert result.metadata["method"] == "callout"

    def test_get_notification_status(self):
        """Test getting notification status."""
        mock_client = MagicMock()
        mock_status = MagicMock()
        mock_status.status = "completed"
        mock_status.sentCount = 10
        mock_status.respondedCount = 5
        mock_status.failedCount = 1
        mock_client.service.getNotificationStatus.return_value = mock_status

        provider = MIR3Provider(
            wsdl_url="http://example.com/wsdl",
            username="user",
            password="pass",
        )
        provider._client = mock_client

        status = provider.get_notification_status("report-123")

        assert isinstance(status, MIR3NotificationStatus)
        assert status.report_id == "report-123"
        assert status.status == "completed"
        assert status.sent_count == 10
        assert status.responded_count == 5
        assert status.failed_count == 1

    def test_zeep_not_installed(self):
        """Test error when zeep is not installed."""
        provider = MIR3Provider(
            wsdl_url="http://example.com/wsdl",
            username="user",
            password="pass",
        )

        with (
            patch.dict("sys.modules", {"zeep": None}),
            patch("builtins.__import__", side_effect=ImportError("No module named 'zeep'")),
            pytest.raises(NotificationConfigError, match="zeep library is required"),
        ):
            provider._get_client()

    def test_context_manager(self):
        """Test context manager usage."""
        with MIR3Provider(
            wsdl_url="http://example.com/wsdl",
            username="user",
            password="pass",
        ) as provider:
            assert provider.name == "mir3"
        # Client should be cleaned up
        assert provider._client is None

    def test_health_check_success(self):
        """Test successful health check."""
        mock_client = MagicMock()

        provider = MIR3Provider(
            wsdl_url="http://example.com/wsdl",
            username="user",
            password="pass",
        )
        provider._client = mock_client

        assert provider.health_check() is True

    def test_health_check_failure(self):
        """Test health check failure."""
        provider = MIR3Provider(
            wsdl_url="http://invalid.example.com/wsdl",
            username="user",
            password="pass",
        )

        # Mock the client creation to fail
        with patch.object(provider, "_get_client", side_effect=Exception("WSDL load failed")):
            assert provider.health_check() is False
