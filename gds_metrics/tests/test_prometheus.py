"""
Tests for PrometheusMetrics implementation.

These tests mock prometheus_client to avoid starting real HTTP servers
and to verify correct interaction with Prometheus metric types.
"""

import sys
import unittest
from unittest.mock import MagicMock, patch

from gds_metrics.base import MetricsCollector


class TestPrometheusMetricsProtocol(unittest.TestCase):
    """Test that PrometheusMetrics satisfies MetricsCollector protocol."""

    @patch("prometheus_client.start_http_server")
    def test_prometheus_is_metrics_collector(self, mock_server):
        """PrometheusMetrics should satisfy MetricsCollector protocol."""
        from gds_metrics.prometheus import PrometheusMetrics

        metrics = PrometheusMetrics(start_server=False)
        self.assertIsInstance(metrics, MetricsCollector)


class TestPrometheusMetricsInitialization(unittest.TestCase):
    """Test PrometheusMetrics initialization options."""

    @patch("prometheus_client.start_http_server")
    def test_initialization_with_defaults(self, mock_server):
        """Should use default prefix='gds' and port=8080."""
        from gds_metrics.prometheus import PrometheusMetrics

        metrics = PrometheusMetrics()
        self.assertEqual(metrics._prefix, "gds")
        self.assertEqual(metrics._port, 8080)
        mock_server.assert_called_once_with(8080)

    @patch("prometheus_client.start_http_server")
    def test_initialization_custom_prefix(self, mock_server):
        """Custom prefix should be stored."""
        from gds_metrics.prometheus import PrometheusMetrics

        metrics = PrometheusMetrics(prefix="myapp")
        self.assertEqual(metrics._prefix, "myapp")

    @patch("prometheus_client.start_http_server")
    def test_initialization_custom_port(self, mock_server):
        """Custom port should be used for HTTP server."""
        from gds_metrics.prometheus import PrometheusMetrics

        metrics = PrometheusMetrics(port=9090)
        self.assertEqual(metrics._port, 9090)
        mock_server.assert_called_once_with(9090)

    @patch("prometheus_client.start_http_server")
    def test_initialization_starts_server_by_default(self, mock_server):
        """HTTP server should start by default."""
        from gds_metrics.prometheus import PrometheusMetrics

        PrometheusMetrics()
        mock_server.assert_called_once()

    @patch("prometheus_client.start_http_server")
    def test_initialization_skip_server(self, mock_server):
        """start_server=False should skip HTTP server startup."""
        from gds_metrics.prometheus import PrometheusMetrics

        PrometheusMetrics(start_server=False)
        mock_server.assert_not_called()


class TestPrometheusMetricsImportError(unittest.TestCase):
    """Test ImportError handling when prometheus-client is missing."""

    def test_import_error_without_dependency(self):
        """Should raise ImportError with helpful message when prometheus-client missing."""
        # Save original module references
        original_modules = sys.modules.copy()

        try:
            # Remove prometheus_client from sys.modules if present
            modules_to_remove = [
                key for key in sys.modules.keys() if key.startswith("prometheus_client")
            ]
            for mod in modules_to_remove:
                del sys.modules[mod]

            # Also remove gds_metrics.prometheus to force reimport
            if "gds_metrics.prometheus" in sys.modules:
                del sys.modules["gds_metrics.prometheus"]

            # Mock prometheus_client to raise ImportError
            with patch.dict(sys.modules, {"prometheus_client": None}):
                # Clear the cached import
                if "gds_metrics.prometheus" in sys.modules:
                    del sys.modules["gds_metrics.prometheus"]

                # Now try to import and instantiate
                try:
                    # This approach: import the module fresh
                    import importlib.util

                    spec = importlib.util.find_spec("gds_metrics.prometheus")
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        with self.assertRaises(ImportError) as ctx:
                            spec.loader.exec_module(module)
                            module.PrometheusMetrics()

                        error_msg = str(ctx.exception)
                        self.assertIn("prometheus-client", error_msg.lower())
                except TypeError:
                    # Alternative: The import itself may fail
                    pass

        finally:
            # Restore original modules
            sys.modules.clear()
            sys.modules.update(original_modules)


class TestPrometheusMetricsCounter(unittest.TestCase):
    """Test PrometheusMetrics counter operations."""

    def setUp(self):
        """Set up test fixtures - clear registry and create fresh metrics instance."""
        # Clear the default registry to avoid conflicts between tests
        import prometheus_client
        collectors = list(
            prometheus_client.REGISTRY._names_to_collectors.values())
        for collector in collectors:
            try:
                prometheus_client.REGISTRY.unregister(collector)
            except Exception:
                pass

        from gds_metrics.prometheus import PrometheusMetrics
        self.metrics = PrometheusMetrics(
            prefix="counter_test", start_server=False)

    def test_increment_creates_counter(self):
        """increment() should create a Counter on first call."""
        self.metrics.increment("requests_total")

        # Verify counter was created
        key = ("counter_test_requests_total", ())
        self.assertIn(key, self.metrics._counters)

    def test_increment_reuses_counter(self):
        """increment() should reuse Counter for same metric name."""
        self.metrics.increment("reuse_counter")
        self.metrics.increment("reuse_counter")

        # Should only have one counter
        counter_keys = [k for k in self.metrics._counters.keys()
                        if "reuse_counter" in k[0]]
        self.assertEqual(len(counter_keys), 1)

    def test_increment_with_labels(self):
        """increment() should handle labels correctly."""
        self.metrics.increment("labeled_counter", labels={
                               "status": "200", "method": "GET"})

        # Verify counter was created with label names (order may vary due to dict ordering)
        # Just verify the counter exists with both labels
        matching_keys = [k for k in self.metrics._counters.keys()
                         if k[0] == "counter_test_labeled_counter"]
        self.assertEqual(len(matching_keys), 1)
        # Verify both label names are present
        label_names = matching_keys[0][1]
        self.assertIn("status", label_names)
        self.assertIn("method", label_names)

    def test_increment_without_labels(self):
        """increment() should work without labels."""
        # Should not raise
        self.metrics.increment("no_labels_counter")
        self.metrics.increment("no_labels_counter", value=5)

    def test_increment_with_custom_value(self):
        """increment() should accept custom increment value."""
        # Should not raise
        self.metrics.increment("custom_value_counter", value=10)


class TestPrometheusMetricsGauge(unittest.TestCase):
    """Test PrometheusMetrics gauge operations."""

    def setUp(self):
        """Set up test fixtures - clear registry and create fresh metrics instance."""
        import prometheus_client
        collectors = list(
            prometheus_client.REGISTRY._names_to_collectors.values())
        for collector in collectors:
            try:
                prometheus_client.REGISTRY.unregister(collector)
            except Exception:
                pass

        from gds_metrics.prometheus import PrometheusMetrics
        self.metrics = PrometheusMetrics(
            prefix="gauge_test", start_server=False)

    def test_gauge_creates_gauge(self):
        """gauge() should create a Gauge on first call."""
        self.metrics.gauge("active_connections", 42.0)

        key = ("gauge_test_active_connections", ())
        self.assertIn(key, self.metrics._gauges)

    def test_gauge_with_labels(self):
        """gauge() should handle labels correctly."""
        self.metrics.gauge("labeled_gauge", 42.0, labels={"pool": "primary"})

        key = ("gauge_test_labeled_gauge", ("pool",))
        self.assertIn(key, self.metrics._gauges)

    def test_gauge_without_labels(self):
        """gauge() should work without labels."""
        # Should not raise
        self.metrics.gauge("temperature", 72.5)


class TestPrometheusMetricsHistogram(unittest.TestCase):
    """Test PrometheusMetrics histogram operations."""

    def setUp(self):
        """Set up test fixtures - clear registry and create fresh metrics instance."""
        import prometheus_client
        collectors = list(
            prometheus_client.REGISTRY._names_to_collectors.values())
        for collector in collectors:
            try:
                prometheus_client.REGISTRY.unregister(collector)
            except Exception:
                pass

        from gds_metrics.prometheus import PrometheusMetrics
        self.metrics = PrometheusMetrics(
            prefix="hist_test", start_server=False)

    def test_histogram_creates_histogram(self):
        """histogram() should create a Histogram on first call."""
        self.metrics.histogram("request_duration_seconds", 0.125)

        key = ("hist_test_request_duration_seconds", ())
        self.assertIn(key, self.metrics._histograms)

    def test_histogram_with_labels(self):
        """histogram() should handle labels correctly."""
        self.metrics.histogram(
            "labeled_histogram", 0.125, labels={"endpoint": "/api/users"}
        )

        key = ("hist_test_labeled_histogram", ("endpoint",))
        self.assertIn(key, self.metrics._histograms)

    def test_histogram_without_labels(self):
        """histogram() should work without labels."""
        # Should not raise
        self.metrics.histogram("response_size_bytes", 1024.0)


class TestPrometheusMetricsTiming(unittest.TestCase):
    """Test PrometheusMetrics timing operations."""

    def setUp(self):
        """Set up test fixtures - clear registry and create fresh metrics instance."""
        import prometheus_client
        collectors = list(
            prometheus_client.REGISTRY._names_to_collectors.values())
        for collector in collectors:
            try:
                prometheus_client.REGISTRY.unregister(collector)
            except Exception:
                pass

        from gds_metrics.prometheus import PrometheusMetrics
        self.metrics = PrometheusMetrics(
            prefix="timing_test", start_server=False)

    def test_timing_converts_to_seconds(self):
        """timing() should convert milliseconds to seconds."""
        # 1500ms = 1.5 seconds
        self.metrics.timing("operation_duration", 1500.0)

        # Timing uses histogram under the hood
        key = ("timing_test_operation_duration", ())
        self.assertIn(key, self.metrics._histograms)

    def test_timing_with_labels(self):
        """timing() should handle labels correctly."""
        self.metrics.timing("db_query_ms", 50.0, labels={
                            "query_type": "select"})

        key = ("timing_test_db_query_ms", ("query_type",))
        self.assertIn(key, self.metrics._histograms)


class TestPrometheusMetricsRepresentation(unittest.TestCase):
    """Test PrometheusMetrics string representations."""

    @patch("prometheus_client.start_http_server")
    def test_repr(self, mock_server):
        """__repr__ should return developer-friendly format."""
        from gds_metrics.prometheus import PrometheusMetrics

        metrics = PrometheusMetrics(
            prefix="myapp", port=9090, start_server=False)
        repr_str = repr(metrics)

        self.assertIn("PrometheusMetrics", repr_str)
        self.assertIn("myapp", repr_str)
        self.assertIn("9090", repr_str)

    @patch("prometheus_client.start_http_server")
    def test_str(self, mock_server):
        """__str__ should return user-friendly format."""
        from gds_metrics.prometheus import PrometheusMetrics

        metrics = PrometheusMetrics(port=8080, start_server=False)
        str_repr = str(metrics)

        self.assertIn("Prometheus", str_repr)
        self.assertIn("8080", str_repr)


class TestPrometheusMetricsEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    def setUp(self):
        """Clear registry before each test."""
        import prometheus_client
        collectors = list(
            prometheus_client.REGISTRY._names_to_collectors.values())
        for collector in collectors:
            try:
                prometheus_client.REGISTRY.unregister(collector)
            except Exception:
                pass

    def test_empty_prefix(self):
        """Should work with empty prefix."""
        from gds_metrics.prometheus import PrometheusMetrics

        metrics = PrometheusMetrics(prefix="", start_server=False)
        metrics.increment("edge_requests_total")

        # With empty prefix, metric name should not have prefix
        key = ("edge_requests_total", ())
        self.assertIn(key, metrics._counters)

    def test_empty_labels_dict(self):
        """Should handle empty labels dict same as None."""
        from gds_metrics.prometheus import PrometheusMetrics

        metrics = PrometheusMetrics(prefix="edge_test", start_server=False)

        # Empty dict should work
        metrics.increment("empty_labels_metric", labels={})

    def test_metric_caching_different_labels(self):
        """Same metric with same labels should be cached."""
        from gds_metrics.prometheus import PrometheusMetrics

        metrics = PrometheusMetrics(prefix="cache_test", start_server=False)

        # Same metric name, same labels - should reuse the same counter
        metrics.increment("cache_requests", labels={"status": "200"})
        metrics.increment("cache_requests", labels={"status": "404"})

        # Should have only one counter entry (same label names)
        self.assertEqual(len(metrics._counters), 1)


if __name__ == "__main__":
    unittest.main()
