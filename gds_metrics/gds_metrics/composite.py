"""
Composite metrics for multi-backend support.

This module provides a way to send metrics to multiple
backends simultaneously (fan-out pattern).
"""

from typing import TYPE_CHECKING, Optional

__all__ = ["CompositeMetrics"]

if TYPE_CHECKING:
    from gds_metrics.base import MetricsCollector


class CompositeMetrics:
    """
    Send metrics to multiple backends simultaneously.

    Useful when you want to send metrics to both Prometheus
    and Kafka, or add console logging for debugging.

    Example:
        from gds_metrics import CompositeMetrics, PrometheusMetrics, ConsoleMetrics

        metrics = CompositeMetrics([
            PrometheusMetrics(prefix="myapp"),
            ConsoleMetrics(),  # Also print for debugging
        ])

        metrics.increment("requests")  # Sent to both backends
    """

    def __init__(self, collectors: list["MetricsCollector"]):
        """
        Initialize composite metrics.

        Args:
            collectors: List of MetricsCollector implementations
        """
        self._collectors = collectors

    def increment(self, name: str, value: int = 1, labels: Optional[dict[str, str]] = None) -> None:
        """Increment counter on all backends."""
        for collector in self._collectors:
            collector.increment(name, value, labels)

    def gauge(self, name: str, value: float, labels: Optional[dict[str, str]] = None) -> None:
        """Set gauge on all backends."""
        for collector in self._collectors:
            collector.gauge(name, value, labels)

    def histogram(self, name: str, value: float, labels: Optional[dict[str, str]] = None) -> None:
        """Record histogram on all backends."""
        for collector in self._collectors:
            collector.histogram(name, value, labels)

    def timing(self, name: str, value_ms: float, labels: Optional[dict[str, str]] = None) -> None:
        """Record timing on all backends."""
        for collector in self._collectors:
            collector.timing(name, value_ms, labels)

    def add(self, collector: "MetricsCollector") -> None:
        """Add a new collector to the composite."""
        self._collectors.append(collector)

    def remove(self, collector: "MetricsCollector") -> None:
        """Remove a collector from the composite."""
        self._collectors.remove(collector)

    def __len__(self) -> int:
        """Return number of collectors."""
        return len(self._collectors)

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"CompositeMetrics(collectors={len(self._collectors)})"

    def __str__(self) -> str:
        """User-friendly representation."""
        return f"Composite Metrics ({len(self._collectors)} backends)"
