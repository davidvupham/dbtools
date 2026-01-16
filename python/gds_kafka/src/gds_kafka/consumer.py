"""Kafka consumer client with connection management and error handling."""

import json
import logging
from collections.abc import Generator
from typing import Any, Optional

from kafka import KafkaConsumer
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


class KafkaConsumerClient:
    """Reusable Kafka consumer with connection management.

    Provides a simple interface for consuming messages from Kafka topics
    with proper error handling and resource cleanup.

    Args:
        topic: Topic to subscribe to.
        bootstrap_servers: Comma-separated list of broker addresses.
        group_id: Consumer group ID for offset management.
        **config: Additional configuration passed to KafkaConsumer.

    Raises:
        KafkaConnectionError: If connection to brokers fails.

    Example:
        >>> with KafkaConsumerClient("my-topic", "localhost:9092") as consumer:
        ...     for message in consumer.messages():
        ...         print(message["value"])
    """

    def __init__(
        self,
        topic: str,
        bootstrap_servers: str,
        group_id: Optional[str] = None,
        **config: Any,
    ):
        default_config = {
            "value_deserializer": lambda v: json.loads(v.decode("utf-8")) if v else None,
            "bootstrap_servers": bootstrap_servers,
            "group_id": group_id,
            "auto_offset_reset": "earliest",
        }
        default_config.update(config)

        try:
            self.consumer = KafkaConsumer(topic, **default_config)
        except NoBrokersAvailable as e:
            raise KafkaConnectionError(f"Failed to connect to Kafka brokers: {bootstrap_servers}") from e
        except KafkaError as e:
            raise KafkaConnectionError(f"Kafka connection error: {e}") from e

    def messages(self) -> Generator[dict[str, Any], None, None]:
        """Yield messages from the topic.

        Yields:
            Dictionary containing message data with keys:
                - key: Message key (decoded string or None)
                - value: Deserialized message value
                - topic: Source topic name
                - partition: Partition number
                - offset: Message offset

        Raises:
            KafkaSerializationError: If message deserialization fails.
            KafkaMessageError: If message consumption fails.
            KafkaTimeoutError: If poll operation times out.
        """
        try:
            for message in self.consumer:
                try:
                    yield {
                        "key": message.key.decode("utf-8") if message.key else None,
                        "value": message.value,
                        "topic": message.topic,
                        "partition": message.partition,
                        "offset": message.offset,
                    }
                except (json.JSONDecodeError, UnicodeDecodeError) as e:
                    raise KafkaSerializationError(f"Failed to deserialize message: {e}") from e
        except KafkaLibTimeoutError as e:
            raise KafkaTimeoutError(f"Consumer poll timed out: {e}") from e
        except KafkaError as e:
            raise KafkaMessageError(f"Failed to consume message: {e}") from e

    def close(self) -> None:
        """Close the consumer."""
        try:
            self.consumer.close()
        except Exception as e:
            logger.warning(f"Error closing consumer: {e}")

    def __enter__(self) -> "KafkaConsumerClient":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
