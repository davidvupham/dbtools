# Observability Quick Reference

A cheat sheet for common observability tasks and patterns.

---

## OpenTelemetry Setup

### Python Quick Start

```bash
pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp
pip install opentelemetry-instrumentation-flask
pip install opentelemetry-instrumentation-requests
```

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

# Initialize
resource = Resource.create({"service.name": "my-service"})
provider = TracerProvider(resource=resource)
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint="http://collector:4317")))
trace.set_tracer_provider(provider)

# Use
tracer = trace.get_tracer(__name__)
with tracer.start_as_current_span("operation"):
    # Your code here
```

### Flask Auto-Instrumentation

```python
from opentelemetry.instrumentation.flask import FlaskInstrumentor
FlaskInstrumentor().instrument_app(app)
```

---

## Structured Logging

### Python JSON Logger

```python
import logging, json
from opentelemetry import trace

class JSONFormatter(logging.Formatter):
    def format(self, record):
        span = trace.get_current_span()
        ctx = span.get_span_context()
        return json.dumps({
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "trace_id": format(ctx.trace_id, '032x') if ctx.trace_id else None,
            "span_id": format(ctx.span_id, '016x') if ctx.span_id else None,
        })
```

### PowerShell JSON Logger

```powershell
function Write-JsonLog {
    param([string]$Level, [string]$Message, [hashtable]$Context = @{})
    @{
        timestamp = (Get-Date).ToUniversalTime().ToString('o')
        level = $Level
        message = $Message
        context = $Context
    } | ConvertTo-Json -Compress | Write-Output
}
```

---

## Kafka Commands

### Topic Operations

```bash
# Create topic
kafka-topics.sh --create --topic gds.metrics.production \
  --partitions 12 --replication-factor 3 \
  --bootstrap-server kafka:9092

# List topics
kafka-topics.sh --list --bootstrap-server kafka:9092

# Describe topic
kafka-topics.sh --describe --topic gds.metrics.production \
  --bootstrap-server kafka:9092

# Delete topic
kafka-topics.sh --delete --topic gds.metrics.production \
  --bootstrap-server kafka:9092
```

### Consumer Operations

```bash
# Consume from beginning
kafka-console-consumer.sh --topic gds.metrics.production \
  --from-beginning --bootstrap-server kafka:9092

# Check consumer group lag
kafka-consumer-groups.sh --describe --group gds-alerting \
  --bootstrap-server kafka:9092
```

### Python Producer

```python
from confluent_kafka import Producer
producer = Producer({'bootstrap.servers': 'kafka:9092', 'acks': 'all'})
producer.produce('topic', key='key', value='value')
producer.flush()
```

### Python Consumer

```python
from confluent_kafka import Consumer
consumer = Consumer({
    'bootstrap.servers': 'kafka:9092',
    'group.id': 'my-group',
    'auto.offset.reset': 'earliest'
})
consumer.subscribe(['topic'])
while True:
    msg = consumer.poll(1.0)
    if msg and not msg.error():
        process(msg.value())
        consumer.commit()
```

---

## OpenTelemetry Collector Config

### Basic Config

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
    timeout: 10s
    send_batch_size: 1000

exporters:
  otlp:
    endpoint: backend:4317
  prometheus:
    endpoint: 0.0.0.0:8889

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlp]
    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [prometheus]
```

---

## Context Propagation

### W3C Trace Context Header

```
traceparent: 00-{trace_id}-{span_id}-{flags}
Example:    00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
```

### Python - Inject/Extract

```python
from opentelemetry.propagate import inject, extract

# Outgoing request
headers = {}
inject(headers)
requests.get(url, headers=headers)

# Incoming request
ctx = extract(request.headers)
with tracer.start_as_current_span("op", context=ctx):
    process()
```

### PowerShell

```powershell
$traceId = [Guid]::NewGuid().ToString("N") + [Guid]::NewGuid().ToString("N").Substring(0, 16)
$spanId = [Guid]::NewGuid().ToString("N").Substring(0, 16)
$traceparent = "00-$traceId-$spanId-01"
Invoke-RestMethod -Uri $url -Headers @{ "traceparent" = $traceparent }
```

---

## Common Metrics

### Counter (always increases)

```python
counter = meter.create_counter("requests_total")
counter.add(1, {"status": "success"})
```

### Histogram (distribution)

```python
histogram = meter.create_histogram("request_duration_ms")
histogram.record(150.5, {"method": "GET"})
```

### Gauge (current value)

```python
gauge = meter.create_up_down_counter("active_connections")
gauge.add(1)   # connection opened
gauge.add(-1)  # connection closed
```

---

## Alert Rule Template

```python
AlertRule(
    id="unique_id",
    name="Human Readable Name",
    description="What this alert means",
    metric_name="metric_name",
    operator=Operator.GT,  # GT, GTE, LT, LTE, EQ, NEQ
    threshold=80,
    severity=AlertSeverity.HIGH,  # CRITICAL, HIGH, MEDIUM, LOW
    duration=300,    # Seconds condition must be true
    cooldown=900,    # Seconds between re-alerts
    runbook_url="https://wiki/runbook",
    filters={"environment": "production"}
)
```

---

## Semantic Conventions

### Resource Attributes

| Attribute | Example |
|-----------|---------|
| `service.name` | `user-service` |
| `service.version` | `1.2.3` |
| `deployment.environment` | `production` |

### HTTP Attributes

| Attribute | Example |
|-----------|---------|
| `http.method` | `GET` |
| `http.status_code` | `200` |
| `http.route` | `/users/{id}` |
| `http.url` | `https://api.example.com/users/123` |

### Database Attributes

| Attribute | Example |
|-----------|---------|
| `db.system` | `postgresql` |
| `db.name` | `users` |
| `db.operation` | `SELECT` |
| `db.statement` | `SELECT * FROM users WHERE id = ?` |

---

## Troubleshooting

### No Traces Appearing

1. Check collector is running: `curl http://collector:4317`
2. Verify exporter endpoint is correct
3. Check for sampling (are traces being dropped?)
4. Look at collector logs: `docker logs otel-collector`

### High Consumer Lag

1. Add more consumers to the group
2. Increase `fetch.min.bytes` and `fetch.wait.max.ms`
3. Process in batches
4. Check for slow processing in consumer

### Missing Log Trace Context

1. Ensure OpenTelemetry is initialized before logging setup
2. Use `LoggingInstrumentor().instrument()`
3. Or manually get span context in formatter

### Alert Not Firing

1. Check rule filters match metric labels
2. Verify threshold and operator
3. Check duration (condition might not be sustained)
4. Look at evaluator logs

---

## Docker Compose Stack

```yaml
version: '3.8'
services:
  otel-collector:
    image: otel/opentelemetry-collector-contrib:latest
    ports:
      - "4317:4317"
      - "4318:4318"
    volumes:
      - ./otel-config.yaml:/etc/otelcol/config.yaml

  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
```

---

## Key URLs

| Service | Default URL |
|---------|-------------|
| Grafana | <http://localhost:3000> |
| Jaeger UI | <http://localhost:16686> |
| Prometheus | <http://localhost:9090> |
| OTLP gRPC | <http://localhost:4317> |
| OTLP HTTP | <http://localhost:4318> |

---

## Emergency Procedures

### Disable Alerting

```python
# Set all rules to silenced
for rule in alert_rules:
    rule.silenced = True
```

### Reduce Sampling

```yaml
# In collector config
processors:
  probabilistic_sampler:
    sampling_percentage: 1  # Down from 100
```

### Increase Kafka Retention

```bash
kafka-configs.sh --alter --entity-type topics \
  --entity-name gds.metrics.production \
  --add-config retention.ms=604800000 \
  --bootstrap-server kafka:9092
```
