"""Tests for retry mechanisms."""

import time
import unittest
from unittest.mock import Mock

from gds_vault.retry import RetryPolicy, retry_with_backoff


class TestRetryPolicy(unittest.TestCase):
    """Test RetryPolicy class."""

    def test_init(self):
        """Test retry policy initialization."""
        policy = RetryPolicy(
            max_retries=5,
            initial_delay=2.0,
            max_delay=60.0,
            backoff_factor=3.0,
        )
        self.assertEqual(policy.max_retries, 5)
        self.assertEqual(policy.initial_delay, 2.0)
        self.assertEqual(policy.max_delay, 60.0)
        self.assertEqual(policy.backoff_factor, 3.0)

    def test_successful_execution(self):
        """Test successful execution without retry."""
        policy = RetryPolicy()
        operation = Mock(return_value="success")

        result = policy.execute(operation)

        self.assertEqual(result, "success")
        operation.assert_called_once()

    def test_retry_on_failure(self):
        """Test retry on retriable exception."""
        policy = RetryPolicy(
            max_retries=3, initial_delay=0.1, retriable_exceptions=(Exception,)
        )

        # Fail twice, then succeed
        operation = Mock(
            side_effect=[Exception("fail1"), Exception("fail2"), "success"]
        )

        result = policy.execute(operation)

        self.assertEqual(result, "success")
        self.assertEqual(operation.call_count, 3)

    def test_max_retries_exceeded(self):
        """Test that operation fails after max retries."""
        policy = RetryPolicy(
            max_retries=2, initial_delay=0.1, retriable_exceptions=(Exception,)
        )
        operation = Mock(side_effect=Exception("persistent failure"))

        with self.assertRaises(Exception) as context:
            policy.execute(operation)

        self.assertIn("persistent failure", str(context.exception))
        self.assertEqual(operation.call_count, 3)  # Initial + 2 retries

    def test_non_retriable_exception(self):
        """Test that non-retriable exceptions are not retried."""
        policy = RetryPolicy(
            max_retries=3, initial_delay=0.1, retriable_exceptions=(ValueError,)
        )

        operation = Mock(side_effect=TypeError("not retriable"))

        with self.assertRaises(TypeError):
            policy.execute(operation)

        operation.assert_called_once()  # No retries

    def test_exponential_backoff(self):
        """Test exponential backoff timing."""
        policy = RetryPolicy(
            max_retries=3,
            initial_delay=0.1,
            backoff_factor=2.0,
            retriable_exceptions=(Exception,),
        )

        operation = Mock(side_effect=[Exception("fail")] * 3 + ["success"])
        start_time = time.time()

        result = policy.execute(operation)

        elapsed = time.time() - start_time

        # Should have delays: 0.1, 0.2, 0.4 = 0.7 total
        # Allow some margin for execution time
        self.assertGreaterEqual(elapsed, 0.6)
        self.assertEqual(result, "success")

    def test_max_delay_cap(self):
        """Test that delay is capped at max_delay."""
        policy = RetryPolicy(
            max_retries=5,
            initial_delay=10.0,
            max_delay=2.0,
            backoff_factor=2.0,
            retriable_exceptions=(Exception,),
        )

        # All delays should be capped at 2.0 seconds
        operation = Mock(side_effect=[Exception("fail")] * 5 + ["success"])

        start_time = time.time()
        result = policy.execute(operation)
        elapsed = time.time() - start_time

        # Should have 5 delays of 2.0 seconds each = 10 seconds total
        # Allow margin for execution time
        self.assertGreaterEqual(elapsed, 9.0)
        self.assertLess(elapsed, 15.0)  # Should not take too long
        self.assertEqual(result, "success")

    def test_repr(self):
        """Test __repr__ method."""
        policy = RetryPolicy(max_retries=5, initial_delay=2.0)
        repr_str = repr(policy)
        self.assertIn("RetryPolicy", repr_str)
        self.assertIn("5", repr_str)
        self.assertIn("2.0", repr_str)

    def test_str(self):
        """Test __str__ method."""
        policy = RetryPolicy(max_retries=5)
        str_repr = str(policy)
        self.assertIn("Retry Policy", str_repr)
        self.assertIn("5", str_repr)


class TestRetryDecorator(unittest.TestCase):
    """Test retry_with_backoff decorator."""

    def test_decorator_successful_call(self):
        """Test decorator with successful call."""

        @retry_with_backoff(max_retries=3, initial_delay=0.1)
        def successful_function():
            return "success"

        result = successful_function()
        self.assertEqual(result, "success")

    def test_decorator_with_retries(self):
        """Test decorator retries on failure."""
        call_count = {"count": 0}

        @retry_with_backoff(
            max_retries=3, initial_delay=0.1, retriable_exceptions=(Exception,)
        )
        def flaky_function():
            call_count["count"] += 1
            if call_count["count"] < 3:
                raise Exception("temporary failure")
            return "success"

        result = flaky_function()
        self.assertEqual(result, "success")
        self.assertEqual(call_count["count"], 3)

    def test_decorator_max_retries(self):
        """Test decorator fails after max retries."""

        @retry_with_backoff(max_retries=2, initial_delay=0.1)
        def always_fails():
            raise Exception("always fails")

        with self.assertRaises(Exception):
            always_fails()

    def test_decorator_with_arguments(self):
        """Test decorator preserves function arguments."""

        @retry_with_backoff(max_retries=2, initial_delay=0.1)
        def add_numbers(a, b):
            return a + b

        result = add_numbers(3, 5)
        self.assertEqual(result, 8)

    def test_decorator_with_kwargs(self):
        """Test decorator preserves keyword arguments."""

        @retry_with_backoff(max_retries=2, initial_delay=0.1)
        def greet(name, greeting="Hello"):
            return f"{greeting}, {name}!"

        result = greet("World", greeting="Hi")
        self.assertEqual(result, "Hi, World!")


if __name__ == "__main__":
    unittest.main()
