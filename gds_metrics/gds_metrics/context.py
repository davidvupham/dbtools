"""
Trace context utilities for OpenTelemetry integration.

This module provides helpers for extracting and propagating
trace context (trace_id, span_id) across metrics and logs.
"""

from typing import Optional

__all__ = ["get_current_trace_context", "with_trace_context"]


def get_current_trace_context() -> dict[str, str]:
    """
    Extract trace context from the current OpenTelemetry span.

    Returns a dictionary with trace_id and span_id if a span is active,
    otherwise returns an empty dict. This allows metrics to be correlated
    with traces in observability backends.

    Returns:
        dict with 'trace_id' and 'span_id' keys if span active, else empty dict

    Example:
        from gds_metrics.context import get_current_trace_context

        # Inside a traced operation
        ctx = get_current_trace_context()
        # ctx = {'trace_id': '4bf92f3577b34da6...', 'span_id': '00f067aa0ba902b7'}
    """
    try:
        from opentelemetry import trace

        span = trace.get_current_span()
        if span is None:
            return {}

        ctx = span.get_span_context()
        if ctx is None or not ctx.is_valid:
            return {}

        return {
            "trace_id": format(ctx.trace_id, "032x"),
            "span_id": format(ctx.span_id, "016x"),
        }
    except ImportError:
        # OpenTelemetry not installed
        return {}
    except Exception:
        # Any other error, fail silently
        return {}


def with_trace_context(
    labels: Optional[dict[str, str]] = None,
    include_trace_context: bool = True,
) -> dict[str, str]:
    """
    Enrich labels with trace context if available.

    Merges the provided labels with the current trace context
    (trace_id, span_id). Existing labels are preserved;
    trace context is added only if not already present.

    Args:
        labels: Existing labels/tags to enrich (optional)
        include_trace_context: Whether to add trace context (default True)

    Returns:
        Labels enriched with trace context (new dict, original not modified)

    Example:
        from gds_metrics.context import with_trace_context

        # Enrich metric labels with trace context
        labels = with_trace_context({"endpoint": "/api/users"})
        # labels = {'endpoint': '/api/users', 'trace_id': '...', 'span_id': '...'}
    """
    result = dict(labels) if labels else {}

    if include_trace_context:
        ctx = get_current_trace_context()
        for key, value in ctx.items():
            if key not in result:  # Don't override existing labels
                result[key] = value

    return result
