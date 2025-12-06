# Exercise 1: Set Up OpenTelemetry Collector

## Objective

Configure and run an OpenTelemetry Collector that receives telemetry via OTLP and exports to:

- Traces → Jaeger
- Metrics → Prometheus

## Prerequisites

- Docker and Docker Compose installed
- Basic understanding of YAML

---

## Step 1: Create Docker Compose File

Create `docker-compose.yaml`:

```yaml
version: '3.8'

services:
  # OpenTelemetry Collector
  otel-collector:
    image: otel/opentelemetry-collector-contrib:0.88.0
    command: ["--config=/etc/otelcol/config.yaml"]
    ports:
      - "4317:4317"   # OTLP gRPC
      - "4318:4318"   # OTLP HTTP
      - "8889:8889"   # Prometheus metrics
    volumes:
      - ./otel-config.yaml:/etc/otelcol/config.yaml

  # Jaeger for traces
  jaeger:
    image: jaegertracing/all-in-one:1.50
    ports:
      - "16686:16686"  # Jaeger UI
      - "14250:14250"  # gRPC (for collector)

  # Prometheus for metrics
  prometheus:
    image: prom/prometheus:v2.47.0
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yaml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
```

---

## Step 2: Create Collector Configuration

Create `otel-config.yaml`:

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
    timeout: 5s
    send_batch_size: 500

  resource:
    attributes:
      - key: deployment.environment
        action: upsert
        value: "development"

exporters:
  # Export traces to Jaeger
  jaeger:
    endpoint: jaeger:14250
    tls:
      insecure: true

  # Expose metrics for Prometheus scraping
  prometheus:
    endpoint: "0.0.0.0:8889"
    namespace: "otel"

  # Debug output
  logging:
    verbosity: detailed

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch, resource]
      exporters: [jaeger, logging]

    metrics:
      receivers: [otlp]
      processors: [batch, resource]
      exporters: [prometheus, logging]
```

---

## Step 3: Create Prometheus Configuration

Create `prometheus.yaml`:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'otel-collector'
    static_configs:
      - targets: ['otel-collector:8889']
```

---

## Step 4: Start the Stack

```bash
docker-compose up -d

# Check logs
docker-compose logs -f otel-collector
```

---

## Step 5: Verify Setup

### Check Collector Health

```bash
curl http://localhost:4318/v1/traces
# Should return 400 or 200 (means endpoint is alive)
```

### Send Test Span

```bash
curl -X POST http://localhost:4318/v1/traces \
  -H "Content-Type: application/json" \
  -d '{
    "resourceSpans": [{
      "resource": {
        "attributes": [
          {"key": "service.name", "value": {"stringValue": "test-service"}}
        ]
      },
      "scopeSpans": [{
        "spans": [{
          "traceId": "5B8EFFF798038103D269B633813FC60C",
          "spanId": "EEE19B7EC3C1B174",
          "name": "test-span",
          "kind": 1,
          "startTimeUnixNano": "1609459200000000000",
          "endTimeUnixNano": "1609459201000000000"
        }]
      }]
    }]
  }'
```

### View in Jaeger

Open <http://localhost:16686> and search for "test-service"

### Check Prometheus

Open <http://localhost:9090> and search for metrics starting with `otel_`

---

## Verification Checklist

- [ ] Docker Compose stack is running
- [ ] OTLP endpoint responds at <http://localhost:4318>
- [ ] Jaeger UI shows test trace
- [ ] Prometheus has metrics from collector

---

## Next Steps

1. Add more processors (filtering, sampling)
2. Configure additional exporters
3. Move to [Exercise 2: Instrument Python](02_instrument_python.md)
