# Part 9: Best Practices

## What You'll Learn

In this part, you'll learn:

- Design patterns for observability systems
- SOLID principles applied to telemetry
- Performance optimization strategies
- Security considerations
- Common anti-patterns to avoid

---

## Design Patterns

### 1. Abstract Factory Pattern

Use Abstract Factory to support multiple telemetry backends:

```python
from abc import ABC, abstractmethod

# Abstract products
class MetricsBackend(ABC):
    @abstractmethod
    def record_counter(self, name: str, value: int, labels: dict): pass

    @abstractmethod
    def record_histogram(self, name: str, value: float, labels: dict): pass

class TracingBackend(ABC):
    @abstractmethod
    def create_span(self, name: str, attributes: dict): pass

# Abstract factory
class TelemetryFactory(ABC):
    @abstractmethod
    def create_metrics_backend(self) -> MetricsBackend: pass

    @abstractmethod
    def create_tracing_backend(self) -> TracingBackend: pass

# Concrete factory for OpenTelemetry
class OpenTelemetryFactory(TelemetryFactory):
    def create_metrics_backend(self) -> MetricsBackend:
        return OTelMetricsBackend()

    def create_tracing_backend(self) -> TracingBackend:
        return OTelTracingBackend()

# Concrete factory for NoOp (testing)
class NoOpTelemetryFactory(TelemetryFactory):
    def create_metrics_backend(self) -> MetricsBackend:
        return NoOpMetricsBackend()

    def create_tracing_backend(self) -> TracingBackend:
        return NoOpTracingBackend()

# Usage
def create_telemetry(env: str) -> TelemetryFactory:
    if env == "production":
        return OpenTelemetryFactory()
    else:
        return NoOpTelemetryFactory()
```

### 2. Strategy Pattern

Use Strategy for different notification channels:

```python
from abc import ABC, abstractmethod

class NotificationStrategy(ABC):
    @abstractmethod
    async def send(self, alert: Alert) -> bool: pass

class EmailNotification(NotificationStrategy):
    async def send(self, alert: Alert) -> bool:
        # Send email
        return await self.smtp_client.send(
            to=alert.owner_email,
            subject=f"Alert: {alert.rule.name}",
            body=self.format_email(alert)
        )

class SlackNotification(NotificationStrategy):
    async def send(self, alert: Alert) -> bool:
        # Send Slack message
        return await self.slack_client.post_message(
            channel=alert.slack_channel,
            text=self.format_slack(alert)
        )

class PagerDutyNotification(NotificationStrategy):
    async def send(self, alert: Alert) -> bool:
        # Create PagerDuty incident
        return await self.pd_client.create_incident(
            service_key=alert.pd_service_key,
            description=alert.rule.name,
            details=self.format_pagerduty(alert)
        )

# Context uses strategy
class AlertNotifier:
    def __init__(self, strategies: List[NotificationStrategy]):
        self.strategies = strategies

    async def notify(self, alert: Alert) -> bool:
        results = await asyncio.gather(
            *[s.send(alert) for s in self.strategies]
        )
        return all(results)
```

### 3. Observer Pattern

Use Observer for metric collection:

```python
from abc import ABC, abstractmethod
from typing import List

class MetricObserver(ABC):
    @abstractmethod
    def on_metric(self, metric: dict): pass

class AlertEvaluatorObserver(MetricObserver):
    def on_metric(self, metric: dict):
        alert = self.evaluate(metric)
        if alert:
            self.notify(alert)

class DashboardObserver(MetricObserver):
    def on_metric(self, metric: dict):
        self.update_dashboard(metric)

class ArchiveObserver(MetricObserver):
    def on_metric(self, metric: dict):
        self.write_to_s3(metric)

class MetricPublisher:
    def __init__(self):
        self._observers: List[MetricObserver] = []

    def subscribe(self, observer: MetricObserver):
        self._observers.append(observer)

    def unsubscribe(self, observer: MetricObserver):
        self._observers.remove(observer)

    def publish(self, metric: dict):
        for observer in self._observers:
            observer.on_metric(metric)

# Usage
publisher = MetricPublisher()
publisher.subscribe(AlertEvaluatorObserver())
publisher.subscribe(DashboardObserver())
publisher.subscribe(ArchiveObserver())

publisher.publish(metric)  # All observers notified
```

### 4. Builder Pattern

Use Builder for complex configurations:

```python
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class CollectorConfig:
    receivers: List[str] = field(default_factory=list)
    processors: List[str] = field(default_factory=list)
    exporters: List[str] = field(default_factory=list)
    batch_size: int = 1000
    flush_interval: int = 10
    sampling_rate: float = 1.0

class CollectorConfigBuilder:
    """Build collector configuration fluently."""

    def __init__(self):
        self._config = CollectorConfig()

    def with_receiver(self, receiver: str) -> 'CollectorConfigBuilder':
        self._config.receivers.append(receiver)
        return self

    def with_processor(self, processor: str) -> 'CollectorConfigBuilder':
        self._config.processors.append(processor)
        return self

    def with_exporter(self, exporter: str) -> 'CollectorConfigBuilder':
        self._config.exporters.append(exporter)
        return self

    def with_batching(self, size: int, interval: int) -> 'CollectorConfigBuilder':
        self._config.batch_size = size
        self._config.flush_interval = interval
        return self

    def with_sampling(self, rate: float) -> 'CollectorConfigBuilder':
        self._config.sampling_rate = rate
        return self

    def build(self) -> CollectorConfig:
        return self._config

# Usage
config = (
    CollectorConfigBuilder()
    .with_receiver("otlp")
    .with_processor("batch")
    .with_processor("attributes")
    .with_exporter("prometheus")
    .with_exporter("jaeger")
    .with_batching(size=2000, interval=5)
    .with_sampling(rate=0.1)
    .build()
)
```

---

## SOLID Principles Applied

### Single Responsibility Principle (SRP)

Each class should have one reason to change:

```python
# ❌ BAD: One class does everything
class MonitoringService:
    def collect_metrics(self): pass
    def evaluate_alerts(self): pass
    def send_notifications(self): pass
    def archive_data(self): pass

# ✅ GOOD: Separate responsibilities
class MetricCollector:
    def collect(self) -> List[Metric]: pass

class AlertEvaluator:
    def evaluate(self, metrics: List[Metric]) -> List[Alert]: pass

class AlertNotifier:
    def notify(self, alert: Alert): pass

class DataArchiver:
    def archive(self, metrics: List[Metric]): pass
```

### Open/Closed Principle (OCP)

Open for extension, closed for modification:

```python
# ✅ GOOD: Easy to add new collectors without changing existing code
class MetricCollector(ABC):
    @abstractmethod
    async def collect(self) -> List[Metric]: pass

class PostgreSQLCollector(MetricCollector):
    async def collect(self) -> List[Metric]:
        # PostgreSQL-specific collection
        pass

class MongoDBCollector(MetricCollector):
    async def collect(self) -> List[Metric]:
        # MongoDB-specific collection
        pass

# Adding new database: just add new class
class SnowflakeCollector(MetricCollector):
    async def collect(self) -> List[Metric]:
        # Snowflake-specific collection
        pass
```

### Liskov Substitution Principle (LSP)

Subtypes must be substitutable for their base types:

```python
# ✅ GOOD: All collectors are interchangeable
def run_collection(collectors: List[MetricCollector]):
    for collector in collectors:
        metrics = collector.collect()  # Works for any collector
        process(metrics)

# Any collector subtype can be used
run_collection([
    PostgreSQLCollector(config1),
    MongoDBCollector(config2),
    SnowflakeCollector(config3),
])
```

### Interface Segregation Principle (ISP)

Clients shouldn't depend on interfaces they don't use:

```python
# ❌ BAD: Fat interface
class TelemetryClient(ABC):
    @abstractmethod
    def send_trace(self, trace): pass

    @abstractmethod
    def send_metric(self, metric): pass

    @abstractmethod
    def send_log(self, log): pass

# ✅ GOOD: Segregated interfaces
class TraceClient(ABC):
    @abstractmethod
    def send_trace(self, trace): pass

class MetricsClient(ABC):
    @abstractmethod
    def send_metric(self, metric): pass

class LogClient(ABC):
    @abstractmethod
    def send_log(self, log): pass

# Classes can implement only what they need
class PrometheusClient(MetricsClient):
    def send_metric(self, metric):
        # Only handles metrics
        pass
```

### Dependency Inversion Principle (DIP)

Depend on abstractions, not concretions:

```python
# ❌ BAD: Direct dependency on concrete class
class AlertService:
    def __init__(self):
        self.notifier = SlackNotifier()  # Hardcoded dependency

# ✅ GOOD: Depend on abstraction
class AlertService:
    def __init__(self, notifier: NotificationStrategy):  # Injected
        self.notifier = notifier

# Inject any implementation
alert_service = AlertService(SlackNotification())
alert_service = AlertService(EmailNotification())
```

---

## Performance Optimization

### 1. Batching

Reduce overhead by batching operations:

```python
class BatchedMetricsSender:
    """Send metrics in batches for efficiency."""

    def __init__(self, batch_size: int = 100, flush_interval: float = 5.0):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.buffer = []
        self.last_flush = time.time()

    def add(self, metric: dict):
        self.buffer.append(metric)

        if len(self.buffer) >= self.batch_size:
            self.flush()
        elif time.time() - self.last_flush >= self.flush_interval:
            self.flush()

    def flush(self):
        if self.buffer:
            self._send_batch(self.buffer)
            self.buffer = []
            self.last_flush = time.time()

    def _send_batch(self, batch: List[dict]):
        # Send batch in single request
        pass
```

### 2. Sampling

Reduce volume while maintaining visibility:

```python
class AdaptiveSampler:
    """Sample based on importance and volume."""

    def __init__(self, base_rate: float = 0.1):
        self.base_rate = base_rate

    def should_sample(self, item: dict) -> bool:
        # Always sample errors
        if item.get('level') == 'error':
            return True

        # Always sample slow requests
        if item.get('duration_ms', 0) > 1000:
            return True

        # Otherwise use base rate
        return random.random() < self.base_rate
```

### 3. Async I/O

Use async for I/O-bound operations:

```python
import asyncio
import aiohttp

class AsyncMetricCollector:
    """Collect metrics from multiple sources concurrently."""

    async def collect_all(self, instances: List[str]) -> List[Metric]:
        async with aiohttp.ClientSession() as session:
            tasks = [
                self._collect_instance(session, instance)
                for instance in instances
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            metrics = []
            for result in results:
                if isinstance(result, list):
                    metrics.extend(result)
                elif isinstance(result, Exception):
                    self.logger.error(f"Collection failed: {result}")

            return metrics
```

### 4. Connection Pooling

Reuse connections:

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    "postgresql://user:pass@localhost/db",
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Check connection before use
)
```

### 5. Compression

Reduce network bandwidth:

```python
# Kafka producer with compression
producer_config = {
    'compression.type': 'lz4',  # Fast compression
    # Or 'gzip' for better ratio
}

# OTLP with compression
exporter = OTLPSpanExporter(
    endpoint='http://collector:4317',
    compression=True,  # Enable compression
)
```

---

## Security Considerations

### 1. Data Redaction

Never log sensitive data:

```python
SENSITIVE_KEYS = {'password', 'token', 'api_key', 'secret', 'credential'}

def redact_sensitive(data: dict) -> dict:
    """Redact sensitive values from data."""
    redacted = {}

    for key, value in data.items():
        key_lower = key.lower()

        if any(sensitive in key_lower for sensitive in SENSITIVE_KEYS):
            redacted[key] = f"[REDACTED length={len(str(value))}]"
        elif isinstance(value, dict):
            redacted[key] = redact_sensitive(value)
        else:
            redacted[key] = value

    return redacted
```

### 2. Access Control

Limit access to telemetry data:

```python
class TelemetryAccess:
    """Control access to telemetry queries."""

    def __init__(self, user_roles: dict):
        self.permissions = {
            'admin': ['read:all', 'write:all'],
            'developer': ['read:own_service', 'read:errors'],
            'viewer': ['read:dashboards'],
        }

    def can_query(self, user: str, query: dict) -> bool:
        role = self.user_roles.get(user, 'viewer')
        permissions = self.permissions.get(role, [])

        if 'read:all' in permissions:
            return True

        if 'read:own_service' in permissions:
            return query.get('service') in user.owned_services

        return False
```

### 3. Encryption

Encrypt data in transit and at rest:

```yaml
# OTLP with TLS
exporters:
  otlp:
    endpoint: collector:4317
    tls:
      cert_file: /certs/client.crt
      key_file: /certs/client.key
      ca_file: /certs/ca.crt

# Kafka with TLS
producer_config:
  security.protocol: SSL
  ssl.ca.location: /certs/ca.crt
  ssl.certificate.location: /certs/client.crt
  ssl.key.location: /certs/client.key
```

### 4. Audit Logging

Log access to telemetry:

```python
class AuditLogger:
    """Log access to telemetry data."""

    def log_query(self, user: str, query: dict, results_count: int):
        self.logger.info("Telemetry query", extra={
            "user": user,
            "query_type": query.get("type"),
            "time_range": query.get("time_range"),
            "results_count": results_count,
            "timestamp": datetime.utcnow().isoformat()
        })

    def log_export(self, user: str, export_type: str, data_size: int):
        self.logger.info("Telemetry export", extra={
            "user": user,
            "export_type": export_type,
            "data_size_bytes": data_size,
            "timestamp": datetime.utcnow().isoformat()
        })
```

---

## Anti-Patterns to Avoid

### 1. Metric Cardinality Explosion

```python
# ❌ BAD: Unbounded label values
metrics.record_counter("requests", labels={
    "user_id": "12345",  # Millions of unique values!
})

# ✅ GOOD: Bounded label values
metrics.record_counter("requests", labels={
    "user_tier": "premium",  # Few distinct values
    "region": "us-east-1",
})
```

### 2. Logging Too Much

```python
# ❌ BAD: Logging in hot paths
for i in range(1000000):
    logger.debug(f"Processing item {i}")  # Million log lines!
    process(items[i])

# ✅ GOOD: Sample or aggregate
processed = 0
for item in items:
    process(item)
    processed += 1

if processed % 10000 == 0:
    logger.info(f"Processed {processed} items")

logger.info(f"Completed: processed {processed} items")
```

### 3. Synchronous Export

```python
# ❌ BAD: Blocking on export
def handle_request(request):
    response = process(request)
    exporter.export(trace)  # Blocks!
    return response

# ✅ GOOD: Async/batch export
def handle_request(request):
    response = process(request)
    export_queue.put(trace)  # Non-blocking
    return response

# Background thread handles exports
```

### 4. Alert Fatigue

```python
# ❌ BAD: Alert on every error
if error_count > 0:
    send_alert("Errors detected!")

# ✅ GOOD: Alert on significant conditions
if error_rate > 0.05 and sustained_for > 300:
    send_alert(f"Error rate {error_rate}% for 5 minutes")
```

### 5. No Context Propagation

```python
# ❌ BAD: Losing trace context
def call_service(url, data):
    return requests.post(url, json=data)  # No trace headers!

# ✅ GOOD: Propagate context
def call_service(url, data):
    headers = {}
    inject(headers)  # Add traceparent header
    return requests.post(url, json=data, headers=headers)
```

---

## Operational Best Practices

### Capacity Planning

| Component | Sizing Factors |
|-----------|----------------|
| **Kafka** | Throughput × retention × replication |
| **Collector** | Events/sec × processing complexity |
| **Trace Backend** | Traces/sec × span count × retention |
| **Metrics Backend** | Series count × scrape interval × retention |
| **Log Backend** | Log lines/sec × avg size × retention |

### Retention Policies

| Data Type | Hot Storage | Warm Storage | Cold Storage |
|-----------|-------------|--------------|--------------|
| **Traces** | 7 days | 30 days | 1 year |
| **Metrics** | 15 days (1min) | 90 days (5min) | 2 years (1hr) |
| **Logs** | 7 days | 30 days | 1 year |
| **Alerts** | 90 days | 1 year | 5 years |

### Disaster Recovery

1. **Multi-region Kafka**: Replicate across regions
2. **Collector redundancy**: Multiple collectors per region
3. **Backend replication**: Use native replication features
4. **Backup exports**: Archive to S3/GCS for long-term

---

## Summary

| Topic | Key Points |
|-------|------------|
| **Design Patterns** | Factory, Strategy, Observer, Builder |
| **SOLID** | Single responsibility, open/closed, etc. |
| **Performance** | Batching, sampling, async, pooling |
| **Security** | Redaction, access control, encryption |
| **Anti-Patterns** | Cardinality, over-logging, sync export |

### Key Takeaways

1. **Apply proven patterns** - Factory, Strategy, Observer
2. **Follow SOLID principles** - maintainable, extensible code
3. **Optimize for performance** - batch, sample, async
4. **Secure your telemetry** - redact, encrypt, audit
5. **Avoid common pitfalls** - cardinality, alert fatigue

---

## What's Next?

Congratulations on completing the Observability Tutorial!

For quick reference during implementation, see the [Quick Reference Guide](QUICK_REFERENCE.md).

To practice what you've learned, try the [Hands-On Exercises](exercises/).

---

## Further Reading

- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [Grafana Loki Documentation](https://grafana.com/docs/loki/)
- [Kafka Documentation](https://kafka.apache.org/documentation/)
