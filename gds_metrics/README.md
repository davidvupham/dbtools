# GDS Metrics

A unified metrics collection package for the GDS tooling ecosystem. Provides a protocol-based architecture supporting OpenTelemetry, Prometheus, Kafka, and custom backends.

## Installation

```bash
# Base package (includes NoOpMetrics, ConsoleMetrics)
pip install gds-metrics

# With OpenTelemetry support (recommended)
pip install gds-metrics[opentelemetry]

# With Prometheus support
pip install gds-metrics[prometheus]

# With all backends
pip install gds-metrics[all]

# With Kafka support (requires gds-kafka)
pip install gds-metrics gds-kafka
```

## Quick Start

```python
from gds_metrics import NoOpMetrics, OpenTelemetryMetrics, PrometheusMetrics

# OpenTelemetry: Unified observability with trace context (recommended)
metrics = OpenTelemetryMetrics(service_name="my-service")

# Prometheus: Expose /metrics endpoint
metrics = PrometheusMetrics(prefix="myapp", port=8080)

# Default: No-op (does nothing, zero overhead)
metrics = NoOpMetrics()

# Use in your application
metrics.increment("requests_total", labels={"endpoint": "/api/users"})
metrics.histogram("request_duration_seconds", 0.125)
metrics.gauge("active_connections", 42)
metrics.timing("db_query_ms", 45.2)
```

## OpenTelemetry Integration

The `OpenTelemetryMetrics` backend automatically enriches metrics with trace context for correlation:

```python
from opentelemetry import trace
from gds_metrics import OpenTelemetryMetrics

tracer = trace.get_tracer(__name__)
metrics = OpenTelemetryMetrics(service_name="my-service")

with tracer.start_as_current_span("process_request"):
    # Metrics auto-include trace_id and span_id
    metrics.increment("requests_handled")
    metrics.timing("processing_ms", 23.5)
```

See [docs/INSTRUMENTATION_GUIDE.md](docs/INSTRUMENTATION_GUIDE.md) for detailed instrumentation patterns.

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture documentation.

## Supported Backends

| Backend | Description | Dependency |
|---------|-------------|------------|
| `NoOpMetrics` | Does nothing (default) | None |
| `ConsoleMetrics` | Prints to stdout | None |
| `OpenTelemetryMetrics` | OTel with trace context | `opentelemetry-*` |
| `PrometheusMetrics` | Prometheus /metrics endpoint | `prometheus-client` |
| `KafkaMetrics` | Stream to Kafka | `gds-kafka` |
| `CompositeMetrics` | Fan-out to multiple backends | None |

## Multi-Backend Support

Send metrics to multiple backends simultaneously:

```python
from gds_metrics import CompositeMetrics, OpenTelemetryMetrics, PrometheusMetrics

metrics = CompositeMetrics([
    OpenTelemetryMetrics(service_name="my-service"),
    PrometheusMetrics(prefix="myapp", port=8080),
])

metrics.increment("requests")  # Sent to both backends
```

## Kafka Integration

Stream metrics to Kafka for the observability pipeline:

```python
from gds_kafka import KafkaProducerClient, KafkaMetrics

producer = KafkaProducerClient("localhost:9092")
metrics = KafkaMetrics(producer, topic="gds.metrics.telemetry")

metrics.increment("events_processed", labels={"type": "order"})
```

## API Reference

### MetricsCollector Protocol

All metrics implementations follow this protocol:

```python
class MetricsCollector(Protocol):
    def increment(self, name: str, value: int = 1, labels: dict = None) -> None: ...
    def gauge(self, name: str, value: float, labels: dict = None) -> None: ...
    def histogram(self, name: str, value: float, labels: dict = None) -> None: ...
    def timing(self, name: str, value_ms: float, labels: dict = None) -> None: ...
```

### Trace Context Utilities

```python
from gds_metrics import get_current_trace_context, with_trace_context

# Get current trace context
ctx = get_current_trace_context()
# {'trace_id': '4bf92f3577...', 'span_id': '00f067aa...'}

# Enrich labels with trace context
labels = with_trace_context({"env": "prod"})
# {'env': 'prod', 'trace_id': '...', 'span_id': '...'}
```

## Contributing

See [docs/DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md) for development setup and contributing guidelines.

## Related Tutorials

For learning about observability concepts and instrumentation patterns, see the [Observability Tutorial](../docs/tutorials/observability/):

- [OpenTelemetry Deep Dive](../docs/tutorials/observability/04_OPENTELEMETRY.md) - Comprehensive OTel guide
- [Python Integration](../docs/tutorials/observability/06_PYTHON_INTEGRATION.md) - Python instrumentation patterns
- [Best Practices](../docs/tutorials/observability/09_BEST_PRACTICES.md) - Design patterns and SOLID principles

## License

MIT
