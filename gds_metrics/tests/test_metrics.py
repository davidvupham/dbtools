"""
Tests for metrics implementations.
"""

import unittest
from io import StringIO
from unittest.mock import patch

from gds_metrics import CompositeMetrics, ConsoleMetrics, NoOpMetrics
from gds_metrics.base import MetricsCollector


class TestMetricsCollectorProtocol(unittest.TestCase):
    """Test that implementations satisfy MetricsCollector protocol."""

    def test_noop_is_metrics_collector(self):
        """NoOpMetrics should satisfy MetricsCollector protocol."""
        metrics = NoOpMetrics()
        self.assertIsInstance(metrics, MetricsCollector)

    def test_console_is_metrics_collector(self):
        """ConsoleMetrics should satisfy MetricsCollector protocol."""
        metrics = ConsoleMetrics()
        self.assertIsInstance(metrics, MetricsCollector)

    def test_composite_is_metrics_collector(self):
        """CompositeMetrics should satisfy MetricsCollector protocol."""
        metrics = CompositeMetrics([NoOpMetrics()])
        self.assertIsInstance(metrics, MetricsCollector)


class TestNoOpMetrics(unittest.TestCase):
    """Test NoOpMetrics implementation."""

    def setUp(self):
        """Set up test fixtures."""
        self.metrics = NoOpMetrics()

    def test_increment_does_nothing(self):
        """increment() should not raise."""
        self.metrics.increment("test_counter")
        self.metrics.increment("test_counter", value=5)
        self.metrics.increment("test_counter", labels={"key": "value"})

    def test_gauge_does_nothing(self):
        """gauge() should not raise."""
        self.metrics.gauge("test_gauge", 42.0)
        self.metrics.gauge("test_gauge", 42.0, labels={"key": "value"})

    def test_histogram_does_nothing(self):
        """histogram() should not raise."""
        self.metrics.histogram("test_histogram", 0.125)
        self.metrics.histogram("test_histogram", 0.125, labels={"key": "value"})

    def test_timing_does_nothing(self):
        """timing() should not raise."""
        self.metrics.timing("test_timing", 150.5)
        self.metrics.timing("test_timing", 150.5, labels={"key": "value"})

    def test_repr(self):
        """__repr__ should return expected format."""
        self.assertEqual(repr(self.metrics), "NoOpMetrics()")

    def test_str(self):
        """__str__ should return user-friendly format."""
        self.assertIn("No-Op", str(self.metrics))


class TestConsoleMetrics(unittest.TestCase):
    """Test ConsoleMetrics implementation."""

    def test_increment_prints_counter(self):
        """increment() should print to stdout."""
        metrics = ConsoleMetrics()
        with patch("sys.stdout", new_callable=StringIO):
            with patch("builtins.print") as mock_print:
                metrics.increment("requests_total")
                mock_print.assert_called()
                call_args = str(mock_print.call_args)
                self.assertIn("COUNTER", call_args)
                self.assertIn("requests_total", call_args)

    def test_prefix_applied(self):
        """Prefix should be applied to metric names."""
        metrics = ConsoleMetrics(prefix="myapp")
        with patch("builtins.print") as mock_print:
            metrics.gauge("connections", 42)
            call_args = str(mock_print.call_args)
            self.assertIn("myapp.connections", call_args)

    def test_labels_printed(self):
        """Labels should be included in output."""
        metrics = ConsoleMetrics()
        with patch("builtins.print") as mock_print:
            metrics.increment("requests", labels={"status": "200"})
            call_args = str(mock_print.call_args)
            self.assertIn("status", call_args)
            self.assertIn("200", call_args)

    def test_timing_formats_milliseconds(self):
        """timing() should format value with ms suffix."""
        metrics = ConsoleMetrics()
        with patch("builtins.print") as mock_print:
            metrics.timing("duration", 123.456)
            call_args = str(mock_print.call_args)
            self.assertIn("TIMING", call_args)
            self.assertIn("123.46", call_args)  # 2 decimal places

    def test_repr_with_prefix(self):
        """__repr__ should include prefix."""
        metrics = ConsoleMetrics(prefix="test")
        self.assertEqual(repr(metrics), "ConsoleMetrics(prefix='test')")

    def test_gauge_output_format(self):
        """gauge() should print GAUGE format."""
        metrics = ConsoleMetrics()
        with patch("builtins.print") as mock_print:
            metrics.gauge("connections", 42.5)
            call_args = str(mock_print.call_args)
            self.assertIn("GAUGE", call_args)
            self.assertIn("connections", call_args)
            self.assertIn("42.5", call_args)

    def test_histogram_output_format(self):
        """histogram() should print HISTOGRAM format."""
        metrics = ConsoleMetrics()
        with patch("builtins.print") as mock_print:
            metrics.histogram("duration", 0.125)
            call_args = str(mock_print.call_args)
            self.assertIn("HISTOGRAM", call_args)
            self.assertIn("duration", call_args)
            self.assertIn("0.125", call_args)

    def test_str(self):
        """__str__ should return user-friendly format."""
        metrics = ConsoleMetrics()
        self.assertIn("Console", str(metrics))

    def test_str_with_prefix(self):
        """__str__ should include prefix when set."""
        metrics = ConsoleMetrics(prefix="myapp")
        str_repr = str(metrics)
        self.assertIn("Console", str_repr)
        self.assertIn("myapp", str_repr)

    def test_empty_prefix(self):
        """Should work correctly with empty prefix."""
        metrics = ConsoleMetrics(prefix="")
        with patch("builtins.print") as mock_print:
            metrics.increment("test_metric")
            call_args = str(mock_print.call_args)
            # Should not have double dots or prefix
            self.assertIn("test_metric", call_args)
            self.assertNotIn("..", call_args)

    def test_repr_without_prefix(self):
        """__repr__ should handle empty prefix."""
        metrics = ConsoleMetrics()
        repr_str = repr(metrics)
        self.assertIn("ConsoleMetrics", repr_str)
        self.assertIn("prefix=''", repr_str)


class TestCompositeMetrics(unittest.TestCase):
    """Test CompositeMetrics implementation."""

    def test_increment_calls_all_collectors(self):
        """increment() should call all child collectors."""
        collector1 = NoOpMetrics()
        collector2 = NoOpMetrics()
        composite = CompositeMetrics([collector1, collector2])

        # Should not raise
        composite.increment("test", value=5, labels={"key": "value"})

    def test_len_returns_collector_count(self):
        """__len__ should return number of collectors."""
        composite = CompositeMetrics([NoOpMetrics(), NoOpMetrics()])
        self.assertEqual(len(composite), 2)

    def test_add_collector(self):
        """add() should increase collector count."""
        composite = CompositeMetrics([])
        self.assertEqual(len(composite), 0)

        composite.add(NoOpMetrics())
        self.assertEqual(len(composite), 1)

    def test_remove_collector(self):
        """remove() should decrease collector count."""
        collector = NoOpMetrics()
        composite = CompositeMetrics([collector])
        self.assertEqual(len(composite), 1)

        composite.remove(collector)
        self.assertEqual(len(composite), 0)

    def test_repr(self):
        """__repr__ should show collector count."""
        composite = CompositeMetrics([NoOpMetrics(), NoOpMetrics()])
        self.assertIn("2", repr(composite))

    def test_gauge_calls_all_collectors(self):
        """gauge() should delegate to all child collectors."""
        from unittest.mock import MagicMock

        mock1, mock2 = MagicMock(), MagicMock()
        composite = CompositeMetrics([mock1, mock2])
        composite.gauge("connections", 42.0, {"env": "prod"})
        mock1.gauge.assert_called_once_with("connections", 42.0, {"env": "prod"})
        mock2.gauge.assert_called_once_with("connections", 42.0, {"env": "prod"})

    def test_histogram_calls_all_collectors(self):
        """histogram() should delegate to all child collectors."""
        from unittest.mock import MagicMock

        mock1, mock2 = MagicMock(), MagicMock()
        composite = CompositeMetrics([mock1, mock2])
        composite.histogram("duration", 0.5, {"path": "/api"})
        mock1.histogram.assert_called_once_with("duration", 0.5, {"path": "/api"})
        mock2.histogram.assert_called_once_with("duration", 0.5, {"path": "/api"})

    def test_timing_calls_all_collectors(self):
        """timing() should delegate to all child collectors."""
        from unittest.mock import MagicMock

        mock1, mock2 = MagicMock(), MagicMock()
        composite = CompositeMetrics([mock1, mock2])
        composite.timing("query_ms", 150.0, {"db": "postgres"})
        mock1.timing.assert_called_once_with("query_ms", 150.0, {"db": "postgres"})
        mock2.timing.assert_called_once_with("query_ms", 150.0, {"db": "postgres"})

    def test_str(self):
        """__str__ should return user-friendly format."""
        composite = CompositeMetrics([NoOpMetrics(), NoOpMetrics()])
        str_repr = str(composite)
        self.assertIn("Composite", str_repr)
        self.assertIn("2", str_repr)

    def test_empty_collector_list(self):
        """Should work with no collectors."""
        composite = CompositeMetrics([])
        # Should not raise
        composite.increment("test")
        composite.gauge("test", 1.0)
        composite.histogram("test", 0.5)
        composite.timing("test", 100.0)

    def test_remove_nonexistent_raises_valueerror(self):
        """remove() should raise ValueError for non-existent collector."""
        composite = CompositeMetrics([])
        collector = NoOpMetrics()
        with self.assertRaises(ValueError):
            composite.remove(collector)

    def test_increment_with_mocks_verifies_delegation(self):
        """increment() should be verified via mocks."""
        from unittest.mock import MagicMock

        mock1, mock2 = MagicMock(), MagicMock()
        composite = CompositeMetrics([mock1, mock2])
        composite.increment("requests", 5, {"status": "200"})
        mock1.increment.assert_called_once_with("requests", 5, {"status": "200"})
        mock2.increment.assert_called_once_with("requests", 5, {"status": "200"})


if __name__ == "__main__":
    unittest.main()
