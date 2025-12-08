"""
Retry mechanisms with exponential backoff.

This module provides retry logic for resilient operations,
particularly useful for network requests and remote service calls.
"""

import logging
import time
from functools import wraps
from typing import Any, Callable

import requests

logger = logging.getLogger(__name__)


class RetryPolicy:
    """
    Configurable retry policy with exponential backoff.

    This class encapsulates retry logic that can be reused across
    different operations, making it easier to test and configure.

    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        initial_delay: Initial delay in seconds before first retry (default: 1.0)
        max_delay: Maximum delay between retries in seconds (default: 32.0)
        backoff_factor: Multiplier for exponential backoff (default: 2.0)
        retriable_exceptions: Exceptions that trigger a retry

    Example:
        policy = RetryPolicy(max_retries=5, initial_delay=2.0)
        result = policy.execute(lambda: risky_operation())
    """

    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 32.0,
        backoff_factor: float = 2.0,
        retriable_exceptions: tuple = (requests.RequestException,),
    ):
        """Initialize retry policy."""
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.retriable_exceptions = retriable_exceptions

    def execute(self, operation: Callable[[], Any]) -> Any:
        """
        Execute operation with retry logic.

        Args:
            operation: Callable that performs the operation

        Returns:
            Result of the operation

        Raises:
            Exception: If operation fails after all retries
        """
        delay = self.initial_delay
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                return operation()
            except Exception as e:
                # Check if exception is retriable
                if not isinstance(e, self.retriable_exceptions):
                    # Not a retriable exception, raise immediately
                    raise

                last_exception = e

                if attempt == self.max_retries:
                    logger.error("Operation failed after %d retries: %s", self.max_retries, e)
                    raise

                # Calculate delay with exponential backoff
                current_delay = min(delay, self.max_delay)
                logger.warning(
                    "Attempt %d/%d failed: %s. Retrying in %.1fs...",
                    attempt + 1,
                    self.max_retries + 1,
                    e,
                    current_delay,
                )
                time.sleep(current_delay)
                delay *= self.backoff_factor

        # Should never reach here, but just in case
        if last_exception:
            raise last_exception

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"RetryPolicy(max_retries={self.max_retries}, "
            f"initial_delay={self.initial_delay}, "
            f"backoff_factor={self.backoff_factor})"
        )

    def __str__(self) -> str:
        """User-friendly representation."""
        return f"Retry Policy (max {self.max_retries} retries)"


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 32.0,
    backoff_factor: float = 2.0,
    retriable_exceptions: tuple = (requests.RequestException,),
) -> Callable:
    """
    Decorator that retries a function with exponential backoff.

    This decorator wraps a function to automatically retry on failure
    with configurable exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds before first retry
        max_delay: Maximum delay between retries in seconds
        backoff_factor: Multiplier for exponential backoff
        retriable_exceptions: Tuple of exceptions that trigger a retry

    Returns:
        Decorated function that retries on failure

    Example:
        @retry_with_backoff(max_retries=3, initial_delay=1.0)
        def fetch_data():
            return requests.get('https://api.example.com/data')
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            policy = RetryPolicy(
                max_retries=max_retries,
                initial_delay=initial_delay,
                max_delay=max_delay,
                backoff_factor=backoff_factor,
                retriable_exceptions=retriable_exceptions,
            )
            return policy.execute(lambda: func(*args, **kwargs))

        return wrapper

    return decorator
