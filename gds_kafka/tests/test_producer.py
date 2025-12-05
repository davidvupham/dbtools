"""Tests for KafkaProducerClient."""

from unittest.mock import patch

import pytest

from gds_kafka import KafkaConnectionError, KafkaProducerClient


@pytest.fixture
def mock_kafka_producer():
    """Mock the underlying KafkaProducer."""
    with patch("gds_kafka.producer.KafkaProducer") as mock:
        yield mock


class TestKafkaProducerClient:
    """Test suite for KafkaProducerClient."""

    def test_initialization(self, mock_kafka_producer):
        """Test producer initializes with correct configuration."""
        _client = KafkaProducerClient(bootstrap_servers="localhost:9092")

        mock_kafka_producer.assert_called_once()
        call_kwargs = mock_kafka_producer.call_args[1]
        assert call_kwargs["bootstrap_servers"] == "localhost:9092"
        assert "value_serializer" in call_kwargs

    def test_send_with_key(self, mock_kafka_producer):
        """Test send() with message key."""
        client = KafkaProducerClient(bootstrap_servers="localhost:9092")
        client.send("test-topic", {"data": "value"}, key="my-key")

        call_args = mock_kafka_producer.return_value.send.call_args
        assert call_args[0][0] == "test-topic"
        assert call_args[1]["key"] == b"my-key"

    def test_send_without_key(self, mock_kafka_producer):
        """Test send() without message key."""
        client = KafkaProducerClient(bootstrap_servers="localhost:9092")
        client.send("test-topic", {"data": "value"})

        call_args = mock_kafka_producer.return_value.send.call_args
        assert call_args[1]["key"] is None

    def test_flush(self, mock_kafka_producer):
        """Test flush() calls underlying producer flush."""
        client = KafkaProducerClient(bootstrap_servers="localhost:9092")
        client.flush()

        mock_kafka_producer.return_value.flush.assert_called_once()

    def test_flush_with_timeout(self, mock_kafka_producer):
        """Test flush() with timeout parameter."""
        client = KafkaProducerClient(bootstrap_servers="localhost:9092")
        client.flush(timeout=5.0)

        mock_kafka_producer.return_value.flush.assert_called_once_with(timeout=5.0)

    def test_close(self, mock_kafka_producer):
        """Test close() calls underlying producer close."""
        client = KafkaProducerClient(bootstrap_servers="localhost:9092")
        client.close()

        mock_kafka_producer.return_value.close.assert_called_once()

    def test_context_manager(self, mock_kafka_producer):
        """Test producer works as context manager."""
        with KafkaProducerClient(bootstrap_servers="localhost:9092") as client:
            assert client is not None
            client.send("test-topic", {"data": "value"})

        mock_kafka_producer.return_value.close.assert_called_once()

    def test_connection_failure(self, mock_kafka_producer):
        """Test connection failure raises KafkaConnectionError."""
        from kafka.errors import NoBrokersAvailable

        mock_kafka_producer.side_effect = NoBrokersAvailable()

        with pytest.raises(KafkaConnectionError) as exc_info:
            KafkaProducerClient(bootstrap_servers="localhost:9092")

        assert "Failed to connect" in str(exc_info.value)

    def test_custom_config_passthrough(self, mock_kafka_producer):
        """Test custom configuration is passed to underlying producer."""
        _client = KafkaProducerClient(
            bootstrap_servers="localhost:9092",
            acks="all",
            retries=3,
        )

        call_kwargs = mock_kafka_producer.call_args[1]
        assert call_kwargs["acks"] == "all"
        assert call_kwargs["retries"] == 3
