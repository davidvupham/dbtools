# Part 4: OpenTelemetry Deep Dive

## What You'll Learn

In this part, you'll learn:

- What OpenTelemetry is and why it's important
- Core components: SDK, API, Collector, and OTLP
- Deployment patterns and architecture
- Context propagation across services
- Collector configuration and processors
- Choosing and configuring backends

---

## What is OpenTelemetry?

**OpenTelemetry (OTel)** is an open-source, vendor-neutral observability framework that provides a unified approach to collecting, processing, and exporting telemetry data.

### The Problem OpenTelemetry Solves

Before OpenTelemetry:

```
┌─────────────────────────────────────────────────────────────────┐
│              BEFORE OPENTELEMETRY                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌───────────┐    ┌──────────────────────────────────────────┐  │
│  │Application│───►│ Vendor A Agent (proprietary)             │  │
│  └───────────┘    └──────────────────────────────────────────┘  │
│                   ┌──────────────────────────────────────────┐  │
│              ───►│ Library X for traces                      │  │
│                   └──────────────────────────────────────────┘  │
│                   ┌──────────────────────────────────────────┐  │
│              ───►│ Library Y for metrics                     │  │
│                   └──────────────────────────────────────────┘  │
│                   ┌──────────────────────────────────────────┐  │
│              ───►│ Library Z for logs                        │  │
│                   └──────────────────────────────────────────┘  │
│                                                                  │
│  Problems:                                                       │
│  • Vendor lock-in                                               │
│  • Multiple agents and libraries                                │
│  • Inconsistent APIs                                            │
│  • No correlation between signals                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

After OpenTelemetry:

```
┌─────────────────────────────────────────────────────────────────┐
│              WITH OPENTELEMETRY                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌───────────┐    ┌──────────────────────────────────────────┐  │
│  │Application│───►│ OpenTelemetry SDK                        │  │
│  └───────────┘    │ (Traces + Metrics + Logs unified)        │  │
│                   └─────────────────┬────────────────────────┘  │
│                                     │ OTLP                      │
│                   ┌─────────────────▼────────────────────────┐  │
│                   │     OpenTelemetry Collector              │  │
│                   └─────────────────┬────────────────────────┘  │
│                                     │                           │
│           ┌─────────────────────────┼─────────────────────────┐ │
│           │                         │                         │ │
│           ▼                         ▼                         ▼ │
│     ┌──────────┐              ┌──────────┐              ┌─────┐ │
│     │ Jaeger   │              │Prometheus│              │Loki │ │
│     │ Tempo    │              │ Datadog  │              │ ELK │ │
│     │ Zipkin   │              │ New Relic│              │     │ │
│     └──────────┘              └──────────┘              └─────┘ │
│                                                                  │
│  Benefits:                                                       │
│  • Vendor neutral - switch backends easily                      │
│  • Single SDK for all signals                                   │
│  • Automatic correlation                                        │
│  • Industry standard                                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Key Principle

> **Instrument once, export anywhere.**

OpenTelemetry decouples telemetry generation from telemetry backends.

---

## Core Components

### 1. OpenTelemetry API

The **API** defines how to instrument code:

- Create spans for tracing
- Record metrics
- Emit logs with context

The API is intentionally separate from implementation, allowing libraries to instrument themselves without forcing specific SDK dependencies.

### 2. OpenTelemetry SDK

The **SDK** is the implementation of the API:

- Manages span lifecycle
- Handles sampling decisions
- Batches and exports telemetry

### 3. OTLP (OpenTelemetry Protocol)

**OTLP** is the standardized protocol for transmitting telemetry:

| Protocol | Port | Use Case |
|----------|------|----------|
| gRPC | 4317 | High performance, binary |
| HTTP/Protobuf | 4318 | Firewall-friendly |

Example endpoint: `http://collector:4318/v1/traces`

### 4. OpenTelemetry Collector

The **Collector** is a vendor-agnostic telemetry processor:

```
┌─────────────────────────────────────────────────────────────────┐
│                   OPENTELEMETRY COLLECTOR                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐     │
│  │   RECEIVERS    │  │   PROCESSORS   │  │   EXPORTERS    │     │
│  │                │  │                │  │                │     │
│  │ • OTLP         │  │ • Batch        │  │ • OTLP        │     │
│  │ • Jaeger       │──│ • Filter       │──│ • Prometheus  │     │
│  │ • Prometheus   │  │ • Transform    │  │ • Jaeger      │     │
│  │ • Kafka        │  │ • Sampling     │  │ • Kafka       │     │
│  │ • Filelog      │  │ • Attributes   │  │ • Loki        │     │
│  │                │  │                │  │                │     │
│  └────────────────┘  └────────────────┘  └────────────────┘     │
│                                                                  │
│  Pipelines connect receivers → processors → exporters           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Deployment Patterns

### Pattern 1: Agent (Sidecar/DaemonSet)

Collector runs alongside each application:

```
┌─────────────────────────────────────────────────────────────────┐
│                      AGENT PATTERN                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Host 1                           Host 2                         │
│  ┌─────────────────────────┐     ┌─────────────────────────┐    │
│  │ ┌─────┐  ┌───────────┐  │     │ ┌─────┐  ┌───────────┐  │    │
│  │ │ App │──│ Collector │  │     │ │ App │──│ Collector │  │    │
│  │ └─────┘  │ (Agent)   │  │     │ └─────┘  │ (Agent)   │  │    │
│  │          └─────┬─────┘  │     │          └─────┬─────┘  │    │
│  └────────────────┼────────┘     └────────────────┼────────┘    │
│                   │                               │              │
│                   └───────────────┬───────────────┘              │
│                                   │                              │
│                                   ▼                              │
│                          ┌───────────────┐                      │
│                          │   Backends    │                      │
│                          └───────────────┘                      │
│                                                                  │
│  Benefits: Low latency, offline buffering, simple app config    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Best for**: Kubernetes deployments, microservices

### Pattern 2: Gateway (Centralized)

Single centralized collector:

```
┌─────────────────────────────────────────────────────────────────┐
│                     GATEWAY PATTERN                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌───────┐  ┌───────┐  ┌───────┐                                │
│  │ App 1 │  │ App 2 │  │ App 3 │                                │
│  └───┬───┘  └───┬───┘  └───┬───┘                                │
│      │          │          │                                     │
│      └──────────┼──────────┘                                     │
│                 │ OTLP                                           │
│                 ▼                                                │
│      ┌─────────────────────┐                                    │
│      │ Collector (Gateway) │                                    │
│      │  • Central config   │                                    │
│      │  • Processing       │                                    │
│      │  • Routing          │                                    │
│      └──────────┬──────────┘                                    │
│                 │                                                │
│                 ▼                                                │
│            Backends                                              │
│                                                                  │
│  Benefits: Simpler deployment, centralized management           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Best for**: Smaller deployments, getting started

### Pattern 3: Hybrid (Agent + Gateway)

Combines both patterns for maximum flexibility:

```
┌─────────────────────────────────────────────────────────────────┐
│                     HYBRID PATTERN                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌───────────────────────┐  ┌───────────────────────┐           │
│  │ ┌─────┐  ┌─────────┐  │  │ ┌─────┐  ┌─────────┐  │           │
│  │ │ App │──│ Agent   │  │  │ │ App │──│ Agent   │  │           │
│  │ └─────┘  └────┬────┘  │  │ └─────┘  └────┬────┘  │           │
│  └───────────────┼───────┘  └───────────────┼───────┘           │
│                  │                          │                    │
│                  └──────────┬───────────────┘                    │
│                             │                                    │
│                  ┌──────────▼──────────┐                        │
│                  │  Collector Gateway  │                        │
│                  │  • Aggregation      │                        │
│                  │  • Sampling         │                        │
│                  │  • Routing          │                        │
│                  └──────────┬──────────┘                        │
│                             │                                    │
│              ┌──────────────┼──────────────┐                    │
│              │              │              │                    │
│              ▼              ▼              ▼                    │
│          Jaeger       Prometheus        Loki                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Best for**: Production deployments at scale

---

## Context Propagation

### W3C Trace Context

The **W3C Trace Context** standard ensures trace correlation across services:

```
HTTP Request Headers:
┌─────────────────────────────────────────────────────────────────┐
│ traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa-01   │
│              ││ │                                  │        │    │
│              ││ │ trace_id (32 hex)               span_id   │    │
│              ││                                    (16 hex) │    │
│              │└─ version (00)                               │    │
│              │                                      flags ──┘    │
│              │                                      (01=sampled) │
└─────────────────────────────────────────────────────────────────┘
```

### How Context Flows

```
┌─────────────┐     traceparent      ┌─────────────┐     traceparent      ┌─────────────┐
│  Service A  │──────────────────────│  Service B  │──────────────────────│  Service C  │
│             │  trace_id: abc123    │             │  trace_id: abc123    │             │
│  span: s1   │  span_id:  s1        │  span: s2   │  span_id:  s2        │  span: s3   │
└─────────────┘                      └─────────────┘                      └─────────────┘
     │                                    │                                    │
     │                                    │                                    │
     └────────────────────────────────────┴────────────────────────────────────┘
                              All share trace_id: abc123
                              Form a tree via parent_span_id
```

### Context Propagation in Code

**Python (auto-instrumented)**:

```python
# Automatic - no code needed for HTTP calls!
# OpenTelemetry instrumentations handle it
```

**Python (manual)**:

```python
from opentelemetry import trace
from opentelemetry.propagate import inject, extract

# Inject (outgoing request)
headers = {}
inject(headers)  # Adds traceparent header

# Extract (incoming request)
ctx = extract(request.headers)
with tracer.start_as_current_span("operation", context=ctx):
    process_request()
```

**PowerShell**:

```powershell
# Generate trace context
$traceId = [Guid]::NewGuid().ToString("N")
$spanId = [Guid]::NewGuid().ToString("N").Substring(0, 16)

# Create traceparent header
$traceparent = "00-$traceId-$spanId-01"

# Include in HTTP calls
$headers = @{ "traceparent" = $traceparent }
Invoke-RestMethod -Uri $uri -Headers $headers
```

---

## Collector Configuration

### Basic Configuration Structure

```yaml
# otel-collector-config.yaml

receivers:
  # How data comes in
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  # How data is transformed
  batch:
    timeout: 10s
    send_batch_size: 1000

exporters:
  # Where data goes out
  otlp/jaeger:
    endpoint: jaeger:4317
    tls:
      insecure: true

service:
  pipelines:
    # Connect receivers → processors → exporters
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlp/jaeger]
```

### Common Processors

#### Batch Processor (Performance)

```yaml
processors:
  batch:
    timeout: 10s           # Max wait before sending
    send_batch_size: 1000  # Send when batch reaches this size
    send_batch_max_size: 2000  # Never exceed this size
```

#### Resource Processor (Enrichment)

```yaml
processors:
  resource:
    attributes:
      - key: deployment.environment
        action: upsert
        value: production
      - key: service.version
        action: upsert
        value: "1.2.3"
```

#### Attributes Processor (Modification)

```yaml
processors:
  attributes:
    actions:
      # Remove sensitive data
      - key: password
        action: delete
      - key: api_key
        action: delete
      # Hash for anonymization
      - key: user.email
        action: hash
```

#### Filter Processor (Reduction)

```yaml
processors:
  filter:
    traces:
      span:
        # Drop health check spans
        - 'attributes["http.route"] == "/health"'
        - 'attributes["http.route"] == "/metrics"'
```

#### Tail Sampling Processor (Smart Sampling)

```yaml
processors:
  tail_sampling:
    decision_wait: 10s
    policies:
      # Always keep errors
      - name: errors
        type: status_code
        status_code:
          status_codes: [ERROR]
      # Always keep slow requests
      - name: slow-requests
        type: latency
        latency:
          threshold_ms: 1000
      # Sample 10% of everything else
      - name: probabilistic
        type: probabilistic
        probabilistic:
          sampling_percentage: 10
```

### Complete Example Configuration

```yaml
# otel-collector-config.yaml

receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

  # Read JSON logs from files
  filelog:
    include: [/var/log/apps/*.json]
    operators:
      - type: json_parser

processors:
  # Batch for efficiency
  batch:
    timeout: 10s
    send_batch_size: 1000

  # Add common attributes
  resource:
    attributes:
      - key: deployment.environment
        action: upsert
        value: production

  # Remove sensitive data
  attributes/redact:
    actions:
      - key: password
        action: delete
      - key: db.password
        action: delete

  # Smart sampling (traces only)
  tail_sampling:
    decision_wait: 10s
    policies:
      - name: errors
        type: status_code
        status_code:
          status_codes: [ERROR]
      - name: probabilistic
        type: probabilistic
        probabilistic:
          sampling_percentage: 20

exporters:
  # Traces to Jaeger/Tempo
  otlp/traces:
    endpoint: tempo:4317
    tls:
      insecure: true

  # Metrics to Prometheus
  prometheus:
    endpoint: "0.0.0.0:8889"
    namespace: "otel"

  # Logs to Loki
  loki:
    endpoint: "http://loki:3100/loki/api/v1/push"

  # Optional: Also send to Kafka
  kafka:
    brokers: ["kafka:9092"]
    topic: telemetry-all
    encoding: otlp_proto

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch, resource, attributes/redact, tail_sampling]
      exporters: [otlp/traces, kafka]

    metrics:
      receivers: [otlp]
      processors: [batch, resource]
      exporters: [prometheus, kafka]

    logs:
      receivers: [otlp, filelog]
      processors: [batch, resource, attributes/redact]
      exporters: [loki, kafka]
```

---

## Backend Options

### Open Source Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                   OPEN SOURCE STACK                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Traces:    Jaeger or Grafana Tempo                             │
│  Metrics:   Prometheus (+ Thanos/Cortex for scale)              │
│  Logs:      Grafana Loki                                        │
│  Viz:       Grafana                                              │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                      GRAFANA                              │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐          │   │
│  │  │   Traces   │  │  Metrics   │  │    Logs    │          │   │
│  │  │  (Tempo)   │  │(Prometheus)│  │   (Loki)   │          │   │
│  │  └────────────┘  └────────────┘  └────────────┘          │   │
│  │                                                           │   │
│  │  Unified dashboards with correlation                      │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Backend Comparison

| Backend | Signal | Strengths | Best For |
|---------|--------|-----------|----------|
| **Jaeger** | Traces | Mature, well-documented | Established teams |
| **Tempo** | Traces | Simple, S3-backend, Grafana native | Grafana users |
| **Prometheus** | Metrics | Industry standard, PromQL | All teams |
| **Thanos** | Metrics | Global view, long-term storage | Large scale |
| **Loki** | Logs | Label-based, cost-effective | Grafana users |
| **Elasticsearch** | Logs | Full-text search, powerful | Search-heavy use |

### Commercial Options

| Vendor | Strengths |
|--------|-----------|
| **Grafana Cloud** | Managed Prometheus/Loki/Tempo |
| **Datadog** | Full-featured, ML insights |
| **New Relic** | AI-powered, easy setup |
| **Honeycomb** | High cardinality, exploration |
| **Dynatrace** | Auto-discovery, Davis AI |

---

## Semantic Conventions

OpenTelemetry defines **semantic conventions** for consistent naming:

### Common Attributes

| Attribute | Description | Example |
|-----------|-------------|---------|
| `service.name` | Logical service name | `user-service` |
| `service.version` | Service version | `1.2.3` |
| `deployment.environment` | Deployment environment | `production` |

### HTTP Attributes

| Attribute | Description | Example |
|-----------|-------------|---------|
| `http.method` | HTTP method | `GET`, `POST` |
| `http.status_code` | Response status | `200`, `500` |
| `http.url` | Full URL | `https://api.example.com/users` |
| `http.route` | Route template | `/users/{id}` |

### Database Attributes

| Attribute | Description | Example |
|-----------|-------------|---------|
| `db.system` | Database type | `postgresql`, `mongodb` |
| `db.name` | Database name | `users` |
| `db.operation` | Operation type | `SELECT`, `INSERT` |
| `db.statement` | Query (sanitized) | `SELECT * FROM users WHERE id = ?` |

> [!TIP]
> Always follow semantic conventions for consistent querying and correlation across services.

---

## Summary

| Component | Purpose |
|-----------|---------|
| **API** | Define instrumentation contract |
| **SDK** | Implement telemetry collection |
| **OTLP** | Standardized transport protocol |
| **Collector** | Receive, process, export telemetry |

### Key Takeaways

1. **OpenTelemetry unifies observability** - single framework for all signals
2. **Vendor neutral** - switch backends without re-instrumenting
3. **Context propagation is automatic** - with proper instrumentation
4. **Collector is powerful** - use processors for sampling, filtering, enrichment
5. **Follow semantic conventions** - enables cross-service querying

---

## What's Next?

Part 5 will cover **PowerShell Logging** patterns for structured logging and observability integration.

[Continue to Part 5: PowerShell Logging →](05_POWERSHELL_LOGGING.md)
