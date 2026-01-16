"""Pytest configuration and shared fixtures for gds_kafka tests."""

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_kafka_producer():
    """Create a mock Kafka producer for testing."""
    mock = MagicMock()
    mock.send = MagicMock()
    mock.flush = MagicMock()
    mock.close = MagicMock()
    return mock


@pytest.fixture
def mock_kafka_consumer():
    """Create a mock Kafka consumer for testing."""
    mock = MagicMock()
    mock.subscribe = MagicMock()
    mock.poll = MagicMock(return_value=None)
    mock.close = MagicMock()
    return mock


@pytest.fixture
def sample_kafka_config() -> dict:
    """Return sample Kafka configuration for testing."""
    return {
        "bootstrap_servers": "localhost:9092",
        "client_id": "test-client",
    }
