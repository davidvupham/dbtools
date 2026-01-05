# Part 2: The Three Pillars of Observability

## What You'll Learn

In this part, you'll learn:

- Deep understanding of traces, metrics, and logs
- How each pillar contributes to observability
- How to correlate data across all three pillars
- When to use each type of telemetry

---

## Overview

The three pillars of observability are:

| Pillar | What It Captures | Primary Use Case |
|--------|------------------|------------------|
| **Traces** | Request flow through distributed systems | Understanding request paths and latency |
| **Metrics** | Numeric measurements over time | Monitoring system health and trends |
| **Logs** | Discrete events with context | Detailed debugging and audit trails |

```
┌─────────────────────────────────────────────────────────────────┐
│                    THE THREE PILLARS                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│    ┌───────────┐     ┌───────────┐     ┌───────────┐            │
│    │           │     │           │     │           │            │
│    │  TRACES   │     │  METRICS  │     │   LOGS    │            │
│    │           │     │           │     │           │            │
│    │  Shows    │     │  Shows    │     │  Shows    │            │
│    │  the path │     │  the      │     │  what     │            │
│    │           │     │  numbers  │     │  happened │            │
│    └─────┬─────┘     └─────┬─────┘     └─────┬─────┘            │
│          │                 │                 │                   │
│          └─────────────────┼─────────────────┘                   │
│                            │                                     │
│                      trace_id                                    │
│                   (Correlation)                                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

Each pillar provides a unique lens into your system. Together, they provide complete observability.

---

## Pillar 1: Traces (Distributed Tracing)

### What is a Trace?

A **trace** represents the complete journey of a request as it flows through a distributed system. It shows:

- Which services were involved
- How long each operation took
- The order of operations
- Where errors occurred

### Anatomy of a Trace

A trace consists of one or more **spans**. Each span represents a single operation:

```
Trace: user-login-request (trace_id: abc123)
│
├── Span: API Gateway (span_id: 001, parent: none)
│   ├── Start: 10:30:45.000
│   ├── End:   10:30:45.150
│   └── Duration: 150ms
│
├── Span: Auth Service (span_id: 002, parent: 001)
│   ├── Start: 10:30:45.010
│   ├── End:   10:30:45.090
│   └── Duration: 80ms
│
│   └── Span: Database Query (span_id: 003, parent: 002)
│       ├── Start: 10:30:45.020
│       ├── End:   10:30:45.050
│       └── Duration: 30ms
│
└── Span: Session Service (span_id: 004, parent: 001)
    ├── Start: 10:30:45.095
    ├── End:   10:30:45.140
    └── Duration: 45ms
```

### Span Attributes

Spans carry rich context through **attributes** (key-value pairs):

| Attribute Category | Examples |
|-------------------|----------|
| **Service** | `service.name`, `service.version` |
| **HTTP** | `http.method`, `http.status_code`, `http.url` |
| **Database** | `db.system`, `db.statement`, `db.instance` |
| **User** | `user.id`, `user.role` |
| **Custom** | `order.id`, `payment.method` |

### Trace Visualization

In a tracing UI (like Jaeger or Grafana Tempo), traces appear as waterfall diagrams:

```
Time →
├─────────────────────────────────────────────────────────┤
│                                                          │
│ API Gateway        ████████████████████████████████████  │ 150ms
│ Auth Service           ████████████████████              │  80ms
│   └─ DB Query              █████████                     │  30ms
│ Session Service                         █████████████    │  45ms
│                                                          │
├─────────────────────────────────────────────────────────┤
```

### When to Use Traces

| Scenario | Why Traces Help |
|----------|-----------------|
| Debugging slow requests | See where time is spent |
| Finding error sources | Pinpoint which service failed |
| Understanding dependencies | Visualize service interactions |
| Capacity planning | Identify bottlenecks |

### Trace Context Propagation

For traces to work across services, **trace context** must be propagated:

```
┌─────────────┐     traceparent header      ┌─────────────┐
│   Service   │ ─────────────────────────── │  Service    │
│      A      │    00-abc123-def456-01      │      B      │
└─────────────┘                              └─────────────┘
```

The **W3C Trace Context** standard uses two headers:

- `traceparent`: Contains trace_id, span_id, and flags
- `tracestate`: Vendor-specific information (optional)

**traceparent format**:

```
traceparent: 00-{trace_id}-{parent_span_id}-{flags}
             ││ │          │                │
             ││ │          │                └── 01 = sampled
             ││ │          └── Current span ID (16 hex chars)
             ││ └── Trace ID (32 hex chars)
             └└── Version (always 00)

Example:
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
```

---

## Pillar 2: Metrics

### What are Metrics?

**Metrics** are numeric measurements captured at regular intervals. They answer questions about system health and performance:

- How many requests per second?
- What's the average response time?
- How much memory is being used?
- What's the error rate?

### Types of Metrics

| Type | Description | Use Cases | Example |
|------|-------------|-----------|---------|
| **Counter** | Cumulative value that only increases | Request counts, error counts | `http_requests_total: 12,345` |
| **Gauge** | Point-in-time value that can go up or down | Memory usage, queue size | `memory_usage_bytes: 1,073,741,824` |
| **Histogram** | Distribution of values | Response time percentiles | `request_duration_p99: 250ms` |

### Counter Example

Counters track cumulative values:

```
Time:    10:00    10:01    10:02    10:03    10:04
         ┬        ┬        ┬        ┬        ┬
Value:   100      150      210      280      350
                   │        │        │        │
Rate:             +50      +60      +70      +70  (requests/min)
```

### Gauge Example

Gauges capture current state:

```
Memory Usage Over Time
│
│   ████
│  █████████                      ████████
│ ███████████                   ████████████
│██████████████               ████████████████
│                ██████████
└────────────────────────────────────────────── Time
 10:00     10:05     10:10     10:15     10:20
```

### Histogram Example

Histograms show distribution:

```
Response Time Distribution
│
│                  ████
│                ████████
│              ████████████
│            ████████████████
│          ████████████████████
│        ████████████████████████
│      ████████████████████████████
└──────────────────────────────────────────
   0ms   50ms  100ms  150ms  200ms  250ms+

Percentiles:
  p50:  75ms
  p90: 150ms
  p99: 220ms
```

### Metric Labels (Dimensions)

Metrics use **labels** to add dimensions:

```
http_requests_total{method="GET", status="200", endpoint="/api/users"}  = 1234
http_requests_total{method="POST", status="201", endpoint="/api/orders"} = 567
http_requests_total{method="GET", status="500", endpoint="/api/users"}  = 12
```

This enables powerful queries:

- Total requests: `sum(http_requests_total)`
- Error rate: `sum(http_requests_total{status=~"5.."}) / sum(http_requests_total)`
- Requests by endpoint: `http_requests_total{endpoint="/api/users"}`

### When to Use Metrics

| Scenario | Why Metrics Help |
|----------|------------------|
| Alerting | Trigger alerts when thresholds exceeded |
| Dashboards | Visualize system health at a glance |
| Trend analysis | Understand patterns over time |
| Capacity planning | Predict future resource needs |
| SLO monitoring | Track service level objectives |

### Common Metrics to Collect

**Application Metrics**:

| Metric | Type | Description |
|--------|------|-------------|
| `http_requests_total` | Counter | Total HTTP requests |
| `http_request_duration_seconds` | Histogram | Request latency |
| `http_requests_in_progress` | Gauge | Active requests |
| `errors_total` | Counter | Total errors |

**Infrastructure Metrics**:

| Metric | Type | Description |
|--------|------|-------------|
| `cpu_usage_percent` | Gauge | CPU utilization |
| `memory_usage_bytes` | Gauge | Memory usage |
| `disk_io_bytes` | Counter | Disk I/O |
| `network_bytes_total` | Counter | Network traffic |

**Database Metrics**:

| Metric | Type | Description |
|--------|------|-------------|
| `db_connections_active` | Gauge | Active connections |
| `db_query_duration_seconds` | Histogram | Query latency |
| `db_transactions_total` | Counter | Total transactions |

---

## Pillar 3: Logs

### What are Logs?

**Logs** are timestamped records of discrete events. They capture:

- What happened
- When it happened
- Context about the event
- Error details and stack traces

### Structured vs Unstructured Logs

**Unstructured logs** are plain text:

```
2025-01-15 10:30:45 ERROR - Database connection failed: timeout after 30s
```

**Structured logs** are machine-parseable (JSON):

```json
{
  "timestamp": "2025-01-15T10:30:45.123Z",
  "level": "ERROR",
  "message": "Database connection failed",
  "service": "user-service",
  "db.system": "postgresql",
  "db.instance": "prod-db-01",
  "error.type": "ConnectionTimeout",
  "error.message": "timeout after 30s",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7"
}
```

> [!TIP]
> **Always use structured logging.** Structured logs are:
>
> - Easier to search and filter
> - Parseable by log aggregation systems
> - Correlatable with traces and metrics

### Log Levels

Standard log levels from most to least verbose:

| Level | When to Use | Example |
|-------|-------------|---------|
| **DEBUG** | Detailed diagnostic info | Variable values, loop iterations |
| **INFO** | Normal operations | "Request processed", "User logged in" |
| **WARNING** | Unexpected but handled | "Retry attempt 2/3", "Deprecated API" |
| **ERROR** | Failures requiring attention | "Database query failed" |
| **CRITICAL/FATAL** | System-threatening failures | "Out of memory", "Config invalid" |

### Log Correlation with Trace Context

The key to correlating logs with traces is including **trace_id** and **span_id**:

```json
{
  "timestamp": "2025-01-15T10:30:45.123Z",
  "level": "ERROR",
  "message": "Payment processing failed",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7",
  "order.id": "ORD-12345",
  "error.type": "PaymentDeclined"
}
```

This enables:

- Clicking from a log entry → viewing the full trace
- Filtering logs by trace_id to see all logs for a request
- Jumping from a trace span → seeing related logs

### When to Use Logs

| Scenario | Why Logs Help |
|----------|---------------|
| Debugging errors | Stack traces and error details |
| Audit trails | Record of security-relevant events |
| Business events | User actions, transactions |
| Compliance | Regulatory requirements |

### Log Best Practices

1. **Use structured format (JSON)**

   ```json
   {"timestamp": "...", "level": "...", "message": "...", "context": {...}}
   ```

2. **Include trace context**

   ```json
   {"trace_id": "abc123", "span_id": "def456", ...}
   ```

3. **Add meaningful context**

   ```json
   {"user_id": "12345", "order_id": "ORD-567", "action": "checkout"}
   ```

4. **Don't log sensitive data**
   - ❌ `{"password": "secret123"}`
   - ✅ `{"password": "[REDACTED]"}`

5. **Use appropriate log levels**
   - Don't use ERROR for expected conditions
   - Don't use DEBUG in production (by default)

---

## How the Three Pillars Work Together

### The Power of Correlation

Each pillar provides unique value, but the real power comes from **correlation**:

```
┌─────────────────────────────────────────────────────────────────┐
│                     CORRELATED VIEW                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  METRICS tell you WHAT happened                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Error Rate                                               │    │
│  │     ▲                                                    │    │
│  │   2%│                    ████                            │    │
│  │   1%│                 ███    ███                         │    │
│  │   0%│────────────────────────────────────                │    │
│  │     └─────────────────────────────────── Time            │    │
│  │              10:30 AM  ← Spike here!                     │    │
│  └─────────────────────────────────────────────────────────┘    │
│                            │                                     │
│                            ▼                                     │
│  TRACES tell you WHERE it happened                               │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Trace: abc123 (10:30:15, ERROR)                         │    │
│  │ ├── API Gateway        ████████ 50ms                    │    │
│  │ ├── Order Service           ████████ 45ms               │    │
│  │ └── Payment Service              █████ ← FAILED         │    │
│  └─────────────────────────────────────────────────────────┘    │
│                            │                                     │
│                            ▼                                     │
│  LOGS tell you WHY it happened                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 10:30:15.234 ERROR Payment Service                      │    │
│  │ trace_id: abc123                                        │    │
│  │ message: "Card declined: insufficient funds"            │    │
│  │ card.last4: "4242"                                      │    │
│  │ amount: 150.00                                          │    │
│  │ customer.id: "cust_987"                                 │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Debugging Workflow

A typical debugging workflow using all three pillars:

1. **Start with Metrics**: Alert fires for high error rate
2. **Identify Pattern**: Dashboard shows errors increasing at 10:30 AM
3. **Find Affected Traces**: Filter traces by time range and error status
4. **Examine Trace**: See the payment service is failing
5. **Read Logs**: Find "Card declined" error with full context
6. **Root Cause**: Understand the issue and fix it

### Correlation in Practice

**In Grafana with all three pillars**:

```
┌─────────────────────────────────────────────────────────────────┐
│ GRAFANA DASHBOARD                                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ [Metrics Panel]                                                  │
│ Error rate: 2.5% ↑                                              │
│ Click point → Opens trace search                                │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ [Traces Panel]                                                   │
│ Trace abc123: API → Order → Payment (ERROR)                     │
│ Click span → Opens logs filtered by trace_id                    │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ [Logs Panel]                                                     │
│ {trace_id="abc123"} → Shows all logs for this request           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Choosing the Right Pillar

| Question | Best Pillar | Why |
|----------|-------------|-----|
| "Is the system healthy?" | Metrics | Quick overview, trends |
| "Why is this request slow?" | Traces | Shows time spent in each service |
| "What error occurred?" | Logs | Detailed error messages |
| "How many errors today?" | Metrics | Aggregated counts |
| "Which service caused the error?" | Traces | Shows request path |
| "What was the input that failed?" | Logs | Captures context |
| "What's the p99 latency?" | Metrics | Histogram distribution |
| "What happened at 10:30 AM?" | Traces + Logs | Request details + context |

---

## Summary

| Pillar | Captures | Best For | Key Identifier |
|--------|----------|----------|----------------|
| **Traces** | Request flow across services | Performance debugging, dependency analysis | trace_id, span_id |
| **Metrics** | Numeric measurements over time | Health monitoring, alerting, trends | Metric name + labels |
| **Logs** | Discrete events with context | Detailed debugging, audit trails | trace_id + timestamp |

### Key Takeaways

1. **All three pillars are essential**—each provides unique insights
2. **Correlation is critical**—use trace_id to link data across pillars
3. **Use structured logging**—enables machine parsing and correlation
4. **Include context**—rich attributes make debugging easier
5. **Choose the right pillar for the question**—metrics for "what", traces for "where", logs for "why"

---

## What's Next?

Now that you understand the three pillars, Part 3 will explore how to build a **data pipeline architecture** to collect, process, and store telemetry at scale.

[Continue to Part 3: Data Pipeline Architecture →](03_DATA_PIPELINE_ARCHITECTURE.md)
