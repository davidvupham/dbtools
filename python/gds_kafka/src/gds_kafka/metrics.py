"""Kafka-based metrics collector implementing gds_metrics.MetricsCollector protocol."""

import logging
import time
from typing import Optional

from gds_metrics import MetricsCollector

from .producer import KafkaProducerClient

logger = logging.getLogger(__name__)


class KafkaMetrics(MetricsCollector):
    """Metrics collector that streams metrics to Kafka.

    Implements the MetricsCollector protocol from gds_metrics,
    allowing seamless integration with any code expecting a MetricsCollector.

    Args:
        producer: KafkaProducerClient instance for sending metrics.
        topic: Kafka topic for metrics (default: "metrics").

    Example:
        >>> producer = KafkaProducerClient("localhost:9092")
        >>> metrics = KafkaMetrics(producer, topic="app-metrics")
        >>> metrics.increment("requests_total", labels={"endpoint": "/api"})
    """

    def __init__(self, producer: KafkaProducerClient, topic: str = "metrics"):
        self.producer = producer
        self.topic = topic

    def _send(
        self,
        metric_type: str,
        name: str,
        value: float,
        labels: Optional[dict[str, str]] = None,
    ) -> None:
        """Internal method to send metric to Kafka.

        Args:
            metric_type: Type of metric (counter, gauge, histogram, timing).
            name: Metric name.
            value: Metric value.
            labels: Optional key-value labels for filtering.
        """
        payload = {
            "timestamp": time.time(),
            "type": metric_type,
            "name": name,
            "value": value,
            "labels": labels or {},
        }
        try:
            self.producer.send(self.topic, payload)
        except Exception as e:
            # Log warning but don't fail the calling application
            logger.warning(f"Failed to send metric '{name}': {e}")

    def increment(self, name: str, value: int = 1, labels: Optional[dict[str, str]] = None) -> None:
        """Increment a counter metric.

        Args:
            name: Metric name (e.g., 'requests_total').
            value: Amount to increment (default: 1).
            labels: Optional key-value labels for filtering.
        """
        self._send("counter", name, float(value), labels)

    def gauge(self, name: str, value: float, labels: Optional[dict[str, str]] = None) -> None:
        """Set a gauge to a specific value.

        Args:
            name: Metric name (e.g., 'active_connections').
            value: Current value.
            labels: Optional key-value labels for filtering.
        """
        self._send("gauge", name, value, labels)

    def histogram(self, name: str, value: float, labels: Optional[dict[str, str]] = None) -> None:
        """Record a value in a histogram.

        Args:
            name: Metric name (e.g., 'request_duration_seconds').
            value: Observed value.
            labels: Optional key-value labels for filtering.
        """
        self._send("histogram", name, value, labels)

    def timing(self, name: str, value_ms: float, labels: Optional[dict[str, str]] = None) -> None:
        """Record a timing measurement in milliseconds.

        Args:
            name: Metric name (e.g., 'db_query_ms').
            value_ms: Duration in milliseconds.
            labels: Optional key-value labels for filtering.
        """
        self._send("timing", name, value_ms, labels)
