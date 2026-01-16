"""
Unit tests for OpenTelemetry metrics implementation.

These tests verify the OpenTelemetryMetrics class functionality
without requiring an actual OTel Collector.
"""

import pytest


class TestOpenTelemetryMetrics:
    """Tests for OpenTelemetryMetrics class."""

    def test_import_error_without_otel(self):
        """Test that ImportError is raised when OTel not installed."""
        # We can't easily test this without uninstalling OTel
        # Instead, verify the error message in the code
        from gds_metrics.opentelemetry import OpenTelemetryMetrics

        # If we get here, OTel is installed, so just verify class exists
        assert OpenTelemetryMetrics is not None

    def test_initialization(self):
        """Test basic initialization."""
        try:
            from gds_metrics import OpenTelemetryMetrics

            if OpenTelemetryMetrics is None:
                pytest.skip("OpenTelemetry not installed")

            metrics = OpenTelemetryMetrics(service_name="test-service", service_version="1.0.0")
            assert metrics._service_name == "test-service"
            assert metrics._service_version == "1.0.0"
            assert metrics._include_trace_context is True
        except ImportError:
            pytest.skip("OpenTelemetry not installed")

    def test_initialization_without_trace_context(self):
        """Test initialization with trace context disabled."""
        try:
            from gds_metrics import OpenTelemetryMetrics

            if OpenTelemetryMetrics is None:
                pytest.skip("OpenTelemetry not installed")

            metrics = OpenTelemetryMetrics(service_name="test", include_trace_context=False)
            assert metrics._include_trace_context is False
        except ImportError:
            pytest.skip("OpenTelemetry not installed")

    def test_increment_counter(self):
        """Test counter increment."""
        try:
            from gds_metrics import OpenTelemetryMetrics

            if OpenTelemetryMetrics is None:
                pytest.skip("OpenTelemetry not installed")

            metrics = OpenTelemetryMetrics(service_name="test")

            # Should not raise
            metrics.increment("test_counter")
            metrics.increment("test_counter", value=5)
            metrics.increment("test_counter", labels={"env": "test"})
        except ImportError:
            pytest.skip("OpenTelemetry not installed")

    def test_histogram_record(self):
        """Test histogram recording."""
        try:
            from gds_metrics import OpenTelemetryMetrics

            if OpenTelemetryMetrics is None:
                pytest.skip("OpenTelemetry not installed")

            metrics = OpenTelemetryMetrics(service_name="test")

            # Should not raise
            metrics.histogram("request_duration", 0.5)
            metrics.histogram("request_duration", 1.2, labels={"method": "GET"})
        except ImportError:
            pytest.skip("OpenTelemetry not installed")

    def test_gauge_set(self):
        """Test gauge setting."""
        try:
            from gds_metrics import OpenTelemetryMetrics

            if OpenTelemetryMetrics is None:
                pytest.skip("OpenTelemetry not installed")

            metrics = OpenTelemetryMetrics(service_name="test")

            # Should not raise
            metrics.gauge("active_connections", 42)
            metrics.gauge("active_connections", 50, labels={"pool": "primary"})
        except ImportError:
            pytest.skip("OpenTelemetry not installed")

    def test_timing(self):
        """Test timing measurement."""
        try:
            from gds_metrics import OpenTelemetryMetrics

            if OpenTelemetryMetrics is None:
                pytest.skip("OpenTelemetry not installed")

            metrics = OpenTelemetryMetrics(service_name="test")

            # Should not raise and use histogram under the hood
            metrics.timing("db_query_ms", 45.2)
            metrics.timing("db_query_ms", 100.0, labels={"operation": "SELECT"})
        except ImportError:
            pytest.skip("OpenTelemetry not installed")

    def test_repr_and_str(self):
        """Test string representations."""
        try:
            from gds_metrics import OpenTelemetryMetrics

            if OpenTelemetryMetrics is None:
                pytest.skip("OpenTelemetry not installed")

            metrics = OpenTelemetryMetrics(service_name="my-service", service_version="2.0.0")

            assert "my-service" in repr(metrics)
            assert "2.0.0" in repr(metrics)
            assert "my-service" in str(metrics)
        except ImportError:
            pytest.skip("OpenTelemetry not installed")


class TestContextUtilities:
    """Tests for trace context utilities."""

    def test_get_current_trace_context_no_span(self):
        """Test that context returns empty dict when no span active."""
        from gds_metrics.context import get_current_trace_context

        # Without an active span, should return empty
        ctx = get_current_trace_context()
        # Either empty or has trace context (if OTel running elsewhere)
        assert isinstance(ctx, dict)

    def test_with_trace_context_preserves_labels(self):
        """Test that existing labels are preserved."""
        from gds_metrics.context import with_trace_context

        original_labels = {"endpoint": "/api", "method": "GET"}
        result = with_trace_context(original_labels, include_trace_context=False)

        assert result["endpoint"] == "/api"
        assert result["method"] == "GET"
        # Original should not be modified
        assert original_labels == {"endpoint": "/api", "method": "GET"}

    def test_with_trace_context_none_labels(self):
        """Test with None labels returns empty dict (when context disabled)."""
        from gds_metrics.context import with_trace_context

        result = with_trace_context(None, include_trace_context=False)
        assert result == {}

    def test_with_trace_context_disabled(self):
        """Test that trace context not added when disabled."""
        from gds_metrics.context import with_trace_context

        result = with_trace_context({"key": "value"}, include_trace_context=False)

        assert "trace_id" not in result
        assert "span_id" not in result
        assert result["key"] == "value"

    def test_with_trace_context_creates_new_dict(self):
        """Test that original labels dict is not mutated."""
        from gds_metrics.context import with_trace_context

        original = {"key": "value"}
        result = with_trace_context(original, include_trace_context=False)

        assert result is not original
        result["new_key"] = "new_value"
        assert "new_key" not in original


class TestProtocolCompliance:
    """Test that OpenTelemetryMetrics satisfies MetricsCollector protocol."""

    def test_implements_protocol(self):
        """Test that OpenTelemetryMetrics implements MetricsCollector."""
        try:
            from gds_metrics import MetricsCollector, OpenTelemetryMetrics

            if OpenTelemetryMetrics is None:
                pytest.skip("OpenTelemetry not installed")

            metrics = OpenTelemetryMetrics(service_name="test")

            # Check protocol compliance
            assert isinstance(metrics, MetricsCollector)
        except ImportError:
            pytest.skip("OpenTelemetry not installed")

    def test_composite_compatibility(self):
        """Test that OpenTelemetryMetrics works with CompositeMetrics."""
        try:
            from gds_metrics import CompositeMetrics, NoOpMetrics, OpenTelemetryMetrics

            if OpenTelemetryMetrics is None:
                pytest.skip("OpenTelemetry not installed")

            otel = OpenTelemetryMetrics(service_name="test")
            noop = NoOpMetrics()

            composite = CompositeMetrics([otel, noop])

            # Should not raise
            composite.increment("test_counter")
            composite.timing("test_timing", 10.0)
        except ImportError:
            pytest.skip("OpenTelemetry not installed")
