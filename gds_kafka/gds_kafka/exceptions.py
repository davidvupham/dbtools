"""
Custom exceptions for the gds_kafka package.

This module defines a hierarchy of exceptions for handling
Kafka-related errors in a consistent manner.
"""


class GdsKafkaError(Exception):
    """Base exception for gds_kafka package.

    All custom exceptions in this package inherit from this class,
    allowing consumers to catch all package-specific errors with
    a single except clause.
    """

    pass


class KafkaConnectionError(GdsKafkaError):
    """Raised when connection to Kafka broker fails.

    This includes scenarios such as:
    - No brokers available
    - Network connectivity issues
    - Authentication failures
    """

    pass


class KafkaMessageError(GdsKafkaError):
    """Raised when message send/receive operation fails.

    This includes scenarios such as:
    - Topic does not exist
    - Message too large
    - Producer/consumer not connected
    """

    pass


class KafkaSerializationError(GdsKafkaError):
    """Raised when message serialization/deserialization fails.

    This includes scenarios such as:
    - JSON encoding failures
    - JSON decoding failures
    - Invalid message format
    """

    pass


class KafkaTimeoutError(GdsKafkaError):
    """Raised when a Kafka operation times out.

    This includes scenarios such as:
    - Send timeout
    - Flush timeout
    - Consumer poll timeout
    """

    pass
