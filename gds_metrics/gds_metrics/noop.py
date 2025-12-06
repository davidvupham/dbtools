"""
No-operation metrics implementation.

This module provides a null object pattern implementation
that discards all metrics with zero overhead.
"""

from typing import Optional

__all__ = ["NoOpMetrics"]


class NoOpMetrics:
    """
    Null object pattern - discards all metrics.

    This is the default implementation when metrics are disabled.
    All methods do nothing, providing zero overhead.

    Example:
        from gds_metrics import NoOpMetrics

        metrics = NoOpMetrics()
        metrics.increment("requests")  # Does nothing
    """

    def increment(
        self, name: str, value: int = 1, labels: Optional[dict[str, str]] = None
    ) -> None:
        """Discard counter increment."""
        pass

    def gauge(
        self, name: str, value: float, labels: Optional[dict[str, str]] = None
    ) -> None:
        """Discard gauge value."""
        pass

    def histogram(
        self, name: str, value: float, labels: Optional[dict[str, str]] = None
    ) -> None:
        """Discard histogram observation."""
        pass

    def timing(
        self, name: str, value_ms: float, labels: Optional[dict[str, str]] = None
    ) -> None:
        """Discard timing measurement."""
        pass

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return "NoOpMetrics()"

    def __str__(self) -> str:
        """User-friendly representation."""
        return "No-Op Metrics (disabled)"
