"""Kafka producer client with connection management and error handling."""

import json
import logging
from typing import Any, Optional

from kafka import KafkaProducer
from kafka.errors import (
    KafkaError,
    NoBrokersAvailable,
)
from kafka.errors import (
    KafkaTimeoutError as KafkaLibTimeoutError,
)

from .exceptions import (
    KafkaConnectionError,
    KafkaMessageError,
    KafkaSerializationError,
    KafkaTimeoutError,
)

logger = logging.getLogger(__name__)


class KafkaProducerClient:
    """Reusable Kafka producer with connection management.

    Provides a simple interface for sending messages to Kafka topics
    with proper error handling and resource cleanup.

    Args:
        bootstrap_servers: Comma-separated list of broker addresses.
        **config: Additional configuration passed to KafkaProducer.

    Raises:
        KafkaConnectionError: If connection to brokers fails.

    Example:
        >>> with KafkaProducerClient("localhost:9092") as producer:
        ...     producer.send("my-topic", {"key": "value"})
        ...     producer.flush()
    """

    def __init__(self, bootstrap_servers: str, **config: Any):
        default_config = {
            "value_serializer": lambda v: json.dumps(v).encode("utf-8"),
            "bootstrap_servers": bootstrap_servers,
        }
        default_config.update(config)

        try:
            self.producer = KafkaProducer(**default_config)
        except NoBrokersAvailable as e:
            raise KafkaConnectionError(f"Failed to connect to Kafka brokers: {bootstrap_servers}") from e
        except KafkaError as e:
            raise KafkaConnectionError(f"Kafka connection error: {e}") from e

    def send(self, topic: str, value: dict[str, Any], key: Optional[str] = None) -> None:
        """Send a message to a Kafka topic.

        Args:
            topic: Target topic name.
            value: Message payload (will be JSON serialized).
            key: Optional message key for partitioning.

        Raises:
            KafkaSerializationError: If message serialization fails.
            KafkaMessageError: If send operation fails.
            KafkaTimeoutError: If send operation times out.
        """
        try:
            key_bytes = key.encode("utf-8") if key else None
            self.producer.send(topic, value=value, key=key_bytes)
        except TypeError as e:
            raise KafkaSerializationError(f"Failed to serialize message: {e}") from e
        except KafkaLibTimeoutError as e:
            raise KafkaTimeoutError(f"Send operation timed out: {e}") from e
        except KafkaError as e:
            raise KafkaMessageError(f"Failed to send message: {e}") from e

    def flush(self, timeout: Optional[float] = None) -> None:
        """Flush pending messages.

        Args:
            timeout: Maximum time to wait in seconds.

        Raises:
            KafkaTimeoutError: If flush times out.
        """
        try:
            self.producer.flush(timeout=timeout)
        except KafkaLibTimeoutError as e:
            raise KafkaTimeoutError(f"Flush operation timed out: {e}") from e

    def close(self, timeout: Optional[float] = None) -> None:
        """Close the producer.

        Args:
            timeout: Maximum time to wait for cleanup in seconds.
        """
        try:
            self.producer.close(timeout=timeout)
        except Exception as e:
            logger.warning(f"Error closing producer: {e}")

    def __enter__(self) -> "KafkaProducerClient":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
