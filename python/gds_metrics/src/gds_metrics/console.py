"""
Console metrics implementation for debugging.

This module provides a metrics implementation that
prints all metrics to stdout for development/debugging.
"""

from typing import Optional

__all__ = ["ConsoleMetrics"]


class ConsoleMetrics:
    """
    Print metrics to console for debugging.

    Useful during development to see what metrics are being recorded.
    Not recommended for production due to I/O overhead.

    Example:
        from gds_metrics import ConsoleMetrics

        metrics = ConsoleMetrics(prefix="myapp")
        metrics.increment("requests", labels={"status": "200"})
        # Output: [COUNTER] myapp.requests: +1 {'status': '200'}
    """

    def __init__(self, prefix: str = ""):
        """
        Initialize console metrics.

        Args:
            prefix: Optional prefix for all metric names
        """
        self._prefix = prefix

    def _format_name(self, name: str) -> str:
        """Format metric name with optional prefix."""
        if self._prefix:
            return f"{self._prefix}.{name}"
        return name

    def _format_labels(self, labels: Optional[dict[str, str]]) -> str:
        """Format labels for display."""
        if not labels:
            return ""
        return f" {labels}"

    def increment(self, name: str, value: int = 1, labels: Optional[dict[str, str]] = None) -> None:
        """Print counter increment to stdout."""
        formatted_name = self._format_name(name)
        formatted_labels = self._format_labels(labels)
        print(f"[COUNTER] {formatted_name}: +{value}{formatted_labels}")

    def gauge(self, name: str, value: float, labels: Optional[dict[str, str]] = None) -> None:
        """Print gauge value to stdout."""
        formatted_name = self._format_name(name)
        formatted_labels = self._format_labels(labels)
        print(f"[GAUGE] {formatted_name}: {value}{formatted_labels}")

    def histogram(self, name: str, value: float, labels: Optional[dict[str, str]] = None) -> None:
        """Print histogram observation to stdout."""
        formatted_name = self._format_name(name)
        formatted_labels = self._format_labels(labels)
        print(f"[HISTOGRAM] {formatted_name}: {value}{formatted_labels}")

    def timing(self, name: str, value_ms: float, labels: Optional[dict[str, str]] = None) -> None:
        """Print timing measurement to stdout."""
        formatted_name = self._format_name(name)
        formatted_labels = self._format_labels(labels)
        print(f"[TIMING] {formatted_name}: {value_ms:.2f}ms{formatted_labels}")

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"ConsoleMetrics(prefix={self._prefix!r})"

    def __str__(self) -> str:
        """User-friendly representation."""
        if self._prefix:
            return f"Console Metrics (prefix: {self._prefix})"
        return "Console Metrics"
