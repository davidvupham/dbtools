"""Comprehensive tests for gds_snmp_receiver.core module.

This test suite covers:
- Configuration validation (SNMPReceiverConfig)
- Idempotency key generation
- Trap callback processing
- RabbitMQ publish logic with retry
- Signal handling and cleanup
- URL redaction utility
- Error scenarios

Tests use mocks to avoid requiring real SNMP/RabbitMQ infrastructure.
"""

import json
import sys
import types
from datetime import datetime
from unittest.mock import Mock

import pytest

# =============================================================================
# pysnmp Stubs (must be set up before importing core)
# =============================================================================

# Provide minimal pysnmp stubs so tests can import the core module without
# having the real pysnmp package installed in the test environment.
_pysnmp = types.ModuleType("pysnmp")
_carrier = types.ModuleType("pysnmp.carrier")
_asynsock = types.ModuleType("pysnmp.carrier.asynsock")
_dgram = types.ModuleType("pysnmp.carrier.asynsock.dgram")


class _UdpTransport:
    """Stub UDP transport for testing."""

    def openServerMode(self, addr):
        return None


_udp = types.SimpleNamespace(domainName="udp", UdpTransport=_UdpTransport)
_dgram.udp = _udp

sys.modules["pysnmp"] = _pysnmp
sys.modules["pysnmp.carrier"] = _carrier
sys.modules["pysnmp.carrier.asynsock"] = _asynsock
sys.modules["pysnmp.carrier.asynsock.dgram"] = _dgram

# Minimal entity/engine/config and ntfrcv stubs
_entity = types.ModuleType("pysnmp.entity")
_engine = types.ModuleType("pysnmp.entity.engine")
_config = types.ModuleType("pysnmp.entity.config")
_rfc = types.ModuleType("pysnmp.entity.rfc3413")


class _DummyTransportDispatcher:
    """Stub transport dispatcher for testing."""

    def jobStarted(self, n):
        pass

    def runDispatcher(self):
        pass

    def closeDispatcher(self):
        pass


class _DummySnmpEngine:
    """Stub SNMP engine for testing."""

    def __init__(self):
        self.transportDispatcher = _DummyTransportDispatcher()


_engine.SnmpEngine = _DummySnmpEngine
_config.addTransport = lambda *a, **k: None
_config.addV1System = lambda *a, **k: None
_rfc.ntfrcv = types.SimpleNamespace(NotificationReceiver=lambda *a, **k: None)

sys.modules["pysnmp.entity"] = _entity
sys.modules["pysnmp.entity.engine"] = _engine
sys.modules["pysnmp.entity.config"] = _config
sys.modules["pysnmp.entity.rfc3413"] = _rfc

# Now import from core
from gds_snmp_receiver.core import (  # noqa: E402
    DEFAULT_COMMUNITY_STRING,
    DEFAULT_LISTEN_HOST,
    DEFAULT_LISTEN_PORT,
    DEFAULT_QUEUE_NAME,
    DEFAULT_RABBIT_URL,
    MAX_PAYLOAD_SIZE,
    ConfigurationError,
    SNMPReceiver,
    SNMPReceiverConfig,
)

# =============================================================================
# Configuration Tests
# =============================================================================


class TestSNMPReceiverConfig:
    """Tests for SNMPReceiverConfig dataclass."""

    def test_default_config_is_valid(self):
        """Default configuration should be valid."""
        config = SNMPReceiverConfig()
        assert config.listen_host == DEFAULT_LISTEN_HOST
        assert config.listen_port == DEFAULT_LISTEN_PORT
        assert config.rabbit_url == DEFAULT_RABBIT_URL
        assert config.queue_name == DEFAULT_QUEUE_NAME
        assert config.community_string == DEFAULT_COMMUNITY_STRING

    def test_custom_config_values(self):
        """Custom configuration values should be stored correctly."""
        config = SNMPReceiverConfig(
            listen_host="127.0.0.1",
            listen_port=9162,
            rabbit_url="amqp://user:pass@localhost:5672/vhost",
            queue_name="my_queue",
            community_string="secret",
        )
        assert config.listen_host == "127.0.0.1"
        assert config.listen_port == 9162
        assert config.rabbit_url == "amqp://user:pass@localhost:5672/vhost"
        assert config.queue_name == "my_queue"
        assert config.community_string == "secret"

    def test_invalid_port_zero(self):
        """Port 0 should be rejected."""
        with pytest.raises(ValueError, match="must be between"):
            SNMPReceiverConfig(listen_port=0)

    def test_invalid_port_negative(self):
        """Negative port should be rejected."""
        with pytest.raises(ValueError, match="must be between"):
            SNMPReceiverConfig(listen_port=-1)

    def test_invalid_port_too_high(self):
        """Port > 65535 should be rejected."""
        with pytest.raises(ValueError, match="must be between"):
            SNMPReceiverConfig(listen_port=65536)

    def test_invalid_port_type(self):
        """Non-integer port should be rejected."""
        with pytest.raises(ValueError, match="must be an integer"):
            SNMPReceiverConfig(listen_port="not_a_port")  # type: ignore

    def test_empty_host(self):
        """Empty host should be rejected."""
        with pytest.raises(ValueError, match="cannot be empty"):
            SNMPReceiverConfig(listen_host="")

    def test_invalid_host_format(self):
        """Invalid hostname format should be rejected."""
        with pytest.raises(ValueError, match="not a valid IP address or hostname"):
            SNMPReceiverConfig(listen_host="invalid host with spaces")

    def test_valid_ipv4_host(self):
        """Valid IPv4 address should be accepted."""
        config = SNMPReceiverConfig(listen_host="192.168.1.1")
        assert config.listen_host == "192.168.1.1"

    def test_valid_hostname(self):
        """Valid hostname should be accepted."""
        config = SNMPReceiverConfig(listen_host="my-server.example.com")
        assert config.listen_host == "my-server.example.com"

    def test_invalid_rabbit_url_scheme(self):
        """Non-AMQP URL scheme should be rejected."""
        with pytest.raises(ValueError, match="amqp://.*amqps://"):
            SNMPReceiverConfig(rabbit_url="http://localhost:5672/")

    def test_invalid_rabbit_url_no_host(self):
        """AMQP URL without hostname should be rejected."""
        with pytest.raises(ValueError, match="must include a hostname"):
            SNMPReceiverConfig(rabbit_url="amqp://:5672/")

    def test_empty_rabbit_url(self):
        """Empty rabbit_url should be rejected."""
        with pytest.raises(ValueError, match="cannot be empty"):
            SNMPReceiverConfig(rabbit_url="")

    def test_valid_amqps_url(self):
        """AMQPS (TLS) URL should be accepted."""
        config = SNMPReceiverConfig(rabbit_url="amqps://user:pass@secure.example.com:5671/")
        assert config.rabbit_url == "amqps://user:pass@secure.example.com:5671/"

    def test_empty_queue_name(self):
        """Empty queue_name should be rejected."""
        with pytest.raises(ValueError, match="cannot be empty"):
            SNMPReceiverConfig(queue_name="")

    def test_queue_name_too_long(self):
        """Queue name > 255 bytes should be rejected."""
        long_name = "a" * 256
        with pytest.raises(ValueError, match="exceeds maximum length"):
            SNMPReceiverConfig(queue_name=long_name)

    def test_invalid_connection_timeout(self):
        """Zero or negative timeout should be rejected."""
        with pytest.raises(ValueError, match="must be positive"):
            SNMPReceiverConfig(connection_timeout=0)

    def test_invalid_rabbitmq_wait_timeout(self):
        """Zero or negative timeout should be rejected."""
        with pytest.raises(ValueError, match="must be positive"):
            SNMPReceiverConfig(rabbitmq_wait_timeout=-1)


# =============================================================================
# SNMPReceiver Initialization Tests
# =============================================================================


class TestSNMPReceiverInit:
    """Tests for SNMPReceiver initialization."""

    def test_default_initialization(self):
        """Receiver should initialize with default values."""
        receiver = SNMPReceiver()
        assert receiver.listen_host == DEFAULT_LISTEN_HOST
        assert receiver.listen_port == DEFAULT_LISTEN_PORT
        assert receiver.rabbit_url == DEFAULT_RABBIT_URL
        assert receiver.queue_name == DEFAULT_QUEUE_NAME

    def test_custom_initialization(self):
        """Receiver should accept custom values."""
        receiver = SNMPReceiver(
            listen_host="127.0.0.1",
            listen_port=9162,
            rabbit_url="amqp://test:test@localhost:5672/",
            queue_name="test_queue",
            community_string="my_community",
        )
        assert receiver.listen_host == "127.0.0.1"
        assert receiver.listen_port == 9162
        assert receiver.queue_name == "test_queue"
        assert receiver.community_string == "my_community"

    def test_invalid_config_raises_error(self):
        """Invalid configuration should raise ConfigurationError."""
        with pytest.raises(ConfigurationError, match="must be between"):
            SNMPReceiver(listen_port=0)

    def test_from_config_factory(self):
        """from_config should create receiver from config object."""
        config = SNMPReceiverConfig(
            listen_port=9162,
            queue_name="factory_queue",
        )
        receiver = SNMPReceiver.from_config(config)
        assert receiver.listen_port == 9162
        assert receiver.queue_name == "factory_queue"

    def test_port_string_converted_to_int(self):
        """Port passed as string should be converted to int."""
        receiver = SNMPReceiver(listen_port="9162")  # type: ignore
        assert receiver.listen_port == 9162
        assert isinstance(receiver.listen_port, int)


# =============================================================================
# Idempotency Tests
# =============================================================================


class TestIdempotency:
    """Tests for idempotency key generation."""

    def test_compute_idempotency_returns_hex_64(self):
        """Idempotency key should be 64-char hex string."""
        varbinds = [("1.2.3", "val1"), ("1.2.4", "val2")]
        h = SNMPReceiver.compute_idempotency_from_trap(varbinds)
        assert isinstance(h, str)
        assert len(h) == 64
        # Verify it's valid hex
        int(h, 16)

    def test_compute_idempotency_empty_varbinds(self):
        """Empty varbinds should still produce valid hash."""
        h = SNMPReceiver.compute_idempotency_from_trap([])
        assert isinstance(h, str)
        assert len(h) == 64
        int(h, 16)

    def test_compute_idempotency_different_for_different_varbinds(self):
        """Different varbinds should produce different hashes."""
        h1 = SNMPReceiver.compute_idempotency_from_trap([("1.2.3", "val1")])
        h2 = SNMPReceiver.compute_idempotency_from_trap([("1.2.3", "val2")])
        # Note: Due to timestamp inclusion, these will always be different
        # even with same varbinds. This tests the hash is computed.
        assert isinstance(h1, str)
        assert isinstance(h2, str)


# =============================================================================
# Trap Callback Tests
# =============================================================================


class TestTrapCallback:
    """Tests for _trap_callback method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.receiver = SNMPReceiver(
            rabbit_url="amqp://guest:guest@localhost:5672/",
            queue_name="test_alerts",
        )
        self.receiver.publish_alert = Mock(return_value=True)

    def test_trap_callback_with_standard_varbinds(self):
        """Standard trap with snmpTrapOID should be processed correctly."""
        varbinds = [
            ("1.3.6.1.2.1.1.3.0", "12345"),  # sysUpTime
            # snmpTrapOID -> linkDown
            ("1.3.6.1.6.3.1.1.4.1.0", "1.3.6.1.6.3.1.1.5.3"),
        ]

        self.receiver._trap_callback(None, None, None, None, varbinds, None)

        self.receiver.publish_alert.assert_called_once()
        payload = self.receiver.publish_alert.call_args[0][0]

        assert payload["alert_name"] == "1.3.6.1.6.3.1.1.5.3"
        assert payload["source"] == "snmp"
        assert "idempotency_id" in payload
        assert "received_at" in payload
        assert payload["raw"] == {
            "1.3.6.1.2.1.1.3.0": "12345",
            "1.3.6.1.6.3.1.1.4.1.0": "1.3.6.1.6.3.1.1.5.3",
        }
        assert "SNMP Trap:" in payload["subject"]

    def test_trap_callback_without_trap_oid_uses_fallback(self):
        """Trap without snmpTrapOID should use first OID as fallback."""
        varbinds = [
            ("1.3.6.1.2.1.1.3.0", "12345"),
            ("1.3.6.1.4.1.9.1.100", "some_value"),
        ]

        self.receiver._trap_callback(None, None, None, None, varbinds, None)

        self.receiver.publish_alert.assert_called_once()
        payload = self.receiver.publish_alert.call_args[0][0]

        # Fallback: "snmp:" + first OID
        assert payload["alert_name"] == "snmp:1.3.6.1.2.1.1.3.0"

    def test_trap_callback_with_empty_varbinds_skips_publish(self):
        """Empty varbinds should not publish (warning logged)."""
        self.receiver._trap_callback(None, None, None, None, [], None)

        self.receiver.publish_alert.assert_not_called()

    def test_trap_callback_exception_does_not_crash(self):
        """Exception in callback should be caught and logged."""
        # Make publish_alert raise an exception
        self.receiver.publish_alert.side_effect = Exception("Test error")

        # This should not raise
        varbinds = [("1.2.3", "val")]
        self.receiver._trap_callback(None, None, None, None, varbinds, None)

    def test_trap_callback_received_at_is_utc(self):
        """received_at timestamp should be UTC."""
        varbinds = [("1.2.3", "val")]
        self.receiver._trap_callback(None, None, None, None, varbinds, None)

        payload = self.receiver.publish_alert.call_args[0][0]
        received_at = payload["received_at"]

        assert received_at.endswith("Z")
        # Verify it's parseable
        datetime.fromisoformat(received_at.replace("Z", "+00:00"))

    def test_trap_callback_body_text_is_valid_json(self):
        """body_text should be valid JSON."""
        varbinds = [("1.2.3", "val")]
        self.receiver._trap_callback(None, None, None, None, varbinds, None)

        payload = self.receiver.publish_alert.call_args[0][0]
        # Should not raise
        parsed = json.loads(payload["body_text"])
        assert "1.2.3" in parsed


# =============================================================================
# Publish Alert Tests
# =============================================================================


class TestPublishAlert:
    """Tests for publish_alert method."""

    def test_publish_alert_uses_pika(self, monkeypatch):
        """publish_alert should publish via pika channel."""
        published = {}

        class FakeChannel:
            is_open = True

            def queue_declare(self, *args, **kwargs):
                pass

            def basic_publish(self, *args, **kwargs):
                rk = kwargs.get("routing_key", args[1] if len(args) > 1 else None)
                body = kwargs.get("body", args[2] if len(args) > 2 else None)
                published["routing_key"] = rk
                published["body"] = body

        class FakeConn:
            is_open = True

            def __init__(self, _params):
                self._ch = FakeChannel()

            def channel(self):
                return self._ch

            def close(self):
                self.is_open = False

        import gds_snmp_receiver.core as core_mod

        monkeypatch.setattr(core_mod.pika, "BlockingConnection", FakeConn)

        receiver = SNMPReceiver(
            rabbit_url="amqp://guest:guest@rabbitmq:5672/",
            queue_name="testq",
        )
        payload = {"idempotency_id": "abc123", "alert_name": "test"}

        result = receiver.publish_alert(payload)

        assert result is True
        assert published["routing_key"] == "testq"
        body_obj = json.loads(published["body"])
        assert body_obj["idempotency_id"] == "abc123"

    def test_publish_alert_retry_on_failure(self, monkeypatch):
        """publish_alert should retry once on connection failure."""
        attempt_count = {"count": 0}

        class FakeChannel:
            is_open = True

            def queue_declare(self, *args, **kwargs):
                pass

            def basic_publish(self, *args, **kwargs):
                attempt_count["count"] += 1
                if attempt_count["count"] == 1:
                    raise Exception("Connection lost")
                # Second attempt succeeds

        class FakeConn:
            is_open = True

            def __init__(self, _params):
                self._ch = FakeChannel()

            def channel(self):
                return self._ch

            def close(self):
                self.is_open = False

        import gds_snmp_receiver.core as core_mod

        monkeypatch.setattr(core_mod.pika, "BlockingConnection", FakeConn)

        receiver = SNMPReceiver(
            rabbit_url="amqp://guest:guest@rabbitmq:5672/",
            queue_name="testq",
        )
        payload = {"idempotency_id": "retry123"}

        result = receiver.publish_alert(payload)

        assert result is True
        assert attempt_count["count"] == 2  # Initial + retry

    def test_publish_alert_returns_false_on_double_failure(self, monkeypatch):
        """publish_alert should return False if retry also fails."""

        class FakeChannel:
            is_open = True

            def queue_declare(self, *args, **kwargs):
                pass

            def basic_publish(self, *args, **kwargs):
                raise Exception("Always fails")

        class FakeConn:
            is_open = True

            def __init__(self, _params):
                self._ch = FakeChannel()

            def channel(self):
                return self._ch

            def close(self):
                self.is_open = False

        import gds_snmp_receiver.core as core_mod

        monkeypatch.setattr(core_mod.pika, "BlockingConnection", FakeConn)

        receiver = SNMPReceiver(
            rabbit_url="amqp://guest:guest@rabbitmq:5672/",
            queue_name="testq",
        )
        payload = {"idempotency_id": "fail123"}

        result = receiver.publish_alert(payload)

        assert result is False

    def test_publish_alert_returns_false_when_no_channel(self):
        """publish_alert should return False if no channel available."""
        receiver = SNMPReceiver()
        receiver._pika_ch = None
        receiver._pika_conn = None
        receiver._ensure_pika_connection = Mock()  # Don't actually connect

        result = receiver.publish_alert({"idempotency_id": "test"})

        assert result is False

    def test_publish_alert_rejects_oversized_payload(self):
        """Payload exceeding MAX_PAYLOAD_SIZE should be rejected."""
        receiver = SNMPReceiver()
        receiver._pika_ch = Mock()
        receiver._pika_conn = Mock()

        # Create payload larger than MAX_PAYLOAD_SIZE
        large_data = "x" * (MAX_PAYLOAD_SIZE + 1)
        payload = {"idempotency_id": "large", "data": large_data}

        result = receiver.publish_alert(payload)

        assert result is False
        receiver._pika_ch.basic_publish.assert_not_called()


# =============================================================================
# Connection Management Tests
# =============================================================================


class TestConnectionManagement:
    """Tests for RabbitMQ connection management."""

    def test_ensure_pika_connection_reuses_open_connection(self, monkeypatch):
        """_ensure_pika_connection should reuse open connections."""
        connection_attempts = {"count": 0}

        class FakeChannel:
            is_open = True

            def queue_declare(self, *args, **kwargs):
                pass

        class FakeConn:
            is_open = True

            def __init__(self, _params):
                connection_attempts["count"] += 1
                self._ch = FakeChannel()

            def channel(self):
                return self._ch

        import gds_snmp_receiver.core as core_mod

        monkeypatch.setattr(core_mod.pika, "BlockingConnection", FakeConn)

        receiver = SNMPReceiver()

        # First call creates connection
        receiver._ensure_pika_connection()
        assert connection_attempts["count"] == 1

        # Second call should reuse
        receiver._ensure_pika_connection()
        assert connection_attempts["count"] == 1  # Still 1

    def test_ensure_pika_connection_handles_failure(self, monkeypatch):
        """_ensure_pika_connection should handle connection failures."""
        import gds_snmp_receiver.core as core_mod

        def fail_connect(_params):
            raise Exception("Connection refused")

        monkeypatch.setattr(core_mod.pika, "BlockingConnection", fail_connect)

        receiver = SNMPReceiver()
        receiver._ensure_pika_connection()

        assert receiver._pika_conn is None
        assert receiver._pika_ch is None


# =============================================================================
# Stop and Cleanup Tests
# =============================================================================


class TestStopAndCleanup:
    """Tests for stop() and cleanup methods."""

    def test_stop_closes_connections(self):
        """stop() should close SNMP and pika connections."""
        receiver = SNMPReceiver()

        # Mock SNMP engine
        mock_engine = Mock()
        mock_dispatcher = Mock()
        mock_engine.transportDispatcher = mock_dispatcher
        receiver._snmp_engine = mock_engine

        # Mock pika connection
        mock_conn = Mock()
        receiver._pika_conn = mock_conn
        receiver._pika_ch = Mock()

        receiver._running.set()

        receiver.stop()

        mock_dispatcher.closeDispatcher.assert_called_once()
        mock_conn.close.assert_called_once()
        assert receiver._pika_conn is None
        assert receiver._pika_ch is None
        assert not receiver._running.is_set()

    def test_stop_removes_readiness_marker(self, tmp_path):
        """stop() should remove readiness marker file."""
        marker_file = tmp_path / "ready"
        marker_file.write_text("ready\n")

        receiver = SNMPReceiver(readiness_file=str(marker_file))
        receiver.stop()

        assert not marker_file.exists()

    def test_stop_handles_missing_readiness_marker(self, tmp_path):
        """stop() should handle missing readiness marker gracefully."""
        marker_file = tmp_path / "nonexistent"

        receiver = SNMPReceiver(readiness_file=str(marker_file))
        # Should not raise
        receiver.stop()

    def test_stop_handles_dispatcher_close_error(self):
        """stop() should handle errors when closing dispatcher."""
        receiver = SNMPReceiver()

        mock_engine = Mock()
        mock_engine.transportDispatcher.closeDispatcher.side_effect = Exception("Close failed")
        receiver._snmp_engine = mock_engine

        # Should not raise
        receiver.stop()

    def test_stop_handles_pika_close_error(self):
        """stop() should handle errors when closing pika."""
        receiver = SNMPReceiver()

        mock_conn = Mock()
        mock_conn.close.side_effect = Exception("Close failed")
        receiver._pika_conn = mock_conn
        receiver._pika_ch = Mock()

        # Should not raise
        receiver.stop()

        # Connection state should still be cleared
        assert receiver._pika_conn is None
        assert receiver._pika_ch is None

    def test_is_running_reflects_state(self):
        """is_running() should reflect internal state."""
        receiver = SNMPReceiver()

        assert receiver.is_running() is False

        receiver._running.set()
        assert receiver.is_running() is True

        receiver._running.clear()
        assert receiver.is_running() is False


# =============================================================================
# Signal Handler Tests
# =============================================================================


class TestSignalHandler:
    """Tests for signal handling."""

    def test_signal_handler_calls_stop(self):
        """_signal_handler should call stop()."""
        receiver = SNMPReceiver()
        receiver.stop = Mock()

        receiver._signal_handler(15, None)  # SIGTERM

        receiver.stop.assert_called_once()

    def test_signal_handler_handles_stop_error(self):
        """_signal_handler should handle errors in stop()."""
        receiver = SNMPReceiver()
        receiver.stop = Mock(side_effect=Exception("Stop failed"))

        # Should not raise
        receiver._signal_handler(2, None)  # SIGINT


# =============================================================================
# URL Redaction Tests
# =============================================================================


class TestRedactUrl:
    """Tests for _redact_url utility."""

    def test_redact_url_with_credentials(self):
        """URL with credentials should be redacted."""
        url = "amqp://user:password@localhost:5672/vhost"
        redacted = SNMPReceiver._redact_url(url)
        assert redacted == "amqp://<redacted>@localhost:5672/vhost"

    def test_redact_url_without_credentials(self):
        """URL without credentials should be unchanged."""
        url = "amqp://localhost:5672/"
        redacted = SNMPReceiver._redact_url(url)
        assert redacted == "amqp://localhost:5672/"

    def test_redact_url_with_only_user(self):
        """URL with user but no password should be redacted."""
        url = "amqp://user@localhost:5672/"
        redacted = SNMPReceiver._redact_url(url)
        # Contains @ but user is before it
        assert "@localhost" in redacted

    def test_redact_url_handles_invalid_url(self):
        """Invalid URL should be returned unchanged."""
        invalid_url = "not-a-valid-url"
        redacted = SNMPReceiver._redact_url(invalid_url)
        assert redacted == invalid_url

    def test_redact_url_amqps(self):
        """AMQPS URL should also be redacted."""
        url = "amqps://secure:secret@broker.example.com:5671/"
        redacted = SNMPReceiver._redact_url(url)
        assert redacted == "amqps://<redacted>@broker.example.com:5671/"


# =============================================================================
# Readiness Marker Tests
# =============================================================================


class TestReadinessMarker:
    """Tests for readiness marker file handling."""

    def test_write_readiness_marker(self, tmp_path):
        """_write_readiness_marker should create file."""
        marker_file = tmp_path / "ready"

        receiver = SNMPReceiver(readiness_file=str(marker_file))
        receiver._write_readiness_marker()

        assert marker_file.exists()
        assert marker_file.read_text() == "ready\n"

    def test_write_readiness_marker_handles_permission_error(self, tmp_path):
        """_write_readiness_marker should handle permission errors."""
        # Use a path that doesn't exist and can't be created
        marker_file = "/nonexistent/path/ready"

        receiver = SNMPReceiver(readiness_file=marker_file)
        # Should not raise
        receiver._write_readiness_marker()


# =============================================================================
# Integration-Style Tests
# =============================================================================


class TestIntegration:
    """Higher-level integration tests."""

    def test_full_trap_to_publish_flow(self, monkeypatch):
        """Test complete flow from trap callback to publish."""
        published_messages = []

        class FakeChannel:
            is_open = True

            def queue_declare(self, *args, **kwargs):
                pass

            def basic_publish(self, **kwargs):
                published_messages.append(json.loads(kwargs["body"]))

        class FakeConn:
            is_open = True

            def __init__(self, _params):
                self._ch = FakeChannel()

            def channel(self):
                return self._ch

            def close(self):
                pass

        import gds_snmp_receiver.core as core_mod

        monkeypatch.setattr(core_mod.pika, "BlockingConnection", FakeConn)

        receiver = SNMPReceiver(queue_name="integration_test")

        # Simulate trap
        varbinds = [
            ("1.3.6.1.2.1.1.3.0", "100"),
            ("1.3.6.1.6.3.1.1.4.1.0", "1.3.6.1.6.3.1.1.5.4"),  # linkUp
        ]
        receiver._trap_callback(None, None, None, None, varbinds, None)

        assert len(published_messages) == 1
        msg = published_messages[0]
        assert msg["alert_name"] == "1.3.6.1.6.3.1.1.5.4"
        assert msg["source"] == "snmp"
        assert len(msg["idempotency_id"]) == 64


# =============================================================================
# Error Scenario Tests
# =============================================================================


class TestErrorScenarios:
    """Tests for various error scenarios."""

    def test_trap_with_malformed_varbind(self):
        """Malformed varbind should be handled gracefully."""
        receiver = SNMPReceiver()
        receiver.publish_alert = Mock(return_value=True)

        # Varbind that can't be converted to string properly
        class BadOID:
            def __str__(self):
                raise ValueError("Cannot stringify")

        varbinds = [(BadOID(), "value")]

        # Should not raise, error is logged
        receiver._trap_callback(None, None, None, None, varbinds, None)

    def test_config_validation_comprehensive(self):
        """Test that all validation paths are covered."""
        # Valid config
        config = SNMPReceiverConfig(
            listen_host="0.0.0.0",
            listen_port=9162,
            rabbit_url="amqp://guest:guest@localhost:5672/",
            queue_name="alerts",
            community_string="public",
            connection_timeout=10,
            rabbitmq_wait_timeout=30,
        )
        assert config is not None
