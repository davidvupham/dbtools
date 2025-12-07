"""
Prometheus metrics implementation.

This module provides integration with Prometheus via the
prometheus-client library, exposing metrics at an HTTP endpoint.
"""

import logging
from typing import TYPE_CHECKING, Optional

__all__ = ["PrometheusMetrics"]

logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    # For type hints only; actual classes are set at runtime after import
    from prometheus_client import Counter as _CounterType
    from prometheus_client import Gauge as _GaugeType
    from prometheus_client import Histogram as _HistogramType


class PrometheusMetrics:
    """
    Prometheus metrics with HTTP endpoint.

    Exposes metrics at an HTTP endpoint for Prometheus to scrape.
    Requires the prometheus-client package.

    Example:
        from gds_metrics import PrometheusMetrics

        # Start metrics server on port 8080
        metrics = PrometheusMetrics(prefix="myapp", port=8080)

        metrics.increment("requests_total", labels={"endpoint": "/api"})
        # Prometheus scrapes http://localhost:8080/metrics

    Args:
        prefix: Prefix for all metric names (e.g., "myapp")
        port: HTTP port to expose /metrics endpoint (default: 8080)
        start_server: Whether to start HTTP server (default: True)
    """

    def __init__(self, prefix: str = "gds", port: int = 8080, start_server: bool = True):
        """Initialize Prometheus metrics."""
        try:
            from prometheus_client import Counter, Gauge, Histogram, start_http_server
        except ImportError as e:
            raise ImportError(
                "prometheus-client is required for PrometheusMetrics. "
                "Install with: pip install prometheus-client"
            ) from e

        self._prefix = prefix
        self._port = port

        # Lazy-initialized metric registries
        self._counters: dict[str, _CounterType] = {}
        self._gauges: dict[str, _GaugeType] = {}
        self._histograms: dict[str, _HistogramType] = {}

        # Import classes for later use
        self._Counter = Counter
        self._Gauge = Gauge
        self._Histogram = Histogram

        # Start HTTP server if requested
        if start_server:
            start_http_server(port)
            logger.info("Prometheus metrics server started on port %d", port)

    def _get_counter(self, name: str, labels: Optional[dict[str, str]]) -> "_CounterType":
        """Get or create a counter metric."""
        full_name = f"{self._prefix}_{name}" if self._prefix else name
        label_names = tuple(labels.keys()) if labels else ()

        key = (full_name, label_names)
        if key not in self._counters:
            self._counters[key] = self._Counter(full_name, f"Counter: {name}", list(label_names))
        return self._counters[key]

    def _get_gauge(self, name: str, labels: Optional[dict[str, str]]) -> "_GaugeType":
        """Get or create a gauge metric."""
        full_name = f"{self._prefix}_{name}" if self._prefix else name
        label_names = tuple(labels.keys()) if labels else ()

        key = (full_name, label_names)
        if key not in self._gauges:
            self._gauges[key] = self._Gauge(full_name, f"Gauge: {name}", list(label_names))
        return self._gauges[key]

    def _get_histogram(self, name: str, labels: Optional[dict[str, str]]) -> "_HistogramType":
        """Get or create a histogram metric."""
        full_name = f"{self._prefix}_{name}" if self._prefix else name
        label_names = tuple(labels.keys()) if labels else ()

        key = (full_name, label_names)
        if key not in self._histograms:
            self._histograms[key] = self._Histogram(
                full_name, f"Histogram: {name}", list(label_names)
            )
        return self._histograms[key]

    def increment(self, name: str, value: int = 1, labels: Optional[dict[str, str]] = None) -> None:
        """Increment a Prometheus counter."""
        counter = self._get_counter(name, labels)
        if labels:
            counter.labels(**labels).inc(value)
        else:
            counter.inc(value)

    def gauge(self, name: str, value: float, labels: Optional[dict[str, str]] = None) -> None:
        """Set a Prometheus gauge value."""
        gauge = self._get_gauge(name, labels)
        if labels:
            gauge.labels(**labels).set(value)
        else:
            gauge.set(value)

    def histogram(self, name: str, value: float, labels: Optional[dict[str, str]] = None) -> None:
        """Observe a value in a Prometheus histogram."""
        histogram = self._get_histogram(name, labels)
        if labels:
            histogram.labels(**labels).observe(value)
        else:
            histogram.observe(value)

    def timing(self, name: str, value_ms: float, labels: Optional[dict[str, str]] = None) -> None:
        """Record timing as histogram (converts ms to seconds)."""
        # Prometheus convention: use seconds for durations
        value_seconds = value_ms / 1000.0
        self.histogram(name, value_seconds, labels)

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"PrometheusMetrics(prefix={self._prefix!r}, port={self._port})"

    def __str__(self) -> str:
        """User-friendly representation."""
        return f"Prometheus Metrics (port {self._port})"
