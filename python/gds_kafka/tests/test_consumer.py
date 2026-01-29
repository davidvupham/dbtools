"""Tests for KafkaConsumerClient."""

from unittest.mock import MagicMock, patch

import pytest
from gds_kafka import KafkaConnectionError, KafkaConsumerClient


@pytest.fixture
def mock_kafka_consumer():
    """Mock the underlying KafkaConsumer."""
    with patch("gds_kafka.consumer.KafkaConsumer") as mock:
        yield mock


class TestKafkaConsumerClient:
    """Test suite for KafkaConsumerClient."""

    def test_initialization(self, mock_kafka_consumer):
        """Test consumer initializes with correct configuration."""
        _client = KafkaConsumerClient(
            topic="test-topic",
            bootstrap_servers="localhost:9092",
            group_id="test-group",
        )

        mock_kafka_consumer.assert_called_once()
        call_args = mock_kafka_consumer.call_args
        assert call_args[0][0] == "test-topic"
        assert call_args[1]["bootstrap_servers"] == "localhost:9092"
        assert call_args[1]["group_id"] == "test-group"

    def test_messages_generator(self, mock_kafka_consumer):
        """Test messages() yields properly formatted messages."""
        # Setup mock messages
        mock_message = MagicMock()
        mock_message.key = b"test-key"
        mock_message.value = {"data": "test"}
        mock_message.topic = "test-topic"
        mock_message.partition = 0
        mock_message.offset = 42

        mock_kafka_consumer.return_value.__iter__ = lambda self: iter([mock_message])

        client = KafkaConsumerClient("test-topic", "localhost:9092")
        messages = list(client.messages())

        assert len(messages) == 1
        assert messages[0]["key"] == "test-key"
        assert messages[0]["value"] == {"data": "test"}
        assert messages[0]["topic"] == "test-topic"
        assert messages[0]["partition"] == 0
        assert messages[0]["offset"] == 42

    def test_messages_without_key(self, mock_kafka_consumer):
        """Test messages() handles messages without keys."""
        mock_message = MagicMock()
        mock_message.key = None
        mock_message.value = {"data": "test"}
        mock_message.topic = "test-topic"
        mock_message.partition = 0
        mock_message.offset = 0

        mock_kafka_consumer.return_value.__iter__ = lambda self: iter([mock_message])

        client = KafkaConsumerClient("test-topic", "localhost:9092")
        messages = list(client.messages())

        assert messages[0]["key"] is None

    def test_close(self, mock_kafka_consumer):
        """Test close() calls underlying consumer close."""
        client = KafkaConsumerClient("test-topic", "localhost:9092")
        client.close()

        mock_kafka_consumer.return_value.close.assert_called_once()

    def test_context_manager(self, mock_kafka_consumer):
        """Test consumer works as context manager."""
        with KafkaConsumerClient("test-topic", "localhost:9092") as client:
            assert client is not None

        mock_kafka_consumer.return_value.close.assert_called_once()

    def test_connection_failure(self, mock_kafka_consumer):
        """Test connection failure raises KafkaConnectionError."""
        from kafka.errors import NoBrokersAvailable

        mock_kafka_consumer.side_effect = NoBrokersAvailable()

        with pytest.raises(KafkaConnectionError) as exc_info:
            KafkaConsumerClient("test-topic", "localhost:9092")

        assert "Failed to connect" in str(exc_info.value)
