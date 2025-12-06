"""
Base protocol and abstract classes for metrics collection.

This module defines the MetricsCollector protocol that all
metrics implementations must satisfy.
"""

from typing import Optional, Protocol, runtime_checkable

__all__ = ["MetricsCollector"]


@runtime_checkable
class MetricsCollector(Protocol):
    """
    Protocol for metrics collection.

    All metrics implementations must satisfy this interface,
    enabling duck typing and easy backend swapping.

    Example:
        class MyCustomMetrics:
            def increment(self, name, value=1, labels=None):
                # Custom implementation
                pass
            # ... other methods

        # Works with any code expecting MetricsCollector
        metrics: MetricsCollector = MyCustomMetrics()
    """

    def increment(
        self, name: str, value: int = 1, labels: Optional[dict[str, str]] = None
    ) -> None:
        """
        Increment a counter metric.

        Counters are cumulative metrics that only increase.
        Use for: request counts, error counts, events.

        Args:
            name: Metric name (e.g., 'requests_total')
            value: Amount to increment (default: 1)
            labels: Optional key-value labels for filtering
        """
        ...

    def gauge(
        self, name: str, value: float, labels: Optional[dict[str, str]] = None
    ) -> None:
        """
        Set a gauge to a specific value.

        Gauges represent values that can go up or down.
        Use for: active connections, queue size, temperature.

        Args:
            name: Metric name (e.g., 'active_connections')
            value: Current value
            labels: Optional key-value labels for filtering
        """
        ...

    def histogram(
        self, name: str, value: float, labels: Optional[dict[str, str]] = None
    ) -> None:
        """
        Record a value in a histogram.

        Histograms track distributions of values.
        Use for: request latency, response sizes.

        Args:
            name: Metric name (e.g., 'request_duration_seconds')
            value: Observed value
            labels: Optional key-value labels for filtering
        """
        ...

    def timing(
        self, name: str, value_ms: float, labels: Optional[dict[str, str]] = None
    ) -> None:
        """
        Record a timing measurement in milliseconds.

        Convenience method for duration measurements.
        Typically implemented as histogram under the hood.

        Args:
            name: Metric name (e.g., 'db_query_ms')
            value_ms: Duration in milliseconds
            labels: Optional key-value labels for filtering
        """
        ...
