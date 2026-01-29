"""Tests for KafkaMetrics."""

from unittest.mock import patch

import pytest
from gds_kafka import KafkaMetrics, KafkaProducerClient


@pytest.fixture
def mock_kafka_producer():
    """Mock the underlying KafkaProducer."""
    with patch("gds_kafka.producer.KafkaProducer") as mock:
        yield mock


@pytest.fixture
def producer_client(mock_kafka_producer):
    """Create a producer client with mocked backend."""
    return KafkaProducerClient(bootstrap_servers="localhost:9092")


class TestKafkaMetrics:
    """Test suite for KafkaMetrics."""

    def test_increment(self, mock_kafka_producer, producer_client):
        """Test increment() sends counter metric."""
        metrics = KafkaMetrics(producer_client, topic="metrics")
        metrics.increment("test_counter", 1)

        args = mock_kafka_producer.return_value.send.call_args
        assert args[0][0] == "metrics"
        assert args[1]["value"]["name"] == "test_counter"
        assert args[1]["value"]["type"] == "counter"
        assert args[1]["value"]["value"] == 1.0

    def test_increment_with_labels(self, mock_kafka_producer, producer_client):
        """Test increment() with labels."""
        metrics = KafkaMetrics(producer_client, topic="metrics")
        metrics.increment("requests", 1, labels={"endpoint": "/api", "method": "GET"})

        args = mock_kafka_producer.return_value.send.call_args
        assert args[1]["value"]["labels"] == {"endpoint": "/api", "method": "GET"}

    def test_increment_default_value(self, mock_kafka_producer, producer_client):
        """Test increment() uses default value of 1."""
        metrics = KafkaMetrics(producer_client, topic="metrics")
        metrics.increment("test_counter")

        args = mock_kafka_producer.return_value.send.call_args
        assert args[1]["value"]["value"] == 1.0

    def test_gauge(self, mock_kafka_producer, producer_client):
        """Test gauge() sends gauge metric."""
        metrics = KafkaMetrics(producer_client, topic="metrics")
        metrics.gauge("active_connections", 42.5)

        args = mock_kafka_producer.return_value.send.call_args
        assert args[1]["value"]["name"] == "active_connections"
        assert args[1]["value"]["type"] == "gauge"
        assert args[1]["value"]["value"] == 42.5

    def test_gauge_with_labels(self, mock_kafka_producer, producer_client):
        """Test gauge() with labels."""
        metrics = KafkaMetrics(producer_client, topic="metrics")
        metrics.gauge("queue_size", 100.0, labels={"queue": "orders"})

        args = mock_kafka_producer.return_value.send.call_args
        assert args[1]["value"]["labels"] == {"queue": "orders"}

    def test_histogram(self, mock_kafka_producer, producer_client):
        """Test histogram() sends histogram metric."""
        metrics = KafkaMetrics(producer_client, topic="metrics")
        metrics.histogram("request_duration", 0.125)

        args = mock_kafka_producer.return_value.send.call_args
        assert args[1]["value"]["name"] == "request_duration"
        assert args[1]["value"]["type"] == "histogram"
        assert args[1]["value"]["value"] == 0.125

    def test_histogram_with_labels(self, mock_kafka_producer, producer_client):
        """Test histogram() with labels."""
        metrics = KafkaMetrics(producer_client, topic="metrics")
        metrics.histogram("response_size", 1024.0, labels={"status": "200"})

        args = mock_kafka_producer.return_value.send.call_args
        assert args[1]["value"]["labels"] == {"status": "200"}

    def test_timing(self, mock_kafka_producer, producer_client):
        """Test timing() sends timing metric."""
        metrics = KafkaMetrics(producer_client, topic="metrics")
        metrics.timing("db_query_ms", 45.6)

        args = mock_kafka_producer.return_value.send.call_args
        assert args[1]["value"]["name"] == "db_query_ms"
        assert args[1]["value"]["type"] == "timing"
        assert args[1]["value"]["value"] == 45.6

    def test_timing_with_labels(self, mock_kafka_producer, producer_client):
        """Test timing() with labels."""
        metrics = KafkaMetrics(producer_client, topic="metrics")
        metrics.timing("api_latency_ms", 150.0, labels={"service": "auth"})

        args = mock_kafka_producer.return_value.send.call_args
        assert args[1]["value"]["labels"] == {"service": "auth"}

    def test_metric_has_timestamp(self, mock_kafka_producer, producer_client):
        """Test all metrics include timestamp."""
        metrics = KafkaMetrics(producer_client, topic="metrics")
        metrics.increment("test_counter")

        args = mock_kafka_producer.return_value.send.call_args
        assert "timestamp" in args[1]["value"]
        assert isinstance(args[1]["value"]["timestamp"], float)

    def test_custom_topic(self, mock_kafka_producer, producer_client):
        """Test metrics sent to custom topic."""
        metrics = KafkaMetrics(producer_client, topic="custom-metrics")
        metrics.increment("test_counter")

        args = mock_kafka_producer.return_value.send.call_args
        assert args[0][0] == "custom-metrics"

    def test_empty_labels_default(self, mock_kafka_producer, producer_client):
        """Test metrics default to empty labels dict."""
        metrics = KafkaMetrics(producer_client, topic="metrics")
        metrics.increment("test_counter")

        args = mock_kafka_producer.return_value.send.call_args
        assert args[1]["value"]["labels"] == {}

    def test_send_failure_logs_warning(self, mock_kafka_producer, producer_client):
        """Test send failure is logged but doesn't raise."""
        mock_kafka_producer.return_value.send.side_effect = Exception("Send failed")

        metrics = KafkaMetrics(producer_client, topic="metrics")

        # Should not raise, just log warning
        metrics.increment("test_counter")

    def test_protocol_compliance(self, mock_kafka_producer, producer_client):
        """Test KafkaMetrics implements MetricsCollector protocol."""
        from gds_metrics import MetricsCollector

        metrics = KafkaMetrics(producer_client, topic="metrics")
        assert isinstance(metrics, MetricsCollector)
