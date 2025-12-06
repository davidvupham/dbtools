"""
gds_metrics: Unified metrics collection for GDS tooling.

This package provides a protocol-based metrics system supporting
multiple backends including Prometheus and OpenTelemetry, with a
pluggable architecture for adding additional backends such as Kafka.
"""

from gds_metrics.base import MetricsCollector
from gds_metrics.composite import CompositeMetrics
from gds_metrics.console import ConsoleMetrics
from gds_metrics.context import get_current_trace_context, with_trace_context
from gds_metrics.noop import NoOpMetrics

# Optional imports - Prometheus
try:
    from gds_metrics.prometheus import PrometheusMetrics

    _PROMETHEUS_AVAILABLE = True
except ImportError:
    _PROMETHEUS_AVAILABLE = False
    PrometheusMetrics = None

# Optional imports - OpenTelemetry
try:
    from gds_metrics.opentelemetry import OpenTelemetryMetrics

    _OPENTELEMETRY_AVAILABLE = True
except ImportError:
    _OPENTELEMETRY_AVAILABLE = False
    OpenTelemetryMetrics = None

__version__ = "0.2.0"

__all__ = [
    # Protocol
    "MetricsCollector",
    # Implementations
    "NoOpMetrics",
    "ConsoleMetrics",
    "CompositeMetrics",
    # Optional backends
    "PrometheusMetrics",
    "OpenTelemetryMetrics",
    # Context utilities
    "get_current_trace_context",
    "with_trace_context",
]
