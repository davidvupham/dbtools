"""
OpenTelemetry metrics implementation.

This module provides integration with OpenTelemetry for metrics,
with automatic trace context enrichment for correlation.
"""

import logging
from typing import Any, Optional

from gds_metrics.context import with_trace_context

__all__ = ["OpenTelemetryMetrics"]

logger = logging.getLogger(__name__)


class OpenTelemetryMetrics:
    """
    OpenTelemetry-native metrics with automatic trace context.

    Integrates with the OpenTelemetry metrics API and automatically
    enriches metrics with trace_id/span_id for correlation.

    Requires the opentelemetry-api and opentelemetry-sdk packages.

    Example:
        from gds_metrics import OpenTelemetryMetrics

        metrics = OpenTelemetryMetrics(
            service_name="my-service",
            service_version="1.0.0"
        )

        metrics.increment("requests_total", labels={"endpoint": "/api"})
        metrics.timing("db_query_ms", 45.2, labels={"operation": "SELECT"})

    Args:
        service_name: Name of the service for resource attributes
        service_version: Version of the service (default: "1.0.0")
        include_trace_context: Auto-add trace_id/span_id to metrics (default: True)
    """

    def __init__(
        self,
        service_name: str = "gds_service",
        service_version: str = "1.0.0",
        include_trace_context: bool = True,
    ):
        """Initialize OpenTelemetry metrics."""
        try:
            from opentelemetry import metrics
            from opentelemetry.sdk.metrics import MeterProvider
            from opentelemetry.sdk.resources import Resource
        except ImportError as e:
            raise ImportError(
                "opentelemetry packages are required for OpenTelemetryMetrics. "
                "Install with: pip install gds-metrics[opentelemetry]"
            ) from e

        self._service_name = service_name
        self._service_version = service_version
        self._include_trace_context = include_trace_context
        self._metrics_module = metrics  # Store for later use

        # Check if a MeterProvider is already configured
        current_provider = metrics.get_meter_provider()
        if isinstance(current_provider, metrics.NoOpMeterProvider):
            # No provider configured, create a basic one with resource
            resource = Resource.create(
                {
                    "service.name": service_name,
                    "service.version": service_version,
                }
            )
            provider = MeterProvider(resource=resource)
            metrics.set_meter_provider(provider)
            logger.info(
                "Created MeterProvider for service: %s v%s",
                service_name,
                service_version,
            )

        # Get meter for creating instruments
        self._meter = metrics.get_meter(
            name=service_name,
            version=service_version,
        )

        # Lazy-initialized instrument registries (use Any for dynamic OTel types)
        self._counters: dict[str, Any] = {}
        self._gauges: dict[str, Any] = {}
        self._histograms: dict[str, Any] = {}

        # Store gauge values for callback-based reporting
        self._gauge_values: dict[tuple[str, tuple], float] = {}

    def _get_counter(self, name: str) -> Any:
        """Get or create a counter instrument."""
        if name not in self._counters:
            self._counters[name] = self._meter.create_counter(
                name=name,
                description=f"Counter: {name}",
            )
        return self._counters[name]

    def _get_histogram(self, name: str) -> Any:
        """Get or create a histogram instrument."""
        if name not in self._histograms:
            self._histograms[name] = self._meter.create_histogram(
                name=name,
                description=f"Histogram: {name}",
            )
        return self._histograms[name]

    def _enrich_labels(self, labels: Optional[dict[str, str]]) -> dict[str, str]:
        """Enrich labels with trace context if enabled."""
        return with_trace_context(labels, self._include_trace_context)

    def increment(self, name: str, value: int = 1, labels: Optional[dict[str, str]] = None) -> None:
        """
        Increment a counter metric.

        Counters are cumulative metrics that only increase.
        Use for: request counts, error counts, events.

        Args:
            name: Metric name (e.g., 'requests_total')
            value: Amount to increment (default: 1)
            labels: Optional key-value labels for filtering
        """
        counter = self._get_counter(name)
        enriched_labels = self._enrich_labels(labels)
        counter.add(value, enriched_labels)

    def gauge(self, name: str, value: float, labels: Optional[dict[str, str]] = None) -> None:
        """
        Set a gauge to a specific value.

        Gauges represent values that can go up or down.
        Use for: active connections, queue size, temperature.

        Note: OpenTelemetry uses observable gauges with callbacks.
        This implementation stores the value and reports it on collection.

        Args:
            name: Metric name (e.g., 'active_connections')
            value: Current value
            labels: Optional key-value labels for filtering
        """
        enriched_labels = self._enrich_labels(labels)
        label_key = tuple(sorted(enriched_labels.items())) if enriched_labels else ()

        # Store value for callback-based reporting
        gauge_key = (name, label_key)
        self._gauge_values[gauge_key] = value

        # Create gauge if not exists
        if name not in self._gauges:

            def make_callback(metric_name: str):
                def callback(options):
                    for (n, lk), val in list(self._gauge_values.items()):
                        if n == metric_name:
                            yield metrics.Observation(val, dict(lk))

                return callback

            from opentelemetry import metrics

            self._gauges[name] = self._meter.create_observable_gauge(
                name=name,
                description=f"Gauge: {name}",
                callbacks=[make_callback(name)],
            )

    def histogram(self, name: str, value: float, labels: Optional[dict[str, str]] = None) -> None:
        """
        Record a value in a histogram.

        Histograms track distributions of values.
        Use for: request latency, response sizes.

        Args:
            name: Metric name (e.g., 'request_duration_seconds')
            value: Observed value
            labels: Optional key-value labels for filtering
        """
        histogram = self._get_histogram(name)
        enriched_labels = self._enrich_labels(labels)
        histogram.record(value, enriched_labels)

    def timing(self, name: str, value_ms: float, labels: Optional[dict[str, str]] = None) -> None:
        """
        Record a timing measurement in milliseconds.

        Convenience method for duration measurements.
        Implemented as histogram under the hood.

        Args:
            name: Metric name (e.g., 'db_query_ms')
            value_ms: Duration in milliseconds
            labels: Optional key-value labels for filtering
        """
        # Record in milliseconds (can be changed to seconds if preferred)
        self.histogram(name, value_ms, labels)

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"OpenTelemetryMetrics(service_name={self._service_name!r}, "
            f"service_version={self._service_version!r})"
        )

    def __str__(self) -> str:
        """User-friendly representation."""
        return f"OpenTelemetry Metrics ({self._service_name})"
