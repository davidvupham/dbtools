"""Tests for custom exceptions."""

import pytest
from gds_kafka import (
    GdsKafkaError,
    KafkaConnectionError,
    KafkaMessageError,
    KafkaSerializationError,
    KafkaTimeoutError,
)


class TestExceptionHierarchy:
    """Test exception class hierarchy."""

    def test_base_exception_exists(self):
        """Test GdsKafkaError can be instantiated."""
        exc = GdsKafkaError("test error")
        assert str(exc) == "test error"

    def test_connection_error_inherits_from_base(self):
        """Test KafkaConnectionError inherits from GdsKafkaError."""
        exc = KafkaConnectionError("connection failed")
        assert isinstance(exc, GdsKafkaError)
        assert isinstance(exc, Exception)

    def test_message_error_inherits_from_base(self):
        """Test KafkaMessageError inherits from GdsKafkaError."""
        exc = KafkaMessageError("message failed")
        assert isinstance(exc, GdsKafkaError)
        assert isinstance(exc, Exception)

    def test_serialization_error_inherits_from_base(self):
        """Test KafkaSerializationError inherits from GdsKafkaError."""
        exc = KafkaSerializationError("serialization failed")
        assert isinstance(exc, GdsKafkaError)
        assert isinstance(exc, Exception)

    def test_timeout_error_inherits_from_base(self):
        """Test KafkaTimeoutError inherits from GdsKafkaError."""
        exc = KafkaTimeoutError("timeout")
        assert isinstance(exc, GdsKafkaError)
        assert isinstance(exc, Exception)

    def test_catch_all_with_base_exception(self):
        """Test all custom exceptions can be caught with base class."""

        def raise_connection_error():
            raise KafkaConnectionError("test")

        def raise_message_error():
            raise KafkaMessageError("test")

        def raise_serialization_error():
            raise KafkaSerializationError("test")

        def raise_timeout_error():
            raise KafkaTimeoutError("test")

        # All should be catchable with GdsKafkaError
        for func in [
            raise_connection_error,
            raise_message_error,
            raise_serialization_error,
            raise_timeout_error,
        ]:
            with pytest.raises(GdsKafkaError):
                func()

    def test_exceptions_preserve_message(self):
        """Test exception messages are preserved."""
        exceptions = [
            (GdsKafkaError, "base error"),
            (KafkaConnectionError, "connection error"),
            (KafkaMessageError, "message error"),
            (KafkaSerializationError, "serialization error"),
            (KafkaTimeoutError, "timeout error"),
        ]

        for exc_class, message in exceptions:
            exc = exc_class(message)
            assert str(exc) == message

    def test_exception_chaining(self):
        """Test exceptions can be chained with 'from'."""
        original = ValueError("original error")

        try:
            try:
                raise original
            except ValueError as e:
                raise KafkaConnectionError("wrapped error") from e
        except KafkaConnectionError as exc:
            assert exc.__cause__ is original
            assert str(exc) == "wrapped error"
