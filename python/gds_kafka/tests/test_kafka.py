from unittest.mock import patch

import pytest

from gds_kafka import KafkaLoggingHandler, KafkaMetrics, KafkaProducerClient


@pytest.fixture
def mock_kafka_producer():
    with patch("gds_kafka.producer.KafkaProducer") as mock:
        yield mock


def test_producer_client(mock_kafka_producer):
    client = KafkaProducerClient(bootstrap_servers="localhost:9092")
    client.send("test-topic", {"foo": "bar"})
    mock_kafka_producer.return_value.send.assert_called_once()


def test_metrics(mock_kafka_producer):
    client = KafkaProducerClient(bootstrap_servers="localhost:9092")
    metrics = KafkaMetrics(client, topic="metrics")
    metrics.increment("test_counter", 1)

    # Check if send was called on producer
    args = mock_kafka_producer.return_value.send.call_args
    assert args[0][0] == "metrics"
    assert args[1]["value"]["name"] == "test_counter"
    assert args[1]["value"]["type"] == "counter"


def test_logging(mock_kafka_producer):
    client = KafkaProducerClient(bootstrap_servers="localhost:9092")
    handler = KafkaLoggingHandler(client, topic="logs")

    import logging

    logger = logging.getLogger("test_logger")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    # We strip handlers after test to avoid pollution, but for this test we act locally
    logger.info("Hello Kafka")

    args = mock_kafka_producer.return_value.send.call_args
    assert args[0][0] == "logs"
    assert args[1]["value"]["message"] == "Hello Kafka"
