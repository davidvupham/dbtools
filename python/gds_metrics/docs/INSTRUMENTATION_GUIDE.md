# Application Instrumentation Guide

This guide covers how to instrument applications and scripts for observability within the GDS observability architecture.

## Quick Start

### Python Application

```python
from gds_metrics import OpenTelemetryMetrics

# Initialize metrics with service info
metrics = OpenTelemetryMetrics(
    service_name="my-service",
    service_version="1.0.0"
)

# Record metrics (trace context auto-attached)
metrics.increment("http_requests_total", labels={"status": "200"})
metrics.timing("db_query_ms", 45.2, labels={"operation": "SELECT"})
```

---

## Installation

```bash
# Basic install
pip install gds-metrics

# With OpenTelemetry support
pip install gds-metrics[opentelemetry]

# With all backends
pip install gds-metrics[all]
```

---

## Python Instrumentation

### 1. Basic Metrics

```python
from gds_metrics import OpenTelemetryMetrics

metrics = OpenTelemetryMetrics(service_name="my-api")

# Counter - cumulative, only increases
metrics.increment("requests_total", labels={"endpoint": "/api/users"})

# Gauge - value that goes up/down
metrics.gauge("active_connections", 42, labels={"pool": "primary"})

# Histogram - distribution of values
metrics.histogram("request_duration_seconds", 0.153)

# Timing - convenience for durations
metrics.timing("db_query_ms", 23.5, labels={"query": "user_lookup"})
```

### 2. Full Observability (Traces + Metrics)

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from gds_metrics import OpenTelemetryMetrics

# Setup tracing
resource = Resource.create({
    "service.name": "my-service",
    "service.version": "1.0.0",
})

provider = TracerProvider(resource=resource)
provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint="http://otel-collector:4317"))
)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

# Setup metrics (shares trace context automatically)
metrics = OpenTelemetryMetrics(service_name="my-service")

# Use both together
@app.route("/api/process")
def process_request():
    with tracer.start_as_current_span("process_request") as span:
        span.set_attribute("request.id", request_id)

        # Metrics auto-include trace_id/span_id
        metrics.increment("process_requests_total")

        result = do_work()
        metrics.timing("process_duration_ms", duration)
        return result
```

### 3. Auto-Instrumentation

```python
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

# Auto-instrument frameworks (call at startup)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()
SQLAlchemyInstrumentor().instrument()
```

---

## PowerShell Instrumentation

### 1. Trace Context Generation

```powershell
function New-TraceContext {
    $traceId = [Guid]::NewGuid().ToString("N")
    $spanId = [Guid]::NewGuid().ToString("N").Substring(0, 16)
    @{
        TraceId = $traceId
        SpanId = $spanId
        TraceParent = "00-$traceId-$spanId-01"
    }
}

# Usage
$ctx = New-TraceContext
Invoke-RestMethod -Uri "https://api/endpoint" -Headers @{
    "traceparent" = $ctx.TraceParent
}
```

### 2. Metrics via HTTP

```powershell
function Send-Metric {
    param(
        [string]$Name,
        [double]$Value,
        [hashtable]$Labels = @{},
        [string]$Endpoint = "http://localhost:4318/v1/metrics"
    )

    $payload = @{
        resourceMetrics = @(@{
            resource = @{ attributes = @(@{ key = "service.name"; value = @{ stringValue = "ps-script" }}) }
            scopeMetrics = @(@{
                metrics = @(@{
                    name = $Name
                    gauge = @{ dataPoints = @(@{ asDouble = $Value }) }
                })
            })
        })
    }

    Invoke-RestMethod -Uri $Endpoint -Method Post -Body ($payload | ConvertTo-Json -Depth 10) -ContentType "application/json"
}

# Usage
Send-Metric -Name "backup_duration_seconds" -Value 120.5 -Labels @{database="prod"}
```

---

## Best Practices

| Practice | Description |
|----------|-------------|
| **Use semantic naming** | `http_requests_total`, `db_query_duration_seconds` |
| **Add meaningful labels** | `method`, `status`, `endpoint`, `environment` |
| **Propagate trace context** | Include `traceparent` header in inter-service calls |
| **Use auto-instrumentation** | Leverage OTel instrumentors for common libraries |
| **Set resource attributes** | `service.name`, `service.version`, `deployment.environment` |

---

## Multi-Backend Support

```python
from gds_metrics import CompositeMetrics, OpenTelemetryMetrics, PrometheusMetrics, ConsoleMetrics

# Send to multiple backends simultaneously
metrics = CompositeMetrics([
    OpenTelemetryMetrics(service_name="my-service"),
    PrometheusMetrics(prefix="myapp", port=8080),
    ConsoleMetrics(),  # Debug output
])

metrics.increment("request_count")  # Sent to all backends
```

---

## Integration with Observability Architecture

```
┌──────────────────┐
│  Your App        │
│  ┌────────────┐  │
│  │gds_metrics │──┼──► OpenTelemetry Collector ──► Kafka ──► Prometheus
│  │            │  │                                    │       Jaeger
│  └────────────┘  │                                    │       Loki
└──────────────────┘                                    ▼
                                                   Snowflake
                                                   (Analytics)
```

See [OPENTELEMETRY_ARCHITECTURE.md](../../architecture/observability/OPENTELEMETRY_ARCHITECTURE.md) for details.
