# Enterprise Observability and Notification Data Pipeline Architecture

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Architecture Overview](#architecture-overview)
3. [Package Separation Decision](#package-separation-decision)
4. [Core Design Principles](#core-design-principles)
5. [Package Architecture](#package-architecture)
6. [OOP Design Patterns](#oop-design-patterns)
7. [Data Flow Architecture](#data-flow-architecture)
8. [Component Design](#component-design)
9. [Integration Patterns](#integration-patterns)
10. [Implementation Roadmap](#implementation-roadmap)
11. [Best Practices](#best-practices)

---

## Executive Summary

This document defines the Enterprise Observability and Notification Data Pipeline Architecture—a unified telemetry, analytics, and notification platform for database systems. The architecture follows object-oriented programming best practices and modern observability standards to deliver actionable intelligence across the organization.

At its core, the platform implements an event-driven streaming pipeline (Kappa-style architecture) with Kafka as the durable backbone. The telemetry collector acts as the telemetry producer, the alert evaluation service and analytical services are decoupled consumers, and downstream notification, storage, and visualization layers reuse the same canonical stream for replay, enrichment, and historical insight.

### Integration with Enterprise Notification Service

**Important Context**: This architecture integrates with an enterprise-grade notification service that provides:

- **HTTP API**: REST endpoint (e.g., `POST /alerts`) where alert payloads are submitted for processing and delivery
- **Message Queue**: Asynchronous processing and delivery buffering
- **Delivery Channels**: SMTP, SMS, chat, and other downstream transports
- **Recipient Resolution**: Directory or workflow integration for recipient targeting
- **Blackout Windows**: Scheduled suppression of notifications during maintenance or approved quiet periods

**Key Integration Points**:

- Alert evaluation service evaluates conditions and generates alerts
- Alert evaluation service formats alerts for the notification service API
- The notification service handles queuing, recipient lookup, delivery, and blackout-window enforcement
- Loose coupling through HTTP API and message queues

### High-Level Requirements

- Collect monitoring metrics at specified intervals from database systems and underlying operating systems (CPU utilization, memory usage, disk I/O, network throughput)
- Publish metrics to Kafka topics for real-time processing and analysis
- Consume metrics from Kafka and evaluate against configurable alert thresholds
- Send alerts via HTTP API to the notification service when thresholds exceeded
- Support for different database types (PostgreSQL, MongoDB, MSSQL, Snowflake)
- Configurable alerting rules and escalation policies

---

## Architecture Overview

### System Context

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Database & OS   │    │ Telemetry       │    │     Kafka      │
│ Systems         │───►│ Collector       │───►│   (Message     │
│                 │    │   Service       │    │    Bus)        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                         │
                                                         │
                    ┌────────────────────────────────────┼────────────────────────────────────┐
                    │                                    │                                    │
                    ▼                                    ▼                                    ▼
         ┌─────────────────┐                  ┌─────────────────┐                  ┌─────────────────┐
         │ Alert Evaluation│                  │   Data Warehouse │                  │   Analytics     │
         │    Service      │                  │   Importer       │                  │   Dashboard     │
         │                 │                  │   (Snowflake)     │                  │                 │
         └─────────────────┘                  └─────────────────┘                  └─────────────────┘
                    │                                    │                                    │
                    ▼                                    ▼                                    ▼
         ┌─────────────────┐                  ┌─────────────────┐                  ┌─────────────────┐
         │ Notification    │                  │   Long-term     │                  │   Real-time     │
         │   Service       │                  │   Storage       │                  │   Insights      │
         └─────────────────┘                  └─────────────────┘                  └─────────────────┘
                    │                                    │                                    │
                    ▼                                    ▼                                    ▼
         ┌─────────────────┐                  ┌─────────────────┐                  ┌─────────────────┐
         │   Email/SMS     │                  │   Historical    │                  │   Monitoring    │
         │   Recipients    │                  │   Analytics     │                  │   Trends        │
         └─────────────────┘                  └─────────────────┘                  └─────────────────┘
```

### Data Flow Summary (Event-Driven Streaming Pipeline)

1. **Database & OS Systems** → **Telemetry Collector Service**: Metrics collected at specified intervals
2. **Telemetry Collector Service** → **Kafka**: Metrics (database and infrastructure) published to topics for real-time processing
3. **Alert Evaluation Service** ← **Kafka**: Consumes metrics and evaluates against alert rules
4. **Data Warehouse Importer** ← **Kafka**: Loads metrics into Snowflake for long-term storage
5. **Analytics Dashboard** ← **Kafka**: Provides real-time monitoring insights
6. **Alert Evaluation Service** → **Notification Service**: Alerts sent via HTTP API when thresholds exceeded
7. **Notification Service** → **Recipients**: Emails delivered via SMTP

Note: Metrics flow through Kafka as the single source of truth. The alert evaluation service consumes Kafka topics; there is no direct tight coupling/stream from the telemetry collector to the alert evaluation service in the recommended design. This preserves loose coupling, enables replay, and keeps the data pipeline unified across telemetry, analytics, and alerting use cases.

---

## Package Separation Decision

### Analysis

After researching monitoring system architectures and analyzing existing implementations in the codebase, **separate packages are recommended** for the following reasons:

#### Arguments for Separation

1. **Single Responsibility Principle**: Each package has one clear purpose
   - Telemetry collector service: Collect and report metrics
   - Alert evaluation service: Evaluate conditions and notify stakeholders

2. **Independent Deployment**: Can update monitoring without affecting alerting logic

3. **Different Scaling Requirements**: Monitoring may need more frequent updates than alerting rules

4. **Technology Choices**: Monitoring and alerting may use different storage/notification technologies

5. **Team Organization**: Different teams can own monitoring vs alerting

#### Arguments Against Separation

1. **Tight Coupling**: Monitoring and alerting are closely related concepts
2. **Shared Dependencies**: Both need similar database connections and configurations
3. **Deployment Complexity**: More packages to manage and version

#### Decision: Separate Packages with Close Integration

**Recommendation**: Create separate telemetry collection and alert evaluation services that work together through well-defined interfaces. This provides the benefits of separation while maintaining ease of use.

**Integration Strategy**:

- Shared abstract interfaces in a common module
- Event-driven communication between packages
- Optional coupling through dependency injection

---

## Core Design Principles

### OOP Best Practices Applied

1. **Abstraction**: Abstract base classes define contracts
2. **Encapsulation**: Hide implementation details behind interfaces
3. **Inheritance**: Extend base classes for specific database types
4. **Composition**: Build complex systems from simpler components
5. **Polymorphism**: Support multiple implementations of the same interface

### SOLID Principles

1. **Single Responsibility**: Each class has one reason to change
2. **Open/Closed**: Open for extension, closed for modification
3. **Liskov Substitution**: Subtypes are substitutable for base types
4. **Interface Segregation**: Clients depend only on methods they use
5. **Dependency Inversion**: Depend on abstractions, not concretions

### Monitoring Best Practices

1. **Alert on Symptoms**: Monitor user-visible symptoms, not internal causes
2. **Alert Liberally, Page Judiciously**: Log all issues, page only on urgent problems
3. **Durable Alert Definitions**: Alerts should work across infrastructure changes
4. **Context-Rich Alerts**: Include actionable information in notifications

---

## Package Architecture

### Telemetry Collector Service Structure

```
telemetry_collector/
├── __init__.py
├── base.py              # Abstract base classes and interfaces
├── scheduler.py         # Monitoring scheduler
├── collectors/          # Metric collectors
│   ├── __init__.py
│   ├── base.py
│   ├── postgresql.py
│   ├── mongodb.py
│   ├── mssql.py
│   └── snowflake.py
├── outputs/             # Output handlers (Kafka)
│   ├── __init__.py
│   ├── base.py
│   └── kafka.py
├── config.py            # Configuration management
└── exceptions.py        # Custom exceptions
```

### Alert Evaluation Service Structure

```
alert_evaluation/
├── __init__.py
├── base.py              # Abstract base classes and interfaces
├── evaluator.py         # Alert evaluation engine
├── rules/               # Alert rules
│   ├── __init__.py
│   ├── base.py
│   ├── threshold.py
│   ├── anomaly.py
│   └── custom.py
├── notifiers/           # Integration with enterprise notification service
│   ├── __init__.py
│   ├── base.py
│   ├── notification_service.py  # HTTP client for notification service API
│   └── direct_email.py      # Fallback direct email (optional)
├── escalation.py        # Alert escalation policies
├── config.py            # Configuration management
└── exceptions.py        # Custom exceptions
```

### Shared Interfaces

```
observability_interfaces/
├── __init__.py
├── metrics.py           # Metric data structures
├── alerts.py            # Alert data structures
└── events.py            # Event definitions
```

---

## OOP Design Patterns

### 1. Abstract Factory Pattern

**Purpose**: Create families of related monitoring/alerting components

```python
class MonitorFactory(ABC):
    @abstractmethod
    def create_collector(self, db_type: str) -> MetricCollector:
        pass

    @abstractmethod
    def create_output(self, output_type: str) -> OutputHandler:
        pass

class DatabaseMonitorFactory(MonitorFactory):
    def create_collector(self, db_type: str) -> MetricCollector:
        if db_type == "postgresql":
            return PostgreSQLCollector()
        elif db_type == "mongodb":
            return MongoDBCollector()
        # ... other database types
```

### 2. Observer Pattern

**Purpose**: Notify multiple subscribers when metrics/alerts are generated

```python
class MetricPublisher:
    def __init__(self):
        self._subscribers: List[MetricSubscriber] = []

    def subscribe(self, subscriber: MetricSubscriber):
        self._subscribers.append(subscriber)

    def publish(self, metric: Metric):
        for subscriber in self._subscribers:
            subscriber.on_metric_received(metric)

class AlertEvaluator(MetricSubscriber):
    def on_metric_received(self, metric: Metric):
        # Evaluate metric against rules
        # Generate alerts if needed
        pass
```

### 3. Strategy Pattern

**Purpose**: Configure different evaluation/notification strategies

```python
class AlertEvaluationStrategy(ABC):
    @abstractmethod
    def evaluate(self, metric: Metric, rule: AlertRule) -> Optional[Alert]:
        pass

class ThresholdStrategy(AlertEvaluationStrategy):
    def evaluate(self, metric: Metric, rule: AlertRule) -> Optional[Alert]:
        if metric.value > rule.threshold:
            return Alert(severity=AlertSeverity.WARNING, ...)
        return None

class AnomalyStrategy(AlertEvaluationStrategy):
    def evaluate(self, metric: Metric, rule: AlertRule) -> Optional[Alert]:
        # Anomaly detection logic
        pass
```

### 4. Template Method Pattern

**Purpose**: Define the skeleton of monitoring/alerting workflows

```python
class BaseMonitor(ABC):
    def run_monitoring_cycle(self) -> MonitoringResult:
        """Template method defining monitoring workflow."""
        try:
            self.pre_check()
            metrics = self.collect_metrics()
            self.process_metrics(metrics)
            self.post_check()
            return MonitoringResult(success=True, metrics=metrics)
        except Exception as e:
            return MonitoringResult(success=False, error=str(e))

    @abstractmethod
    def collect_metrics(self) -> List[Metric]:
        pass

    def pre_check(self):
        pass  # Optional hook

    def post_check(self):
        pass  # Optional hook
```

### 5. Builder Pattern

**Purpose**: Construct complex monitoring/alerting configurations

```python
class MonitoringSystemBuilder:
    def __init__(self):
        self._collectors = []
        self._outputs = []
        self._schedules = []

    def add_collector(self, collector: MetricCollector):
        self._collectors.append(collector)
        return self

    def add_output(self, output: OutputHandler):
        self._outputs.append(output)
        return self

    def build(self) -> MonitoringSystem:
        return MonitoringSystem(
            collectors=self._collectors,
            outputs=self._outputs,
            scheduler=Scheduler(self._schedules)
        )
```

---

## Data Flow Architecture

### Metric Collection Flow

```
Database → Collector → Metric → [Output Handler] → Kafka (single source of truth)
                                    ↓
                                [Evaluator] → Alert → [Notifier] → Email/SMS/Slack
```

### Detailed Flow

1. **Collection Phase**:

- Scheduler triggers collection at specified intervals
- Collectors connect to database and operating systems to gather metrics
- Metrics are validated and enriched with metadata

2. **Publishing Phase**:
   - Metrics are published to Kafka topics with appropriate partitioning
   - Topics organized by database type, metric type, or environment
   - Enables real-time processing and multiple downstream consumers

3. **Consumption Phase**:
   - Alert evaluation service consumes metrics from Kafka topics
   - Rules engine evaluates metrics against configured thresholds
   - Alert generation when conditions are met

4. **Notification Phase**:
   - Alerts are formatted for the notification service API
   - HTTP requests sent to the notification service endpoint
   - The notification service handles queuing and delivery

### Kafka Topic Design and Partitioning

#### Topic Structure

```
gds.metrics.{database_type}.{environment}
gds.metrics.{database_type}.{environment}.{instance_id}
```

**Examples**:

- `gds.metrics.postgresql.production`
- `gds.metrics.mongodb.staging`
- `gds.metrics.snowflake.production.account123`

#### Partitioning Strategy

- **By Database Instance (recommended)**: Ensures metrics from the same instance go to the same partition to preserve per-instance ordering
- ~~By Time Window~~: Not recommended. Kafka partitions are static; use topic-level time-based retention instead of time-based partitioning
- **Key Design**: Prefer `{instance_id}` or `{instance_id}:{metric_type}` as the message key. Include `database_type` and `environment` in topic name rather than key.

#### Consumer Groups

- **Alerting Consumers**: `gds-alerting-{rule_group}` for parallel processing
- **Data Warehouse Consumers**: `gds-dw-importer` for batch loading to Snowflake
- **Analytics Consumers**: `gds-analytics` for real-time dashboards and reporting
- **Monitoring Consumers**: `gds-health-check` for system monitoring

#### Message Schema

```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "database_type": "postgresql",
  "instance_id": "prod-db-01",
  "metric_name": "cpu_usage_percent",
  "value": 85.5,
  "tags": {
    "environment": "production",
    "region": "us-east-1"
  },
  "metadata": {
    "collection_duration_ms": 150,
        "version": "1.0",
        "correlation_id": "7f9c1c7e-8b61-4d9d-9a10-9b3a6a7b1234"
  }
}
```

Recommendation: Use a schema registry (e.g., Confluent Schema Registry) with compatibility rules (backward or full) to manage schema evolution safely.

#### Schema Evolution Strategy

##### Compatibility Rules

**1. Backward Compatibility** (Recommended for most cases)

- **Rule**: New schema can read data written with old schema
- **Use Case**: Adding optional fields, removing fields
- **Example**: Adding a new optional field to metrics

```json
// Version 1
{
  "timestamp": "2025-01-15T10:30:00Z",
  "metric_name": "cpu_usage_percent",
  "value": 85.5
}

// Version 2 (Backward Compatible)
{
  "timestamp": "2025-01-15T10:30:00Z",
  "metric_name": "cpu_usage_percent",
  "value": 85.5,
  "collection_method": "agent"  // New optional field
}
```

**2. Forward Compatibility**

- **Rule**: Old schema can read data written with new schema
- **Use Case**: Removing fields, adding fields that old code can ignore

**3. Full Compatibility**

- **Rule**: Both backward and forward compatible
- **Use Case**: Production systems where old and new code run simultaneously

##### Schema Registry Configuration

```python
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer

class SchemaManager:
    """Manage schema registration and evolution."""

    def __init__(self, registry_url: str):
        self.registry_client = SchemaRegistryClient({'url': registry_url})
        self.schema_cache = {}

    def register_schema(
        self,
        subject: str,
        schema_str: str,
        compatibility: str = "BACKWARD"
    ) -> int:
        """Register new schema version with compatibility check."""
        # Set compatibility mode
        self.registry_client.set_compatibility(subject, compatibility)

        # Register schema
        schema_id = self.registry_client.register_schema(subject, schema_str)
        logger.info(f"Registered schema {subject} with ID {schema_id}")

        return schema_id

    def get_schema(self, schema_id: int):
        """Get schema by ID with caching."""
        if schema_id not in self.schema_cache:
            schema = self.registry_client.get_schema(schema_id)
            self.schema_cache[schema_id] = schema
        return self.schema_cache[schema_id]
```

##### Schema Version Management

```python
# Avro schema definition with versioning
metric_schema_v1 = """
{
  "type": "record",
  "name": "Metric",
  "namespace": "com.gds.monitoring",
  "version": "1.0",
  "fields": [
    {"name": "timestamp", "type": "string"},
    {"name": "database_type", "type": "string"},
    {"name": "instance_id", "type": "string"},
    {"name": "metric_name", "type": "string"},
    {"name": "value", "type": "double"},
    {"name": "tags", "type": {"type": "map", "values": "string"}},
    {"name": "metadata", "type": {"type": "map", "values": "string"}}
  ]
}
"""

# Version 2: Add optional fields (backward compatible)
metric_schema_v2 = """
{
  "type": "record",
  "name": "Metric",
  "namespace": "com.gds.monitoring",
  "version": "2.0",
  "fields": [
    {"name": "timestamp", "type": "string"},
    {"name": "database_type", "type": "string"},
    {"name": "instance_id", "type": "string"},
    {"name": "metric_name", "type": "string"},
    {"name": "value", "type": "double"},
    {"name": "tags", "type": {"type": "map", "values": "string"}},
    {"name": "metadata", "type": {"type": "map", "values": "string"}},
    {"name": "collection_method", "type": ["null", "string"], "default": null},
    {"name": "collector_version", "type": ["null", "string"], "default": null}
  ]
}
"""
```

##### Breaking Change Migration Strategy

When breaking changes are unavoidable:

1. **Dual Write Period**: Write to both old and new topics
2. **Consumer Migration**: Update consumers to read from new topic
3. **Deprecation Period**: Maintain old topic for 30 days
4. **Cleanup**: Remove old topic and legacy code

```python
class DualWritePublisher:
    """Publish to both old and new topics during migration."""

    def __init__(self, old_topic: str, new_topic: str):
        self.old_topic = old_topic
        self.new_topic = new_topic
        self.producer = KafkaProducer(...)

    async def publish_metric(self, metric: Metric):
        """Publish to both topics during migration period."""
        # Publish to old topic (v1 schema)
        old_format = self._convert_to_v1(metric)
        self.producer.send(self.old_topic, value=old_format)

        # Publish to new topic (v2 schema)
        new_format = self._convert_to_v2(metric)
        self.producer.send(self.new_topic, value=new_format)
```

#### Kafka Configuration Best Practices

##### Producer Configuration

```python
producer_config = {
    # Reliability settings
    'acks': 'all',  # Wait for all in-sync replicas to acknowledge
    'enable.idempotence': True,  # Exactly-once semantics within partition
    'max.in.flight.requests.per.connection': 5,  # Max unacked requests
    'retries': 2147483647,  # Retry indefinitely (with timeout)
    'delivery.timeout.ms': 120000,  # 2 minute total timeout
    'request.timeout.ms': 30000,  # 30 second per-request timeout

    # Performance settings
    'compression.type': 'lz4',  # Fast compression (alternatives: snappy, gzip, zstd)
    'linger.ms': 100,  # Wait up to 100ms to batch messages
    'batch.size': 16384,  # Batch size in bytes (16KB)
    'buffer.memory': 33554432,  # 32MB total buffer

    # Connection settings
    'bootstrap.servers': 'kafka-1:9092,kafka-2:9092,kafka-3:9092',
    'client.id': 'gds-monitor-producer',
    'security.protocol': 'SASL_SSL',
    'sasl.mechanism': 'PLAIN',  # Or SCRAM-SHA-256/SCRAM-SHA-512
    'ssl.ca.location': '/path/to/ca-cert',
}
```

##### Consumer Configuration

```python
consumer_config = {
    # Group and offset management
    'group.id': 'gds-alerting-production',
    'enable.auto.commit': False,  # Manual commit for reliability
    'auto.offset.reset': 'earliest',  # Start from beginning for new consumers
    'isolation.level': 'read_committed',  # Only read committed messages (for transactions)

    # Performance settings
    'fetch.min.bytes': 1024,  # Wait for at least 1KB
    'fetch.max.wait.ms': 500,  # Or wait max 500ms
    'max.partition.fetch.bytes': 1048576,  # 1MB per partition
    'max.poll.records': 500,  # Process up to 500 records per poll
    'max.poll.interval.ms': 300000,  # 5 minutes to process batch

    # Session and heartbeat
    'session.timeout.ms': 30000,  # 30 seconds before rebalance
    'heartbeat.interval.ms': 10000,  # Heartbeat every 10 seconds

    # Connection settings
    'bootstrap.servers': 'kafka-1:9092,kafka-2:9092,kafka-3:9092',
    'client.id': 'gds-alerting-consumer-1',
    'security.protocol': 'SASL_SSL',
    'sasl.mechanism': 'PLAIN',
    'ssl.ca.location': '/path/to/ca-cert',
}
```

##### Topic Configuration

```python
topic_config = {
    'num.partitions': 12,  # Based on parallelism needs
    'replication.factor': 3,  # At least 3 for production
    'min.insync.replicas': 2,  # At least 2 replicas must acknowledge
    'retention.ms': 604800000,  # 7 days (adjust based on needs)
    'retention.bytes': 1073741824,  # 1GB per partition (optional)
    'segment.ms': 3600000,  # 1 hour segments
    'cleanup.policy': 'delete',  # Or 'compact' for stateful data
    'compression.type': 'producer',  # Use producer's compression
}
```

#### Kafka Offset Management and Exactly-Once Semantics

##### Offset Commit Strategies

**1. Manual Commit After Processing (Recommended for Alerting)**

```python
from kafka import KafkaConsumer
import asyncio

class AlertingConsumer:
    """Consumer with manual offset management for reliable processing."""

    def __init__(self, config: dict):
        self.consumer = KafkaConsumer(
            **config,
            enable_auto_commit=False  # Manual commits only
        )
        self.batch_size = 100
        self.commit_interval = 10  # Commit every 10 seconds
        self.last_commit_time = time.time()

    async def consume_and_alert(self):
        """Consume metrics and process alerts with offset management."""
        batch = []

        try:
            for message in self.consumer:
                try:
                    # Deserialize metric
                    metric = self._deserialize_metric(message.value)

                    # Evaluate and send alerts
                    await self._process_metric(metric)

                    # Track for commit
                    batch.append(message)

                    # Commit periodically or when batch is full
                    if len(batch) >= self.batch_size or \
                       time.time() - self.last_commit_time >= self.commit_interval:
                        await self._commit_batch(batch)
                        batch = []
                        self.last_commit_time = time.time()

                except Exception as e:
                    logger.error(f"Failed to process message: {e}")
                    # Handle poison pill: send to DLQ
                    await self._send_to_dlq(message, e)
                    # Still commit to move past the bad message
                    self.consumer.commit()

        except KeyboardInterrupt:
            logger.info("Shutting down consumer...")
        finally:
            # Commit any remaining messages
            if batch:
                await self._commit_batch(batch)
            self.consumer.close()

    async def _commit_batch(self, batch: List):
        """Commit offsets for processed batch."""
        if not batch:
            return

        try:
            # Synchronous commit for reliability
            self.consumer.commit()
            logger.info(f"Committed {len(batch)} messages")
        except Exception as e:
            logger.error(f"Failed to commit offsets: {e}")
            # On commit failure, messages will be reprocessed
            # Ensure idempotent alert handling
            raise
```

**2. Idempotent Processing**

```python
class IdempotentAlertHandler:
    """Ensure alerts are only sent once even if messages reprocessed."""

    def __init__(self, redis_client):
        self.redis = redis_client
        self.dedup_ttl = 3600  # 1 hour deduplication window

    async def send_alert_idempotent(self, alert: Alert) -> bool:
        """Send alert only if not already sent recently."""
        # Create idempotency key from alert ID and timestamp bucket
        idempotency_key = f"alert:sent:{alert.id}"

        # Try to set key (atomic operation)
        was_set = await self.redis.set(
            idempotency_key,
            "1",
            ex=self.dedup_ttl,
            nx=True  # Only set if not exists
        )

        if was_set:
            # First time seeing this alert, send it
            await self._send_alert(alert)
            return True
        else:
            # Already sent, skip
            logger.info(f"Alert {alert.id} already sent, skipping")
            return False
```

**3. Exactly-Once Semantics with Transactions**

```python
from kafka import KafkaProducer

class TransactionalMetricPublisher:
    """Producer with transactional exactly-once semantics."""

    def __init__(self, config: dict):
        self.producer = KafkaProducer(
            **config,
            transactional_id='gds-monitor-producer-1',  # Unique per instance
            enable.idempotence=True,
            acks='all'
        )
        self.producer.init_transactions()

    async def publish_metrics_transactional(self, metrics: List[Metric]):
        """Publish batch of metrics in single transaction."""
        try:
            self.producer.begin_transaction()

            for metric in metrics:
                # Partition by instance_id for ordering
                key = metric.instance_id.encode('utf-8')
                value = self._serialize_metric(metric)

                self.producer.send(
                    topic=self._get_topic(metric),
                    key=key,
                    value=value
                )

            # Commit transaction
            self.producer.commit_transaction()
            logger.info(f"Published {len(metrics)} metrics transactionally")

        except Exception as e:
            logger.error(f"Transaction failed: {e}")
            self.producer.abort_transaction()
            raise
```

##### Dead Letter Queue (DLQ) Pattern

```python
class DLQHandler:
    """Handle messages that fail processing repeatedly."""

    def __init__(self, producer_config: dict):
        self.dlq_topic = "gds.metrics.dlq"
        self.producer = KafkaProducer(**producer_config)
        self.max_retries = 3
        self.retry_tracker = {}  # In production: use Redis/DB

    async def send_to_dlq(
        self,
        message: ConsumerRecord,
        error: Exception,
        metadata: dict = None
    ):
        """Send failed message to DLQ with error context."""
        dlq_message = {
            "original_topic": message.topic,
            "original_partition": message.partition,
            "original_offset": message.offset,
            "original_key": message.key,
            "original_value": message.value,
            "error": str(error),
            "error_type": type(error).__name__,
            "timestamp": datetime.utcnow().isoformat(),
            "retry_count": self.retry_tracker.get(message.key, 0),
            "metadata": metadata or {}
        }

        # Send to DLQ
        self.producer.send(
            self.dlq_topic,
            key=message.key,
            value=json.dumps(dlq_message).encode('utf-8')
        )

        # Alert on DLQ growth
        await self._check_dlq_size()

    async def _check_dlq_size(self):
        """Alert if DLQ is growing."""
        # Monitor DLQ lag and alert if exceeds threshold
        pass
```

### Data Warehouse Integration

#### Snowflake Importer Architecture

- **Consumer Group**: `gds-dw-importer`
- **Batch Processing**: Accumulates metrics and loads in optimized batches
- **Schema Design**: Star schema with metrics fact table and dimension tables
- **Retention**: Configurable retention policies (30-365 days typical)
- **Compression**: Uses Snowflake's native compression for cost optimization

#### Analytics Use Cases

- **Historical Trending**: Long-term performance analysis and capacity planning
- **Anomaly Detection**: ML-based anomaly detection on historical patterns
- **Predictive Analytics**: Forecast resource usage and identify trends
- **Compliance Reporting**: Audit trails and compliance dashboards
- **Cost Optimization**: Identify underutilized resources and optimization opportunities

#### Real-time Dashboards

- **Live Monitoring**: Real-time views of system health across all databases
- **Alert Correlation**: Visualize alert patterns and system-wide impacts
- **Performance Metrics**: Response times, throughput, and error rates
- **Capacity Planning**: Usage trends and forecasting

### Business Value

#### Unified Data Pipeline Benefits

- **Single Source of Truth**: All metrics flow through one pipeline, ensuring consistency
- **Cost Efficiency**: One collection system serves multiple business needs
- **Faster Insights**: Real-time alerting combined with historical trend analysis
- **Operational Excellence**: Proactive monitoring with predictive analytics
- **Compliance & Audit**: Complete audit trail from collection to long-term storage

#### Use Case Examples

- **Operations Team**: Real-time alerts for immediate response
- **Engineering Team**: Historical analysis for performance optimization
- **Business Intelligence**: Usage patterns for capacity planning
- **Finance Team**: Cost analysis based on resource utilization
- **Compliance Team**: Audit trails and reporting

---

## Component Design

### Monitoring Components

#### MetricCollector (Abstract Base Class)

```python
class MetricCollector(ABC):
    def __init__(self, connection_config: ConnectionConfig):
        self.connection_config = connection_config
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def collect(self) -> List[Metric]:
        """Collect metrics from the database."""
        pass

    @abstractmethod
    def validate_connection(self) -> bool:
        """Validate database connection."""
        pass

    def get_metadata(self) -> Dict[str, Any]:
        """Get collector metadata."""
        return {
            "collector_type": self.__class__.__name__,
            "connection_config": self.connection_config.to_dict()
        }
```

#### Scheduler

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import asyncio
import signal

class MonitoringScheduler:
    """Async scheduler for monitoring jobs with graceful shutdown."""

    def __init__(self):
        self._jobs: Dict[str, ScheduledJob] = {}
        self._scheduler = AsyncIOScheduler()
        self._running = False
        self._shutdown_event = asyncio.Event()
        self._in_flight_tasks: Set[asyncio.Task] = set()

    def schedule_job(
        self,
        job_id: str,
        collector: MetricCollector,
        interval: timedelta,
        outputs: List[OutputHandler]
    ):
        """Schedule a monitoring job."""
        job = ScheduledJob(job_id, collector, interval, outputs)
        self._jobs[job_id] = job

        # Schedule async job execution
        self._scheduler.add_job(
            self._execute_job,
            trigger=IntervalTrigger(seconds=interval.total_seconds()),
            args=[job],
            id=job_id,
            replace_existing=True
        )

    async def _execute_job(self, job: ScheduledJob):
        """Execute a single monitoring job."""
        task = asyncio.create_task(self._run_job(job))
        self._in_flight_tasks.add(task)
        task.add_done_callback(self._in_flight_tasks.discard)

    async def _run_job(self, job: ScheduledJob):
        """Run job with error handling."""
        try:
            metrics = await job.collector.collect()
            for output in job.outputs:
                await output.send(metrics)
        except Exception as e:
            logger.error(f"Job {job.job_id} failed: {e}", exc_info=True)

    def start(self):
        """Start all scheduled jobs."""
        self._running = True
        self._scheduler.start()

        # Set up signal handlers for graceful shutdown
        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, lambda s, f: asyncio.create_task(self.shutdown()))

    async def shutdown(self, timeout: int = 30):
        """Graceful shutdown: stop accepting jobs, wait for in-flight, close connections."""
        if not self._running:
            return

        logger.info("Initiating graceful shutdown...")
        self._running = False

        # Stop scheduler from starting new jobs
        self._scheduler.shutdown(wait=False)

        # Wait for in-flight jobs with timeout
        if self._in_flight_tasks:
            logger.info(f"Waiting for {len(self._in_flight_tasks)} in-flight jobs...")
            try:
                await asyncio.wait_for(
                    asyncio.gather(*self._in_flight_tasks, return_exceptions=True),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                logger.warning(f"Shutdown timeout after {timeout}s, cancelling remaining tasks")
                for task in self._in_flight_tasks:
                    task.cancel()

        # Flush any buffered metrics to outputs
        await self._flush_outputs()

        # Close all connections
        await self._close_connections()

        logger.info("Graceful shutdown complete")
        self._shutdown_event.set()

    async def _flush_outputs(self):
        """Flush all output buffers."""
        for job in self._jobs.values():
            for output in job.outputs:
                if hasattr(output, 'flush'):
                    await output.flush()

    async def _close_connections(self):
        """Close all collector and output connections."""
        for job in self._jobs.values():
            if hasattr(job.collector, 'close'):
                await job.collector.close()
            for output in job.outputs:
                if hasattr(output, 'close'):
                    await output.close()
```

### Alerting Components

#### AlertEvaluator

```python
class AlertEvaluator:
    def __init__(self, rules: List[AlertRule]):
        self.rules = rules
        self.active_alerts: Dict[str, Alert] = {}

    def evaluate_metrics(self, metrics: List[Metric]) -> List[Alert]:
        """Evaluate metrics against alert rules."""
        alerts = []
        for metric in metrics:
            for rule in self.rules:
                if self._should_evaluate_rule(rule, metric):
                    alert = self._evaluate_rule(rule, metric)
                    if alert:
                        alerts.append(alert)
        return alerts

    def _evaluate_rule(self, rule: AlertRule, metric: Metric) -> Optional[Alert]:
        """Evaluate a single rule against a metric."""
        # Rule evaluation logic
        pass

    def _dedup_key(self, rule: AlertRule, metric: Metric, window_minutes: int = 15) -> str:
        """Stable deduplication key with time window to allow re-firing after cooldown."""
        resource_id = metric.tags.get("instance_id") or metric.instance_id
        # Time bucket to allow alert to re-fire after cooldown period
        time_bucket = int(metric.timestamp.timestamp() // (window_minutes * 60))
        return f"{rule.id}:{resource_id}:{metric.metric_name}:{time_bucket}"

    def _should_fire_alert(self, dedup_key: str, alert: Alert) -> bool:
        """Determine if alert should fire based on state machine."""
        if dedup_key not in self.active_alerts:
            return True  # New alert

        existing = self.active_alerts[dedup_key]
        if existing.state == AlertState.RESOLVED:
            return True  # Previous alert resolved, can fire again

        if existing.state == AlertState.SILENCED:
            return False  # Alert is silenced

        # Check for flapping: if alert fired and resolved multiple times in short window
        if self._is_flapping(dedup_key):
            logger.warning(f"Alert {dedup_key} is flapping, suppressing")
            return False

        return False  # Alert already active

class AlertState(Enum):
    """Alert lifecycle states."""
    FIRING = "firing"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SILENCED = "silenced"

@dataclass
class Alert:
    """Enhanced alert with state management."""
    id: str
    rule_id: str
    severity: AlertSeverity
    message: str
    metric: Metric
    timestamp: datetime
    state: AlertState = AlertState.FIRING
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    fire_count: int = 1  # Track flapping
    labels: Dict[str, str] = field(default_factory=dict)
    runbook_url: Optional[str] = None
    dashboard_url: Optional[str] = None
    correlation_id: Optional[str] = None
```

#### AlertNotifier

```python
class AlertNotifier(ABC):
    @abstractmethod
    async def notify(self, alert: Alert) -> bool:
        """Send notification for alert."""
        pass

class NotificationServiceNotifier(AlertNotifier):
    """Notifier that integrates with the enterprise notification service."""

    def __init__(self, notification_api_url: str, timeout: int = 30):
        self.api_url = notification_api_url
        self.timeout = timeout
        self.session = aiohttp.ClientSession()

    async def notify(self, alert: Alert) -> bool:
        """Send alert to the notification service."""
        payload = self._format_alert_for_api(alert)
        async with self.session.post(
            f"{self.api_url}/ingest",
            json=payload,
            timeout=self.timeout
        ) as response:
            return response.status == 200

    def _format_alert_for_api(self, alert: Alert) -> dict:
        """Format alert for the notification service API with rich context."""
        return {
            "alert_name": alert.rule_id,
            "db_instance_id": self._extract_db_instance_id(alert),
            "subject": f"[{alert.severity.name}] {alert.message[:50]}...",
            "body_text": self._format_alert_body(alert),
            "message_id": str(alert.id),            # Idempotency key
            "severity": alert.severity.name,
            "runbook_url": alert.runbook_url,
            "dashboard_url": alert.dashboard_url,
            "labels": alert.labels,
            "routing_key": self._get_routing_key(alert),
            "correlation_id": alert.correlation_id or str(uuid.uuid4()),
            "state": alert.state.value,
            "environment": alert.labels.get("environment", "unknown"),
            "service_owner": alert.labels.get("owner", "unknown"),
            "on_call_person": self._get_on_call(alert),
            "affected_users_count": self._estimate_impact(alert),
            "related_alerts": self._get_related_alerts(alert),
            "context": {
                "metric_value": alert.metric.value,
                "threshold": self._get_threshold(alert),
                "instance_name": alert.metric.tags.get("instance_name"),
                "region": alert.metric.tags.get("region"),
                "alert_fired_at": alert.timestamp.isoformat(),
                "fire_count": alert.fire_count
            }
        }

    def _format_alert_body(self, alert: Alert) -> str:
        """Format detailed alert body with actionable information."""
        body = f"""
Alert: {alert.message}

Severity: {alert.severity.name}
State: {alert.state.value}
Environment: {alert.labels.get('environment', 'unknown')}

Metric Details:
- Name: {alert.metric.metric_name}
- Value: {alert.metric.value}
- Instance: {alert.metric.tags.get('instance_id', 'unknown')}
- Region: {alert.metric.tags.get('region', 'unknown')}
- Timestamp: {alert.timestamp.isoformat()}

Impact:
- Estimated affected users: {self._estimate_impact(alert)}
- Service owner: {alert.labels.get('owner', 'unknown')}
- On-call: {self._get_on_call(alert)}

Actions:
- Runbook: {alert.runbook_url or 'N/A'}
- Dashboard: {alert.dashboard_url or 'N/A'}
- Correlation ID: {alert.correlation_id or 'N/A'}

Related Alerts:
{self._format_related_alerts(alert)}
"""
        return body.strip()
```

#### Circuit Breaker Implementation

```python
from enum import Enum
import time
from typing import Callable, TypeVar, Optional
import asyncio

class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered

T = TypeVar('T')

class CircuitBreaker:
    """Circuit breaker for external service calls with exponential backoff."""

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        success_threshold: int = 2,
        half_open_timeout: int = 30
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout  # Seconds before trying again
        self.success_threshold = success_threshold
        self.half_open_timeout = half_open_timeout

        self.failure_count = 0
        self.success_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time: Optional[float] = None
        self.last_state_change: float = time.time()

    async def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute function with circuit breaker protection."""
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time >= self.timeout:
                logger.info("Circuit breaker transitioning to HALF_OPEN")
                self._transition_to_half_open()
            else:
                raise CircuitOpenError(
                    f"Circuit breaker is OPEN. "
                    f"Will retry in {self.timeout - (time.time() - self.last_failure_time):.0f}s"
                )

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """Handle successful call."""
        self.failure_count = 0

        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                logger.info("Circuit breaker transitioning to CLOSED")
                self._transition_to_closed()
        elif self.state == CircuitState.CLOSED:
            self.success_count += 1

    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        self.success_count = 0

        if self.state == CircuitState.HALF_OPEN:
            logger.warning("Circuit breaker transitioning to OPEN (failure in HALF_OPEN)")
            self._transition_to_open()
        elif self.state == CircuitState.CLOSED:
            if self.failure_count >= self.failure_threshold:
                logger.error(f"Circuit breaker transitioning to OPEN after {self.failure_count} failures")
                self._transition_to_open()

    def _transition_to_open(self):
        """Transition to OPEN state."""
        self.state = CircuitState.OPEN
        self.last_state_change = time.time()
        # Emit metric for monitoring
        emit_metric("circuit_breaker.state_change", {"state": "open"})

    def _transition_to_half_open(self):
        """Transition to HALF_OPEN state."""
        self.state = CircuitState.HALF_OPEN
        self.last_state_change = time.time()
        self.success_count = 0
        emit_metric("circuit_breaker.state_change", {"state": "half_open"})

    def _transition_to_closed(self):
        """Transition to CLOSED state."""
        self.state = CircuitState.CLOSED
        self.last_state_change = time.time()
        self.failure_count = 0
        emit_metric("circuit_breaker.state_change", {"state": "closed"})

class CircuitOpenError(Exception):
    """Exception raised when circuit breaker is open."""
    pass

# Usage in NotificationServiceNotifier
class NotificationServiceNotifierWithCircuitBreaker(AlertNotifier):
    """Notifier with circuit breaker protection."""

    def __init__(self, notification_api_url: str, timeout: int = 30):
        self.api_url = notification_api_url
        self.timeout = timeout
        self.session = aiohttp.ClientSession()
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            timeout=60,
            success_threshold=2
        )

    async def notify(self, alert: Alert) -> bool:
        """Send alert with circuit breaker protection."""
        try:
            return await self.circuit_breaker.call(self._send_alert, alert)
        except CircuitOpenError as e:
            logger.error(f"Circuit breaker is open: {e}")
            # Optionally: queue for retry or use fallback notifier
            await self._handle_circuit_open(alert)
            return False

    async def _send_alert(self, alert: Alert) -> bool:
        """Internal method to send alert."""
        payload = self._format_alert_for_api(alert)
        async with self.session.post(
            f"{self.api_url}/ingest",
            json=payload,
            timeout=self.timeout
        ) as response:
            if response.status != 200:
                raise Exception(f"HTTP {response.status}")
            return True
```

---

## Integration Patterns

### HTTP API Integration with Notification Service

The alert evaluation service integrates with the enterprise notification service through HTTP API calls:

1. **Alert Formatting**: Convert internal Alert objects to the notification service API format
2. **HTTP Client**: Async HTTP client for reliable API communication
3. **Error Handling**: Circuit breaker pattern for API failures
4. **Idempotency**: Use alert IDs for duplicate prevention
5. **Fallback Options**: Direct email as fallback if the notification service is unavailable
6. **Rate Limiting & Backoff**: Apply client-side rate limits and exponential backoff with jitter to prevent thundering herds
7. **Bulkhead Isolation**: Use separate worker pools per destination (Email, Slack, PagerDuty) within the notification service

### Loose Coupling Strategy

The services are designed to work together but remain loosely coupled:

1. **Interface-Based Communication**: Both services implement common interfaces
2. **Event-Driven Architecture**: Metrics and alerts are published as events
3. **Dependency Injection**: Components are injected rather than imported directly
4. **Configuration-Driven**: Integration is configured rather than hardcoded
5. **Dead Letter Queues (DLQ)**: Route repeatedly failing messages to DLQ with retention and a replay process

### Integration Example

```python
# Configure monitoring system (Kafka-only output)
monitor = MonitoringSystem()
monitor.add_collector(PostgreSQLCollector(config))
monitor.add_output(KafkaOutput(kafka_config))  # Exclusive output

# Configure alerting system (Kafka consumer)
alerter = AlertingSystem(kafka_consumer_config)
alerter.add_rule(ThresholdRule("cpu_usage", ">", 80, AlertSeverity.WARNING))

# Configure notification service integration
alerter.add_notifier(NotificationServiceNotifier(notification_config))

# Start systems independently
monitor.start()  # Publishes to Kafka
alerter.start()  # Consumes from Kafka and alerts
```

### Data Format Mapping

```python
# Internal Alert format
@dataclass
class Alert:
    id: str
    rule_id: str
    severity: AlertSeverity
    message: str
    metric: Metric
    timestamp: datetime

# Maps to notification service API format
{
    "alert_name": alert.rule_id,        # Maps to rule_id
    "db_instance_id": extracted_id,     # From metric tags
    "subject": f"Alert: {message[:50]}",
    "body_text": formatted_body,
    "message_id": str(alert.id),        # For idempotency
    "severity": alert.severity.name,
    "runbook_url": alert.runbook_url,
    "labels": alert.labels
}
```

### OpenTelemetry Integration

This platform SHOULD adopt OpenTelemetry (OTel) across services for end-to-end correlation and standardized telemetry delivery. See `docs/architecture/observability/OPENTELEMETRY_ARCHITECTURE.md` for the comprehensive OTel design. This section summarizes required integration points for this pipeline.

- Signals: traces, metrics, logs via OTLP to an OpenTelemetry Collector (agent + gateway pattern).
- Context propagation: W3C Trace Context (`traceparent`) across HTTP and Kafka headers; include `correlation_id` as span attribute.
- Exemplars: attach trace exemplars to key metrics to enable metric-to-trace pivots in dashboards.
- Collector: use processors for batching, resource detection, Kubernetes attributes, attributes redaction, tail-based sampling; exporters to Kafka (optional), Prometheus, Tempo/Jaeger, and Loki.
- Structured logs: JSON logs enriched with `trace_id`, `span_id`, `service.name`, `deployment.environment`.

Minimal requirements:
- All outbound HTTP calls (e.g., to Notification Service) inject trace context.
- Kafka producers/consumers inject/extract trace context in message headers.
- Emit span(s) around alert evaluation, enrichment, remediation, and notification for full lifecycle traceability.

References:
- `OPENTELEMETRY_ARCHITECTURE.md` (collection pipelines, semantic conventions, example configs)

---

## Alert Enrichment and Auto-Remediation

After alert rule evaluation determines an alert should fire, the system performs automated triage and safe remediation before notifying stakeholders. The workflow is orchestrated with strict guardrails, idempotency, and full auditing.

### Workflow Phases

1) Evaluate (existing): rules, deduplication, cooldown, inhibition.
2) Enrichment (automated info gathering, timeboxed):
   - Recent logs for the resource (±5–10 minutes), host metrics (CPU/mem/IO), DB health (connections, locks, replication lag), dependency health, Kafka lag, recent deploys/changes, related alerts.
   - Normalize artifacts, store durable links (logs/traces/dashboards/snapshots) for inclusion in the alert.
   - Cache frequent lookups with short TTL to reduce load.
3) Auto-Remediation (policy-driven, guarded):
   - Preconditions: maintenance windows, change windows, blast radius checks, environment allowlists.
   - Allowed actions (examples): restart collector agent, recycle DB connection pool, restart alert consumer, switch to read replica.
   - Idempotent execution with rate limits and concurrency locks; verify success; rollback on failure; bounded retries with backoff/jitter.
4) Notification:
   - Always send alert to Notification Service with enrichment artifacts and remediation results, including verification outcome and whether alert was auto-resolved or requires action.

### Governance and Safety Guardrails

- Action allowlist per environment; high‑risk actions require explicit approval policy.
- Per-resource rate limits; exponential backoff and jitter.
- Maintenance/silence/change window awareness.
- Idempotency keys and distributed locks to prevent duplicate concurrent actions.
- Full audit trail of inputs, actions, outputs, verification, and rollbacks.

### Extended Alert Schema (additions)

```json
{
  "enrichment_artifacts": [
    {"type": "logs", "url": "https://..."},
    {"type": "trace", "trace_id": "abc...", "url": "https://..."},
    {"type": "dashboard", "url": "https://..."},
    {"type": "snapshot", "url": "s3://..."}
  ],
  "remediation_attempted": true,
  "remediation_steps": [
    {
      "name": "recycle_db_pool",
      "started_at": "2025-11-10T10:22:03Z",
      "ended_at": "2025-11-10T10:22:08Z",
      "status": "SUCCESS",
      "output_ref": "s3://.../logs.txt"
    }
  ],
  "verification": {
    "checks": [
      {"type": "metric_threshold_ok", "status": "PASS"},
      {"type": "error_rate_normalized", "status": "PASS"}
    ]
  },
  "auto_resolved": true,
  "residual_risk": "low"
}
```

### KPIs to Track

- Auto-remediation success rate, rollback rate, time-to-mitigate, false-positive remediation rate, human escalation rate, enrichment latency, enrichment cache hit rate.

---

## Cross-Pillar Correlation

- Require `trace_id` and `span_id` in logs; add exemplars from metrics to traces.
- Include pivot links in notifications: “Open trace,” “Open logs (±5m),” “Open dashboard (scoped).”
- Standardize labels using OTel semantic conventions (e.g., `db.system`, `db.instance`, `deployment.environment`, `host.name`, `region`).

---

## Stateful Stream Alerting (Optional)

For complex stateful rules (windows, joins, rates), consider Kafka Streams or Flink with tumbling/sliding windows and windowed aggregation. This offloads heavy state from the evaluator and scales horizontally while preserving ordering per key (e.g., `{instance_id}`).

---

### Testing Strategy

#### Unit Testing

```python
import pytest
from unittest.mock import Mock, AsyncMock, patch
import asyncio

class TestMetricCollector:
    """Unit tests for metric collector."""

    @pytest.fixture
    def mock_db_connection(self):
        """Mock database connection."""
        conn = AsyncMock()
        conn.fetch.return_value = [
            {"metric_name": "cpu_usage", "value": 85.5},
            {"metric_name": "memory_usage", "value": 75.2}
        ]
        return conn

    @pytest.mark.asyncio
    async def test_collect_metrics_success(self, mock_db_connection):
        """Test successful metric collection."""
        collector = PostgreSQLCollector(connection_config)
        collector.pool = Mock()
        collector.pool.acquire = AsyncMock(return_value=mock_db_connection)

        metrics = await collector.collect()

        assert len(metrics) == 2
        assert metrics[0].metric_name == "cpu_usage"
        assert metrics[0].value == 85.5

    @pytest.mark.asyncio
    async def test_collect_metrics_with_retry(self, mock_db_connection):
        """Test metric collection with retry on failure."""
        collector = PostgreSQLCollector(connection_config)

        # Fail first attempt, succeed second
        mock_db_connection.fetch.side_effect = [
            Exception("Connection timeout"),
            [{"metric_name": "cpu_usage", "value": 85.5}]
        ]

        metrics = await collector.collect()

        assert len(metrics) == 1
        assert mock_db_connection.fetch.call_count == 2

class TestAlertEvaluator:
    """Unit tests for alert evaluator."""

    @pytest.fixture
    def sample_metric(self):
        """Sample metric for testing."""
        return Metric(
            timestamp=datetime.utcnow(),
            database_type="postgresql",
            instance_id="prod-db-01",
            metric_name="cpu_usage_percent",
            value=95.0,
            tags={"environment": "production"}
        )

    def test_threshold_rule_evaluation(self, sample_metric):
        """Test threshold rule evaluation."""
        rule = ThresholdRule(
            metric_name="cpu_usage_percent",
            operator=">",
            threshold=80,
            severity=AlertSeverity.WARNING
        )

        evaluator = AlertEvaluator([rule])
        alerts = evaluator.evaluate_metrics([sample_metric])

        assert len(alerts) == 1
        assert alerts[0].severity == AlertSeverity.WARNING

    def test_alert_deduplication(self, sample_metric):
        """Test alert deduplication logic."""
        rule = ThresholdRule(
            metric_name="cpu_usage_percent",
            operator=">",
            threshold=80,
            severity=AlertSeverity.WARNING
        )

        evaluator = AlertEvaluator([rule])

        # First evaluation should create alert
        alerts1 = evaluator.evaluate_metrics([sample_metric])
        assert len(alerts1) == 1

        # Second evaluation within cooldown should not create duplicate
        alerts2 = evaluator.evaluate_metrics([sample_metric])
        assert len(alerts2) == 0

class TestCircuitBreaker:
    """Unit tests for circuit breaker."""

    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_after_failures(self):
        """Test circuit breaker opens after threshold failures."""
        breaker = CircuitBreaker(failure_threshold=3, timeout=60)

        failing_func = AsyncMock(side_effect=Exception("Service unavailable"))

        # Fail 3 times to trip circuit
        for i in range(3):
            with pytest.raises(Exception):
                await breaker.call(failing_func)

        assert breaker.state == CircuitState.OPEN

        # Next call should fail fast without calling function
        with pytest.raises(CircuitOpenError):
            await breaker.call(failing_func)

    @pytest.mark.asyncio
    async def test_circuit_breaker_half_open_recovery(self):
        """Test circuit breaker recovery through HALF_OPEN state."""
        breaker = CircuitBreaker(failure_threshold=2, timeout=1, success_threshold=2)

        # Trip circuit
        failing_func = AsyncMock(side_effect=Exception("Error"))
        for i in range(2):
            with pytest.raises(Exception):
                await breaker.call(failing_func)

        assert breaker.state == CircuitState.OPEN

        # Wait for timeout
        await asyncio.sleep(1.1)

        # Success should transition to HALF_OPEN then CLOSED
        success_func = AsyncMock(return_value="success")
        await breaker.call(success_func)
        assert breaker.state == CircuitState.HALF_OPEN

        await breaker.call(success_func)
        assert breaker.state == CircuitState.CLOSED
```

#### Integration Testing

```python
import pytest
from testcontainers.kafka import KafkaContainer
from testcontainers.postgres import PostgresContainer
import asyncio

class TestMonitoringIntegration:
    """Integration tests with real dependencies."""

    @pytest.fixture(scope="class")
    def kafka_container(self):
        """Start Kafka container for testing."""
        with KafkaContainer() as kafka:
            yield kafka

    @pytest.fixture(scope="class")
    def postgres_container(self):
        """Start PostgreSQL container for testing."""
        with PostgresContainer("postgres:14") as postgres:
            yield postgres

    @pytest.mark.asyncio
    async def test_end_to_end_metric_flow(
        self,
        kafka_container,
        postgres_container
    ):
        """Test complete metric flow from collection to Kafka."""
        # Set up collector
        collector_config = {
            "host": postgres_container.get_container_host_ip(),
            "port": postgres_container.get_exposed_port(5432),
            "user": "test",
            "password": "test",
            "database": "test"
        }

        collector = PostgreSQLCollector(collector_config)
        await collector.initialize()

        # Set up Kafka output
        kafka_config = {
            "bootstrap_servers": kafka_container.get_bootstrap_server(),
        }
        output = KafkaOutput(kafka_config)

        # Collect and publish metrics
        metrics = await collector.collect()
        await output.send(metrics)

        # Verify metrics in Kafka
        consumer = KafkaConsumer(
            bootstrap_servers=kafka_container.get_bootstrap_server(),
            auto_offset_reset='earliest'
        )
        consumer.subscribe(['gds.metrics.postgresql.test'])

        messages = []
        for msg in consumer:
            messages.append(msg)
            if len(messages) >= len(metrics):
                break

        assert len(messages) == len(metrics)
        consumer.close()

#### Performance Testing

```python
import pytest
import asyncio
import time
from locust import User, task, between

class PerformanceTests:
    """Performance and load testing."""

    @pytest.mark.asyncio
    async def test_collector_throughput(self):
        """Test metric collection throughput."""
        collector = PostgreSQLCollector(config)
        await collector.initialize()

        start = time.time()
        iterations = 100
        total_metrics = 0

        for i in range(iterations):
            metrics = await collector.collect()
            total_metrics += len(metrics)

        duration = time.time() - start
        throughput = total_metrics / duration

        # Assert minimum throughput
        assert throughput >= 1000, f"Throughput too low: {throughput} metrics/sec"

    @pytest.mark.asyncio
    async def test_alert_evaluation_latency(self):
        """Test alert evaluation latency."""
        evaluator = AlertEvaluator(rules=[
            ThresholdRule("cpu_usage", ">", 80, AlertSeverity.WARNING)
            for _ in range(100)
        ])

        metrics = [
            Metric(metric_name="cpu_usage", value=85.0)
            for _ in range(1000)
        ]

        start = time.time()
        alerts = evaluator.evaluate_metrics(metrics)
        duration = time.time() - start

        # Assert p95 latency requirement
        assert duration < 1.0, f"Evaluation too slow: {duration}s"

class MonitoringLoadTest(User):
    """Locust load test for monitoring system."""

    wait_time = between(1, 5)

    @task
    def collect_and_publish_metrics(self):
        """Simulate metric collection and publishing."""
        # Implementation for load testing
        pass
```

### Configuration Management

```python
from dataclasses import dataclass, asdict
import yaml
import json
from typing import Dict, Any
import os
from pathlib import Path

@dataclass
class DatabaseConfig:
    """Database connection configuration."""
    host: str
    port: int
    user: str
    password: str
    database: str
    type: str  # postgresql, mongodb, mssql

    @classmethod
    def from_dict(cls, data: dict):
        """Create from dictionary."""
        return cls(**data)

@dataclass
class KafkaConfig:
    """Kafka configuration."""
    bootstrap_servers: str
    security_protocol: str
    sasl_mechanism: str
    topic_prefix: str

    @classmethod
    def from_dict(cls, data: dict):
        """Create from dictionary."""
        return cls(**data)

@dataclass
class MonitoringConfig:
    """Complete monitoring system configuration."""
    environment: str
    databases: Dict[str, DatabaseConfig]
    kafka: KafkaConfig
    alert_rules: list
    collection_interval: int = 60

    @classmethod
    def from_yaml(cls, file_path: str):
        """Load configuration from YAML file."""
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)

        # Parse nested configs
        databases = {
            name: DatabaseConfig.from_dict(db_config)
            for name, db_config in data['databases'].items()
        }
        kafka = KafkaConfig.from_dict(data['kafka'])

        return cls(
            environment=data['environment'],
            databases=databases,
            kafka=kafka,
            alert_rules=data['alert_rules'],
            collection_interval=data.get('collection_interval', 60)
        )

    def validate(self):
        """Validate configuration."""
        assert self.environment in ['production', 'staging', 'development']
        assert len(self.databases) > 0, "No databases configured"
        assert self.kafka.bootstrap_servers, "Kafka bootstrap servers required"
        assert self.collection_interval > 0, "Collection interval must be positive"

class ConfigurationManager:
    """Manage configuration with hot reload support."""

    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.config: MonitoringConfig = None
        self.last_modified = 0
        self.callbacks = []

    def load(self):
        """Load configuration from file."""
        self.config = MonitoringConfig.from_yaml(self.config_path)
        self.config.validate()
        self.last_modified = self.config_path.stat().st_mtime
        logger.info(f"Configuration loaded from {self.config_path}")
        return self.config

    def register_reload_callback(self, callback):
        """Register callback for configuration reloads."""
        self.callbacks.append(callback)

    async def watch_for_changes(self):
        """Watch for configuration file changes and reload."""
        while True:
            await asyncio.sleep(5)  # Check every 5 seconds

            current_mtime = self.config_path.stat().st_mtime
            if current_mtime > self.last_modified:
                logger.info("Configuration file changed, reloading...")
                try:
                    old_config = self.config
                    self.load()

                    # Notify callbacks
                    for callback in self.callbacks:
                        await callback(old_config, self.config)

                except Exception as e:
                    logger.error(f"Failed to reload configuration: {e}")

# Example configuration file (config.yaml)
"""
environment: production

databases:
  prod-db-01:
    type: postgresql
    host: prod-db-01.example.com
    port: 5432
    user: monitoring
    password: ${DB_PASSWORD}  # From environment variable
    database: postgres

  prod-mongo-01:
    type: mongodb
    host: prod-mongo-01.example.com
    port: 27017
    user: monitoring
    password: ${MONGO_PASSWORD}
    database: admin

kafka:
  bootstrap_servers: kafka-1:9092,kafka-2:9092,kafka-3:9092
  security_protocol: SASL_SSL
  sasl_mechanism: PLAIN
  topic_prefix: gds.metrics

collection_interval: 60

alert_rules:
  - name: high_cpu_usage
    metric: cpu_usage_percent
    operator: ">"
    threshold: 80
    severity: WARNING
    cooldown_minutes: 15

  - name: critical_cpu_usage
    metric: cpu_usage_percent
    operator: ">"
    threshold: 95
    severity: CRITICAL
    cooldown_minutes: 5
"""
```

### Metric Sampling and Downsampling

```python
from dataclasses import dataclass
from typing import List
import random

class MetricSampler:
    """Sample high-frequency metrics to reduce volume."""

    def __init__(self, sample_rate: float = 0.1):
        """
        Args:
            sample_rate: Fraction of metrics to keep (0.0 to 1.0)
        """
        assert 0 <= sample_rate <= 1.0
        self.sample_rate = sample_rate

    def should_sample(self, metric: Metric) -> bool:
        """Determine if metric should be sampled (kept)."""
        # Always keep critical metrics
        if self._is_critical_metric(metric):
            return True

        # Sample others based on rate
        return random.random() < self.sample_rate

    def _is_critical_metric(self, metric: Metric) -> bool:
        """Check if metric is critical and should never be dropped."""
        critical_patterns = [
            'error_rate',
            'availability',
            'critical_alert'
        ]
        return any(pattern in metric.metric_name for pattern in critical_patterns)

    async def sample_metrics(self, metrics: List[Metric]) -> List[Metric]:
        """Sample metrics and add sampling metadata."""
        sampled = []

        for metric in metrics:
            if self.should_sample(metric):
                # Add sampling metadata
                if metric.metadata is None:
                    metric.metadata = {}
                metric.metadata['sampled'] = True
                metric.metadata['sample_rate'] = self.sample_rate
                sampled.append(metric)

        return sampled

class MetricDownsampler:
    """Downsample historical metrics to reduce storage."""

    def __init__(self):
        self.downsampling_rules = {
            # Keep 1-minute resolution for 7 days
            "1min": {"duration_days": 7, "resolution_seconds": 60},
            # Keep 5-minute resolution for 30 days
            "5min": {"duration_days": 30, "resolution_seconds": 300},
            # Keep 1-hour resolution for 90 days
            "1hour": {"duration_days": 90, "resolution_seconds": 3600},
            # Keep 1-day resolution forever
            "1day": {"duration_days": None, "resolution_seconds": 86400},
        }

    async def downsample_metrics(
        self,
        metrics: List[Metric],
        target_resolution_seconds: int
    ) -> List[Metric]:
        """Downsample metrics to target resolution."""
        # Group metrics by time bucket and tags
        groups = {}

        for metric in metrics:
            # Calculate time bucket
            bucket_timestamp = int(metric.timestamp.timestamp() // target_resolution_seconds) * target_resolution_seconds

            # Group key
            group_key = (
                metric.metric_name,
                bucket_timestamp,
                frozenset(metric.tags.items()) if metric.tags else frozenset()
            )

            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(metric)

        # Aggregate each group
        downsampled = []
        for (metric_name, bucket_ts, tags), group_metrics in groups.items():
            downsampled.append(self._aggregate_group(
                metric_name,
                group_metrics,
                datetime.fromtimestamp(bucket_ts, tz=timezone.utc),
                dict(tags)
            ))

        return downsampled

    def _aggregate_group(
        self,
        metric_name: str,
        metrics: List[Metric],
        bucket_time: datetime,
        tags: dict
    ) -> Metric:
        """Aggregate group of metrics with statistics."""
        values = [m.value for m in metrics]

        return Metric(
            timestamp=bucket_time,
            metric_name=metric_name,
            value=sum(values) / len(values),  # Average
            tags=tags,
            metadata={
                "downsampled": True,
                "original_count": len(metrics),
                "min": min(values),
                "max": max(values),
                "p50": sorted(values)[len(values)//2],
                "p95": sorted(values)[int(len(values)*0.95)]
            }
        )
```

## Implementation Roadmap

### Phase 1: Core Infrastructure (Week 1-2)

1. Create package structures and basic scaffolding
2. Implement abstract base classes and interfaces
3. Define core data structures (Metric, Alert, etc.)
4. Set up basic configuration management

### Phase 2: Monitoring System (Week 3-4)

1. Implement metric collectors for each database type
2. Create Kafka output handler with topic partitioning strategy
3. Build monitoring scheduler with configurable intervals
4. Add comprehensive error handling and logging
5. Implement metric serialization and schema validation

### Phase 3: Alerting System (Week 5-6)

1. Implement alert rules and evaluation engine
2. Create notification service API client and notifier
3. Add alert escalation policies
4. Implement alert lifecycle management (creation, resolution, history)
5. Add fallback notification options

### Phase 4: Integration and Testing (Week 7-8)

1. Integrate monitoring and alerting systems
2. Add comprehensive unit and integration tests
3. Create example configurations and usage documentation
4. Performance testing and optimization

### Phase 5: Advanced Features (Week 9-10)

1. Add anomaly detection capabilities
2. Implement alert correlation and deduplication
3. Add dashboard integration
4. Create monitoring dashboards and visualizations

---

## Best Practices

### Monitoring Best Practices

1. **Monitor Symptoms, Not Causes**: Alert on user-visible issues
2. **Use Appropriate Intervals**: Balance timeliness with resource usage
3. **Include Context**: Provide actionable information in alerts
4. **Handle Failures Gracefully**: Continue monitoring even if some checks fail

### Alerting Best Practices

1. **Alert Liberally, Page Judiciously**: Log issues, page only on urgent problems
2. **Define Clear Escalation Paths**: Different severities have different responses
3. **Avoid Alert Fatigue**: Use appropriate thresholds and cooldown periods
4. **Test Alerting**: Regularly test that alerts work and reach the right people

#### SLO-Driven Alerting

- Define SLIs and SLOs per service/database (e.g., availability, latency, error rate) and tie paging alerts to SLO burn rates
- Use the Four Golden Signals (latency, traffic, errors, saturation) and RED/USE methods to guide metric selection

#### Alert Hygiene and Lifecycle

- Use a deterministic deduplication key (rule_id + resource + metric) to avoid flapping
- Group related alerts and provide correlation IDs to reduce noise
- Implement alert states: open → acknowledged → resolved; auto-resolve on recovery
- Provide actionable context in every alert: impact, suspected cause, runbook URL, dashboard links, owner/on-call
- Support silences/maintenance windows and inhibition rules to prevent cascaded paging

#### Routing and Escalation

- Route by severity, service, environment to the right channel (email, Slack, PagerDuty)
- Rate-limit notifications per rule/resource to avoid storms, with exponential backoff and jitter
- Escalate on lack of acknowledgement within defined time windows

### OOP Best Practices

1. **Composition over Inheritance**: Favor composition for flexibility
2. **Dependency Injection**: Inject dependencies rather than creating them
3. **Interface Segregation**: Keep interfaces focused and minimal
4. **Single Responsibility**: Each class should have one reason to change

### Kafka-Specific Best Practices

1. **Topic Naming**: Use hierarchical naming with environment and database type
2. **Partitioning**: Partition by database instance for ordered processing
3. **Message Size**: Keep messages small and focused on individual metrics
4. **Schema Evolution**: Use schema registry for metric format evolution
5. **Consumer Groups**: Use separate groups for different processing needs
6. **Retention**: Configure appropriate retention based on alerting windows
7. **Monitoring**: Monitor Kafka lag, throughput, and error rates
8. **Backpressure & Retries**: Use consumer max-poll intervals and bounded retries; push unrecoverable messages to DLQ and alert on DLQ growth
9. **Idempotency**: Ensure downstream consumers handle at-least-once delivery semantics via idempotent writes keyed by metric identity and timestamp bucket

### Security Considerations

1. **Credential Management**: Secure storage of database credentials
2. **Access Control**: Limit monitoring access to necessary systems
3. **Audit Logging**: Log all monitoring and alerting activities
4. **Encryption**: Encrypt sensitive data in transit and at rest
5. **Transport Security**: Use TLS for Kafka (SASL_SSL), mTLS for service-to-service, and HTTPS for APIs
6. **AuthN/Z**: Use short-lived tokens/approles for collectors; apply least privilege RBAC on topics and APIs
7. **Secrets Management**: Store credentials in Vault (with rotation) and avoid secrets in config files or logs
8. **PII/Data Minimization**: Avoid including PII in metrics/alerts; scrub sensitive fields before publishing
9. **Compliance & Retention**: Apply environment-specific retention policies and audit trails; document data lineage

### Operability and Resilience

1. **Dead Man's Switch**: Emit periodic heartbeats and alert if metrics/alerts stop arriving (per collector and per topic)
2. **Health Checks**: Liveness/readiness for collectors, alerting consumers, and the notification service; include dependency checks
3. **Capacity Planning**: Track queue/topic lag, throughput, and saturation; alert before breaching SLOs
4. **Failure Modes**: Implement bounded in-memory buffers with backpressure; retry with exponential backoff; fall back to local spool if Kafka unavailable
5. **Change Safety**: Feature flags for new rules/collectors; canary deployments; automatic rollback on error budgets burned
6. **Runbooks**: Maintain concise runbooks for top alerts with verification steps and roll-forward/rollback procedures

---

## Advanced Operational Sections

### Database Connection Management

#### Connection Pool Configuration

```python
from sqlalchemy import create_engine, pool
import asyncpg
from motor import motor_asyncio

class DatabaseConnectionManager:
    """Manage database connections with pooling and retry logic."""

    def __init__(self, db_config: dict):
        self.db_config = db_config
        self.db_type = db_config['type']
        self.pool = None
        self.circuit_breaker = CircuitBreaker(failure_threshold=3, timeout=60)

    async def initialize(self):
        """Initialize connection pool."""
        if self.db_type == 'postgresql':
            await self._init_postgres_pool()
        elif self.db_type == 'mongodb':
            await self._init_mongo_pool()
        elif self.db_type == 'mssql':
            await self._init_mssql_pool()

    async def _init_postgres_pool(self):
        """Initialize PostgreSQL connection pool."""
        self.pool = await asyncpg.create_pool(
            host=self.db_config['host'],
            port=self.db_config['port'],
            user=self.db_config['user'],
            password=self.db_config['password'],
            database=self.db_config['database'],

            # Pool sizing
            min_size=2,  # Minimum connections
            max_size=10,  # Maximum connections

            # Timeouts
            command_timeout=30,  # Query timeout in seconds
            timeout=10,  # Connection acquisition timeout

            # Connection management
            max_inactive_connection_lifetime=300,  # 5 minutes
            max_cached_statement_lifetime=300,  # 5 minutes

            # Retry settings
            connection_class=asyncpg.Connection,
        )
        logger.info(f"PostgreSQL pool initialized: {self.pool.get_size()} connections")

    async def _init_mongo_pool(self):
        """Initialize MongoDB connection pool."""
        from pymongo import MongoClient

        connection_string = f"mongodb://{self.db_config['user']}:{self.db_config['password']}@{self.db_config['host']}:{self.db_config['port']}"

        self.pool = motor_asyncio.AsyncIOMotorClient(
            connection_string,
            maxPoolSize=10,
            minPoolSize=2,
            maxIdleTimeMS=300000,  # 5 minutes
            serverSelectionTimeoutMS=10000,  # 10 seconds
            socketTimeoutMS=30000,  # 30 seconds
            connectTimeoutMS=10000,  # 10 seconds
            retryWrites=True,
            retryReads=True
        )

    async def _init_mssql_pool(self):
        """Initialize SQL Server connection pool with SQLAlchemy."""
        connection_string = (
            f"mssql+pyodbc://{self.db_config['user']}:{self.db_config['password']}"
            f"@{self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}"
            f"?driver=ODBC+Driver+17+for+SQL+Server"
        )

        self.pool = create_engine(
            connection_string,
            poolclass=pool.QueuePool,
            pool_size=10,
            max_overflow=5,
            pool_timeout=10,
            pool_recycle=3600,  # Recycle connections after 1 hour
            pool_pre_ping=True,  # Verify connections before using
            echo=False
        )

    async def execute_query_with_retry(
        self,
        query: str,
        params: dict = None,
        max_retries: int = 3
    ):
        """Execute query with exponential backoff retry."""
        for attempt in range(max_retries):
            try:
                return await self.circuit_breaker.call(
                    self._execute_query,
                    query,
                    params
                )
            except CircuitOpenError:
                logger.error("Circuit breaker is open, database unavailable")
                raise
            except Exception as e:
                wait_time = min(2 ** attempt, 30)  # Max 30 seconds
                logger.warning(
                    f"Query failed (attempt {attempt + 1}/{max_retries}): {e}. "
                    f"Retrying in {wait_time}s..."
                )
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(wait_time)

    async def _execute_query(self, query: str, params: dict = None):
        """Internal query execution."""
        if self.db_type == 'postgresql':
            async with self.pool.acquire() as conn:
                return await conn.fetch(query, **(params or {}))
        elif self.db_type == 'mongodb':
            # MongoDB query execution
            db = self.pool[self.db_config['database']]
            collection = db[params.get('collection', 'default')]
            return await collection.find(query).to_list(length=100)

    async def health_check(self) -> bool:
        """Perform health check on database connection."""
        try:
            if self.db_type == 'postgresql':
                async with self.pool.acquire() as conn:
                    await conn.fetchval('SELECT 1')
            elif self.db_type == 'mongodb':
                await self.pool.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

    async def close(self):
        """Close connection pool gracefully."""
        if self.pool:
            if self.db_type == 'postgresql':
                await self.pool.close()
            elif self.db_type == 'mongodb':
                self.pool.close()
            logger.info("Database connection pool closed")
```

#### Maintenance Window Handling

```python
class MaintenanceWindowManager:
    """Handle database maintenance windows to avoid false alerts."""

    def __init__(self, redis_client):
        self.redis = redis_client

    async def is_in_maintenance(self, instance_id: str) -> bool:
        """Check if database instance is in maintenance window."""
        key = f"maintenance:{instance_id}"
        return await self.redis.exists(key)

    async def set_maintenance_window(
        self,
        instance_id: str,
        duration_minutes: int,
        reason: str = ""
    ):
        """Set maintenance window for an instance."""
        key = f"maintenance:{instance_id}"
        metadata = {
            "reason": reason,
            "started_at": datetime.utcnow().isoformat(),
            "duration_minutes": duration_minutes
        }
        await self.redis.setex(
            key,
            duration_minutes * 60,
            json.dumps(metadata)
        )
        logger.info(f"Maintenance window set for {instance_id}: {duration_minutes} minutes")
```

### Time Synchronization and Clock Skew Handling

#### Time Management Best Practices

```python
from datetime import datetime, timezone
import time

class TimeManager:
    """Manage timestamps and handle clock skew."""

    # Always use UTC
    @staticmethod
    def now_utc() -> datetime:
        """Get current time in UTC."""
        return datetime.now(timezone.utc)

    @staticmethod
    def to_utc(dt: datetime) -> datetime:
        """Convert datetime to UTC."""
        if dt.tzinfo is None:
            # Assume UTC if naive
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    @staticmethod
    def detect_clock_skew(
        metric_timestamp: datetime,
        max_drift_seconds: int = 300
    ) -> bool:
        """Detect if metric timestamp indicates clock skew."""
        now = TimeManager.now_utc()
        metric_utc = TimeManager.to_utc(metric_timestamp)

        drift = abs((now - metric_utc).total_seconds())

        if drift > max_drift_seconds:
            logger.warning(
                f"Clock skew detected: {drift:.0f}s drift. "
                f"Metric timestamp: {metric_utc}, System time: {now}"
            )
            return True
        return False

    @staticmethod
    def handle_late_arriving_metrics(
        metric: Metric,
        max_lateness_seconds: int = 3600
    ) -> bool:
        """Determine if late-arriving metric should be processed."""
        now = TimeManager.now_utc()
        metric_time = TimeManager.to_utc(metric.timestamp)
        lateness = (now - metric_time).total_seconds()

        if lateness > max_lateness_seconds:
            logger.warning(
                f"Metric too late ({lateness:.0f}s old), discarding. "
                f"Metric: {metric.metric_name} from {metric.instance_id}"
            )
            return False

        if lateness > 300:  # 5 minutes
            logger.info(f"Processing late metric ({lateness:.0f}s old)")

        return True

class MetricCollectorWithTimeHandling(MetricCollector):
    """Collector with proper time handling."""

    async def collect(self) -> List[Metric]:
        """Collect metrics with collector timestamp."""
        collection_start = TimeManager.now_utc()

        # Query database for metrics
        db_metrics = await self._query_database()

        metrics = []
        for db_metric in db_metrics:
            # Use database server time if available, else collector time
            metric_timestamp = db_metric.get('server_time') or collection_start

            # Detect clock skew
            if TimeManager.detect_clock_skew(metric_timestamp):
                # Use collector time instead if skew detected
                metric_timestamp = collection_start

            metric = Metric(
                timestamp=metric_timestamp,
                collection_timestamp=collection_start,  # Track collection time
                # ... other fields
            )

            # Check if metric is too old
            if TimeManager.handle_late_arriving_metrics(metric):
                metrics.append(metric)

        return metrics
```

#### Handling Event Time vs Processing Time

```python
@dataclass
class Metric:
    """Metric with event time and processing time."""
    # Event time: when metric was generated at source
    timestamp: datetime

    # Processing time: when metric was collected
    collection_timestamp: datetime

    # Ingestion time: when metric entered Kafka
    ingestion_timestamp: Optional[datetime] = None

    # Processing latency tracking
    @property
    def collection_latency_ms(self) -> float:
        """Latency between event and collection."""
        return (self.collection_timestamp - self.timestamp).total_seconds() * 1000

    @property
    def ingestion_latency_ms(self) -> float:
        """Latency between collection and ingestion."""
        if self.ingestion_timestamp:
            return (self.ingestion_timestamp - self.collection_timestamp).total_seconds() * 1000
        return 0
```

### Metric Cardinality Management

#### Cardinality Tracking and Limits

```python
class CardinalityManager:
    """Manage and limit metric cardinality to prevent explosion."""

    def __init__(self, redis_client):
        self.redis = redis_client
        self.cardinality_limits = {
            'default': 1000,
            'high_cardinality': 10000,
            'unlimited': None
        }
        self.cardinality_window = 3600  # 1 hour window

    async def check_cardinality(
        self,
        metric_name: str,
        tag_combination: str,
        limit_profile: str = 'default'
    ) -> bool:
        """Check if adding this metric would exceed cardinality limit."""
        key = f"cardinality:{metric_name}:{self.cardinality_window}"

        # Track unique tag combinations
        current_cardinality = await self.redis.pfcount(key)
        limit = self.cardinality_limits.get(limit_profile)

        if limit and current_cardinality >= limit:
            logger.warning(
                f"Cardinality limit reached for {metric_name}: "
                f"{current_cardinality} >= {limit}"
            )
            # Emit metric about cardinality violation
            emit_metric("cardinality.limit_exceeded", {
                "metric_name": metric_name,
                "current": current_cardinality,
                "limit": limit
            })
            return False

        # Add to HyperLogLog for tracking
        await self.redis.pfadd(key, tag_combination)
        await self.redis.expire(key, self.cardinality_window)

        return True

    async def get_cardinality_report(self) -> Dict[str, int]:
        """Get cardinality report for all metrics."""
        pattern = "cardinality:*"
        keys = await self.redis.keys(pattern)

        report = {}
        for key in keys:
            metric_name = key.split(':')[1]
            cardinality = await self.redis.pfcount(key)
            report[metric_name] = cardinality

        return report

class TagValidator:
    """Validate and sanitize metric tags to prevent cardinality explosion."""

    ALLOWED_TAG_KEYS = {
        'instance_id', 'database_type', 'environment',
        'region', 'availability_zone', 'cluster_id'
    }

    TAG_VALUE_PATTERNS = {
        'instance_id': r'^[a-zA-Z0-9\-_]+$',
        'environment': r'^(production|staging|development|test)$',
        'region': r'^[a-z]{2}-[a-z]+-\d+$'
    }

    @classmethod
    def validate_tags(cls, tags: Dict[str, str]) -> Dict[str, str]:
        """Validate and sanitize tags."""
        validated = {}

        for key, value in tags.items():
            # Check if tag key is allowed
            if key not in cls.ALLOWED_TAG_KEYS:
                logger.warning(f"Dropping disallowed tag: {key}")
                continue

            # Validate tag value pattern
            pattern = cls.TAG_VALUE_PATTERNS.get(key)
            if pattern and not re.match(pattern, value):
                logger.warning(f"Invalid tag value for {key}: {value}")
                continue

            # Limit tag value length
            if len(value) > 128:
                value = value[:128]
                logger.warning(f"Truncating long tag value for {key}")

            validated[key] = value

        return validated

# Usage in collector
class MetricCollectorWithCardinalityControl(MetricCollector):
    """Collector with cardinality management."""

    def __init__(self, config, cardinality_manager: CardinalityManager):
        super().__init__(config)
        self.cardinality_manager = cardinality_manager

    async def collect(self) -> List[Metric]:
        """Collect metrics with cardinality control."""
        raw_metrics = await self._query_database()

        filtered_metrics = []
        for metric_data in raw_metrics:
            # Validate and sanitize tags
            tags = TagValidator.validate_tags(metric_data.get('tags', {}))

            # Check cardinality
            tag_combination = json.dumps(tags, sort_keys=True)
            if await self.cardinality_manager.check_cardinality(
                metric_data['metric_name'],
                tag_combination
            ):
                metric = Metric(
                    metric_name=metric_data['metric_name'],
                    value=metric_data['value'],
                    tags=tags,
                    # ... other fields
                )
                filtered_metrics.append(metric)

        return filtered_metrics
```

#### Aggregation for High-Cardinality Metrics

```python
class MetricAggregator:
    """Aggregate high-cardinality metrics to reduce volume."""

    def __init__(self, aggregation_window: int = 60):
        self.aggregation_window = aggregation_window  # seconds
        self.buffers: Dict[str, List[Metric]] = {}

    def should_aggregate(self, metric_name: str) -> bool:
        """Determine if metric should be aggregated."""
        high_cardinality_patterns = [
            r'.*\.per_user\..*',
            r'.*\.per_session\..*',
            r'.*\.per_request\..*'
        ]
        return any(re.match(pattern, metric_name) for pattern in high_cardinality_patterns)

    async def aggregate_metrics(
        self,
        metrics: List[Metric]
    ) -> List[Metric]:
        """Aggregate metrics by time window and tag combination."""
        aggregated = []

        # Group by metric name and tags (excluding high-cardinality tags)
        groups = {}
        for metric in metrics:
            # Remove high-cardinality tags
            agg_tags = {
                k: v for k, v in metric.tags.items()
                if k not in ['user_id', 'session_id', 'request_id']
            }

            key = (metric.metric_name, json.dumps(agg_tags, sort_keys=True))
            if key not in groups:
                groups[key] = []
            groups[key].append(metric)

        # Aggregate each group
        for (metric_name, tags_json), metric_list in groups.items():
            tags = json.loads(tags_json)
            values = [m.value for m in metric_list]

            # Create aggregated metric with statistics
            aggregated.append(Metric(
                metric_name=f"{metric_name}.count",
                value=len(values),
                tags=tags,
                timestamp=metric_list[0].timestamp
            ))
            aggregated.append(Metric(
                metric_name=f"{metric_name}.avg",
                value=sum(values) / len(values),
                tags=tags,
                timestamp=metric_list[0].timestamp
            ))
            aggregated.append(Metric(
                metric_name=f"{metric_name}.max",
                value=max(values),
                tags=tags,
                timestamp=metric_list[0].timestamp
            ))
            aggregated.append(Metric(
                metric_name=f"{metric_name}.min",
                value=min(values),
                tags=tags,
                timestamp=metric_list[0].timestamp
            ))

        return aggregated
```

### Meta-Monitoring and Dead Man's Switch

#### Monitoring the Monitoring System

```python
class MetaMonitor:
    """Monitor the health of the monitoring system itself."""

    def __init__(self, redis_client, alert_notifier):
        self.redis = redis_client
        self.alert_notifier = alert_notifier
        self.heartbeat_interval = 60  # seconds
        self.heartbeat_timeout = 180  # 3 minutes without heartbeat triggers alert

    async def emit_heartbeat(self, component_name: str, metadata: dict = None):
        """Emit heartbeat from monitoring component."""
        key = f"heartbeat:{component_name}"
        heartbeat_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "component": component_name,
            "status": "healthy",
            "metadata": metadata or {}
        }

        # Store with expiration
        await self.redis.setex(
            key,
            self.heartbeat_timeout,
            json.dumps(heartbeat_data)
        )

        # Also emit as metric
        emit_metric("monitoring.heartbeat", {
            "component": component_name,
            "status": "healthy"
        })

    async def check_heartbeats(self):
        """Check all expected heartbeats and alert if missing."""
        expected_components = [
            'telemetry_collector_postgresql',
            'telemetry_collector_mongodb',
            'telemetry_collector_mssql',
            'alert_evaluation_consumer_1',
            'alert_evaluation_consumer_2',
            'kafka_producer',
        ]

        missing_heartbeats = []
        for component in expected_components:
            key = f"heartbeat:{component}"
            exists = await self.redis.exists(key)

            if not exists:
                missing_heartbeats.append(component)
                logger.error(f"Missing heartbeat from {component}")

                # Send alert
                alert = Alert(
                    id=str(uuid.uuid4()),
                    rule_id="meta_monitoring_heartbeat_missing",
                    severity=AlertSeverity.CRITICAL,
                    message=f"Monitoring component {component} stopped sending heartbeats",
                    metric=None,
                    timestamp=datetime.utcnow(),
                    labels={
                        "component": component,
                        "alert_type": "meta_monitoring"
                    }
                )
                await self.alert_notifier.notify(alert)

        return missing_heartbeats

class DeadMansSwitch:
    """Ensure metrics are flowing through the pipeline."""

    def __init__(self, redis_client, alert_notifier):
        self.redis = redis_client
        self.alert_notifier = alert_notifier
        self.metric_timeout = 300  # 5 minutes

    async def record_metric_arrival(
        self,
        topic: str,
        partition: int,
        instance_id: str
    ):
        """Record that a metric arrived for this instance."""
        key = f"metric_arrival:{topic}:{partition}:{instance_id}"
        await self.redis.setex(key, self.metric_timeout, datetime.utcnow().isoformat())

    async def check_metric_flow(self):
        """Check that metrics are flowing from all expected sources."""
        # Get all expected metric sources
        expected_sources = await self._get_expected_sources()

        missing_metrics = []
        for source in expected_sources:
            key = f"metric_arrival:{source['topic']}:{source['partition']}:{source['instance_id']}"
            exists = await self.redis.exists(key)

            if not exists:
                missing_metrics.append(source)
                logger.error(f"No metrics received from {source['instance_id']} in last {self.metric_timeout}s")

                # Alert on missing metrics
                alert = Alert(
                    id=str(uuid.uuid4()),
                    rule_id="dead_mans_switch_no_metrics",
                    severity=AlertSeverity.CRITICAL,
                    message=f"No metrics received from {source['instance_id']}",
                    metric=None,
                    timestamp=datetime.utcnow(),
                    labels={
                        "instance_id": source['instance_id'],
                        "topic": source['topic'],
                        "alert_type": "absence_detection"
                    }
                )
                await self.alert_notifier.notify(alert)

        return missing_metrics

    async def _get_expected_sources(self) -> List[dict]:
        """Get list of expected metric sources from configuration."""
        # In production: load from database or configuration
        return [
            {"topic": "gds.metrics.postgresql.production", "partition": 0, "instance_id": "prod-db-01"},
            {"topic": "gds.metrics.mongodb.production", "partition": 0, "instance_id": "prod-mongo-01"},
        ]
```

#### Kafka Lag Monitoring

```python
class KafkaLagMonitor:
    """Monitor Kafka consumer lag to detect processing issues."""

    def __init__(self, kafka_admin_client, alert_notifier):
        self.admin_client = kafka_admin_client
        self.alert_notifier = alert_notifier
        self.lag_warning_threshold = 1000  # messages
        self.lag_critical_threshold = 10000  # messages

    async def check_consumer_lag(self, consumer_group: str):
        """Check lag for consumer group."""
        from kafka import TopicPartition

        # Get consumer group offsets
        group_offsets = await self._get_group_offsets(consumer_group)

        # Get topic end offsets
        end_offsets = await self._get_end_offsets(group_offsets.keys())

        lag_by_partition = {}
        total_lag = 0

        for partition, committed_offset in group_offsets.items():
            end_offset = end_offsets.get(partition, 0)
            lag = end_offset - committed_offset
            lag_by_partition[partition] = lag
            total_lag += lag

            # Alert on high lag
            if lag >= self.lag_critical_threshold:
                await self._alert_high_lag(consumer_group, partition, lag, "CRITICAL")
            elif lag >= self.lag_warning_threshold:
                await self._alert_high_lag(consumer_group, partition, lag, "WARNING")

        # Emit lag metrics
        emit_metric("kafka.consumer.lag", {
            "consumer_group": consumer_group,
            "total_lag": total_lag,
            "max_partition_lag": max(lag_by_partition.values()) if lag_by_partition else 0
        })

        return total_lag

    async def _alert_high_lag(
        self,
        consumer_group: str,
        partition: TopicPartition,
        lag: int,
        severity: str
    ):
        """Alert on high consumer lag."""
        alert = Alert(
            id=str(uuid.uuid4()),
            rule_id="kafka_consumer_lag_high",
            severity=AlertSeverity[severity],
            message=f"High Kafka lag for {consumer_group}: {lag} messages behind",
            metric=None,
            timestamp=datetime.utcnow(),
            labels={
                "consumer_group": consumer_group,
                "topic": partition.topic,
                "partition": str(partition.partition),
                "lag": str(lag)
            }
        )
        await self.alert_notifier.notify(alert)
```

#### Alert Delivery Success Tracking

```python
class AlertDeliveryMonitor:
    """Monitor alert delivery success rates."""

    def __init__(self, redis_client):
        self.redis = redis_client
        self.window_size = 3600  # 1 hour window

    async def record_alert_attempt(self, alert_id: str, success: bool, notifier: str):
        """Record alert delivery attempt."""
        key = f"alert_delivery:{notifier}:{int(time.time() // self.window_size)}"

        # Increment counters
        if success:
            await self.redis.hincrby(key, "success", 1)
        else:
            await self.redis.hincrby(key, "failure", 1)

        await self.redis.expire(key, self.window_size * 2)

        # Emit metrics
        emit_metric("alert.delivery", {
            "notifier": notifier,
            "success": success
        })

    async def get_delivery_stats(self, notifier: str) -> dict:
        """Get alert delivery statistics."""
        key = f"alert_delivery:{notifier}:{int(time.time() // self.window_size)}"

        stats = await self.redis.hgetall(key)
        success = int(stats.get(b'success', 0))
        failure = int(stats.get(b'failure', 0))
        total = success + failure

        success_rate = (success / total * 100) if total > 0 else 100

        return {
            "success": success,
            "failure": failure,
            "total": total,
            "success_rate": success_rate
        }
```

### Alert Absence Detection

```python
class AlertAbsenceDetector:
    """Detect when expected alerts stop firing (indicating monitoring failure)."""

    def __init__(self, redis_client, alert_notifier):
        self.redis = redis_client
        self.alert_notifier = alert_notifier
        self.expected_alert_interval = {}  # rule_id -> expected interval in seconds

    def register_expected_alert(
        self,
        rule_id: str,
        expected_interval_seconds: int,
        tolerance_multiplier: float = 2.0
    ):
        """Register an alert that is expected to fire periodically."""
        self.expected_alert_interval[rule_id] = {
            "interval": expected_interval_seconds,
            "timeout": expected_interval_seconds * tolerance_multiplier
        }

    async def record_alert_fired(self, rule_id: str):
        """Record that an alert fired."""
        key = f"alert_last_fired:{rule_id}"
        await self.redis.set(key, datetime.utcnow().isoformat())
        await self.redis.expire(key, self.expected_alert_interval[rule_id]["timeout"])

    async def check_expected_alerts(self):
        """Check that expected alerts are firing."""
        missing_alerts = []

        for rule_id, config in self.expected_alert_interval.items():
            key = f"alert_last_fired:{rule_id}"
            last_fired = await self.redis.get(key)

            if not last_fired:
                # Alert never fired or timeout exceeded
                missing_alerts.append(rule_id)
                logger.error(f"Expected alert {rule_id} has not fired in {config['timeout']}s")

                # Meta-alert: expected alert is absent
                meta_alert = Alert(
                    id=str(uuid.uuid4()),
                    rule_id="meta_alert_absence_detected",
                    severity=AlertSeverity.CRITICAL,
                    message=f"Expected alert '{rule_id}' has stopped firing",
                    metric=None,
                    timestamp=datetime.utcnow(),
                    labels={
                        "missing_rule_id": rule_id,
                        "expected_interval": str(config['interval']),
                        "alert_type": "meta_monitoring"
                    },
                    runbook_url=f"https://runbook.example.com/alert-absence/{rule_id}"
                )
                await self.alert_notifier.notify(meta_alert)

        return missing_alerts

class MetricAbsenceDetector:
    """Detect when expected metrics stop arriving."""

    def __init__(self, redis_client, alert_notifier):
        self.redis = redis_client
        self.alert_notifier = alert_notifier

    async def record_metric_received(
        self,
        instance_id: str,
        metric_name: str,
        expected_interval_seconds: int
    ):
        """Record metric arrival and set expiration."""
        key = f"metric_last_seen:{instance_id}:{metric_name}"
        await self.redis.setex(
            key,
            expected_interval_seconds * 3,  # 3x tolerance
            datetime.utcnow().isoformat()
        )

    async def check_metric_absence(
        self,
        instance_id: str,
        metric_name: str
    ) -> bool:
        """Check if metric is absent (key expired)."""
        key = f"metric_last_seen:{instance_id}:{metric_name}"
        exists = await self.redis.exists(key)

        if not exists:
            logger.warning(f"Metric {metric_name} from {instance_id} is absent")

            # Alert on absence
            alert = Alert(
                id=str(uuid.uuid4()),
                rule_id="metric_absence_detected",
                severity=AlertSeverity.WARNING,
                message=f"Metric {metric_name} from {instance_id} has stopped arriving",
                metric=None,
                timestamp=datetime.utcnow(),
                labels={
                    "instance_id": instance_id,
                    "metric_name": metric_name,
                    "alert_type": "absence_detection"
                }
            )
            await self.alert_notifier.notify(alert)
            return True

        return False
```

### Data Retention Policy

#### Kafka Retention Configuration

```python
# Retention policies by environment
RETENTION_POLICIES = {
    "production": {
        "realtime_metrics": {
            "retention_ms": 604800000,  # 7 days
            "retention_bytes": 10737418240,  # 10GB per partition
            "segment_ms": 3600000,  # 1 hour segments
        },
        "aggregated_metrics": {
            "retention_ms": 2592000000,  # 30 days
            "retention_bytes": 53687091200,  # 50GB per partition
        },
        "alerts": {
            "retention_ms": 7776000000,  # 90 days
            "retention_bytes": -1,  # Unlimited
        },
        "dlq": {
            "retention_ms": 2592000000,  # 30 days for troubleshooting
            "retention_bytes": 1073741824,  # 1GB per partition
        }
    },
    "development": {
        "realtime_metrics": {
            "retention_ms": 86400000,  # 1 day
            "retention_bytes": 1073741824,  # 1GB
        }
    }
}

class RetentionPolicyManager:
    """Manage data retention policies across systems."""

    def __init__(self, kafka_admin_client, snowflake_conn):
        self.kafka_admin = kafka_admin_client
        self.snowflake = snowflake_conn

    async def apply_kafka_retention_policy(
        self,
        topic: str,
        environment: str,
        topic_type: str
    ):
        """Apply retention policy to Kafka topic."""
        policy = RETENTION_POLICIES[environment][topic_type]

        config = {
            "retention.ms": str(policy["retention_ms"]),
            "retention.bytes": str(policy["retention_bytes"]),
            "segment.ms": str(policy.get("segment_ms", 3600000)),
        }

        # Apply configuration to topic
        await self.kafka_admin.alter_configs({
            "topic": topic,
            "configs": config
        })

        logger.info(f"Applied retention policy to {topic}: {policy}")

    async def apply_snowflake_retention_policy(
        self,
        table_name: str,
        retention_days: int
    ):
        """Apply retention policy to Snowflake table."""
        # Set time travel retention
        await self.snowflake.execute(
            f"ALTER TABLE {table_name} SET DATA_RETENTION_TIME_IN_DAYS = {retention_days}"
        )

        # Schedule data cleanup for old partitions
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        await self.snowflake.execute(
            f"DELETE FROM {table_name} WHERE timestamp < '{cutoff_date.isoformat()}'"
        )

        logger.info(f"Applied {retention_days}-day retention to {table_name}")
```

#### GDPR and Compliance

```python
class ComplianceManager:
    """Handle GDPR and compliance requirements."""

    def __init__(self, kafka_producer, snowflake_conn):
        self.kafka_producer = kafka_producer
        self.snowflake = snowflake_conn

    async def delete_user_data(self, user_id: str):
        """Delete all data for a user (GDPR right to be forgotten)."""
        logger.info(f"Initiating data deletion for user {user_id}")

        # 1. Delete from Kafka (via tombstone messages if using compacted topics)
        await self._delete_from_kafka(user_id)

        # 2. Delete from Snowflake
        await self._delete_from_snowflake(user_id)

        # 3. Log deletion for audit trail
        await self._log_deletion(user_id)

    async def _delete_from_kafka(self, user_id: str):
        """Send tombstone messages for compacted topics."""
        # For compacted topics, send null value to delete key
        self.kafka_producer.send(
            topic="gds.metrics.user_data",
            key=user_id.encode('utf-8'),
            value=None  # Tombstone
        )

    async def _delete_from_snowflake(self, user_id: str):
        """Delete user data from Snowflake."""
        tables = ["metrics_fact", "alerts_history", "user_activity"]

        for table in tables:
            await self.snowflake.execute(
                f"DELETE FROM {table} WHERE user_id = ?",
                (user_id,)
            )

    async def _log_deletion(self, user_id: str):
        """Log data deletion for compliance audit."""
        audit_entry = {
            "action": "data_deletion",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "executed_by": "system"
        }
        # Store in audit log
        await self.kafka_producer.send("audit.log", value=json.dumps(audit_entry))
```

### Disaster Recovery Plan

#### Multi-Region Architecture

```
Primary Region (us-east-1)                Secondary Region (us-west-2)
┌─────────────────────┐                   ┌─────────────────────┐
│   Kafka Cluster     │◄──Replication────►│   Kafka Cluster     │
│   (3 brokers)       │                   │   (3 brokers)       │
└─────────────────────┘                   └─────────────────────┘
         │                                          │
         ▼                                          ▼
┌─────────────────────┐                   ┌─────────────────────┐
│ Telemetry Collector │                   │ Telemetry Collector │
│ Alert Evaluation    │                   │ Alert Evaluation    │
│ (active)            │                   │ (standby)           │
└─────────────────────┘                   └─────────────────────┘
```

#### Kafka Multi-DC Replication

```python
# MirrorMaker 2.0 configuration for cross-region replication
MIRROR_MAKER_CONFIG = """
# Source cluster
clusters = primary, secondary
primary.bootstrap.servers = kafka-primary-1:9092,kafka-primary-2:9092
secondary.bootstrap.servers = kafka-secondary-1:9092,kafka-secondary-2:9092

# Replication flows
primary->secondary.enabled = true
primary->secondary.topics = gds\\.metrics\\..*
secondary->primary.enabled = false  # One-way replication

# Replication settings
replication.factor = 3
sync.topic.configs.enabled = true
checkpoints.topic.replication.factor = 3
"""
```

#### Failover Procedures

```python
class DisasterRecoveryManager:
    """Manage disaster recovery and failover procedures."""

    def __init__(self, primary_region: str, secondary_region: str):
        self.primary_region = primary_region
        self.secondary_region = secondary_region
        self.current_active = primary_region

    async def initiate_failover(self, reason: str):
        """Initiate failover to secondary region."""
        logger.critical(f"Initiating failover: {reason}")

        # Step 1: Stop writes to primary
        await self._stop_primary_writers()

        # Step 2: Verify secondary is caught up
        if not await self._verify_replication_lag():
            logger.error("Secondary region lag too high, waiting...")
            await self._wait_for_sync(timeout=300)

        # Step 3: Promote secondary to active
        await self._promote_secondary()

        # Step 4: Update DNS/load balancers
        await self._update_routing()

        # Step 5: Start secondary region services
        await self._start_secondary_services()

        self.current_active = self.secondary_region
        logger.info(f"Failover complete. Active region: {self.current_active}")

    async def _verify_replication_lag(self) -> bool:
        """Check if replication lag is acceptable."""
        lag = await self._get_replication_lag()
        max_acceptable_lag = 1000  # messages

        return lag < max_acceptable_lag

    async def initiate_failback(self):
        """Failback to primary region after recovery."""
        logger.info("Initiating failback to primary region")

        # Verify primary is healthy
        if not await self._check_primary_health():
            raise Exception("Primary region not healthy")

        # Sync data from secondary to primary
        await self._reverse_replication()

        # Wait for sync
        await self._wait_for_sync(timeout=600)

        # Failover to primary
        await self.initiate_failover("Planned failback to primary")

class BackupManager:
    """Manage backups for disaster recovery."""

    def __init__(self, s3_bucket: str):
        self.s3_bucket = s3_bucket

    async def backup_kafka_offsets(self, consumer_group: str):
        """Backup consumer group offsets to S3."""
        offsets = await self._export_offsets(consumer_group)

        backup_key = f"kafka-offsets/{consumer_group}/{datetime.utcnow().isoformat()}.json"
        await self._upload_to_s3(backup_key, offsets)

        logger.info(f"Backed up offsets for {consumer_group}")

    async def restore_kafka_offsets(self, consumer_group: str, timestamp: str):
        """Restore consumer group offsets from backup."""
        backup_key = f"kafka-offsets/{consumer_group}/{timestamp}.json"
        offsets = await self._download_from_s3(backup_key)

        await self._import_offsets(consumer_group, offsets)
        logger.info(f"Restored offsets for {consumer_group}")
```

#### RTO/RPO Targets

| Component | RTO (Recovery Time Objective) | RPO (Recovery Point Objective) |
|-----------|-------------------------------|--------------------------------|
| Monitoring System | < 15 minutes | < 5 minutes |
| Alerting System | < 5 minutes | < 1 minute |
| Kafka Data | < 30 minutes | < 1 minute |
| Snowflake Data | < 1 hour | < 15 minutes |
| Configuration | < 5 minutes | 0 (stored in Git) |

### Failure Modes and Recovery

#### Common Failure Scenarios

```python
class FailureScenarioHandler:
    """Handle common failure scenarios."""

    async def handle_kafka_broker_failure(self, broker_id: int):
        """Handle Kafka broker failure."""
        logger.error(f"Kafka broker {broker_id} failed")

        # 1. Verify ISR (In-Sync Replicas) status
        isr_status = await self._check_isr_status()

        if isr_status['under_replicated']:
            # Alert on under-replicated partitions
            await self._alert_under_replication(isr_status['partitions'])

        # 2. Monitor topic availability
        if not isr_status['available']:
            # Critical: topics unavailable
            await self._alert_topic_unavailable()

            # Failover to secondary region if configured
            if self.dr_enabled:
                await self.dr_manager.initiate_failover("Kafka broker failure")

        # 3. Auto-recovery: restart broker
        await self._restart_broker(broker_id)

    async def handle_collector_failure(self, collector_id: str):
        """Handle metric collector failure."""
        logger.error(f"Collector {collector_id} failed")

        # 1. Check if backup collector exists
        if backup_collector := await self._get_backup_collector(collector_id):
            # Activate backup
            await backup_collector.start()
            logger.info(f"Activated backup collector for {collector_id}")

        # 2. Try to restart failed collector
        await asyncio.sleep(30)  # Wait before restart
        await self._restart_collector(collector_id)

    async def handle_database_unreachable(self, instance_id: str):
        """Handle database unreachable scenario."""
        logger.error(f"Database {instance_id} unreachable")

        # 1. Verify it's not a network issue
        if await self._check_network_connectivity(instance_id):
            # Network is fine, database is down
            await self._alert_database_down(instance_id)

        # 2. Check for read replica
        if replica := await self._get_read_replica(instance_id):
            # Switch to replica for monitoring
            await self._switch_to_replica(instance_id, replica)

        # 3. Enter maintenance mode (suppress false alerts)
        await self.maintenance_manager.set_maintenance_window(
            instance_id,
            duration_minutes=60,
            reason="Database unreachable"
        )

    async def handle_alert_delivery_failure(self, alert: Alert):
        """Handle alert delivery failure."""
        logger.error(f"Failed to deliver alert {alert.id}")

        # 1. Try backup notification channel
        if backup_notifier := self._get_backup_notifier():
            try:
                await backup_notifier.notify(alert)
                return
            except Exception as e:
                logger.error(f"Backup notifier also failed: {e}")

        # 2. Store in local queue for retry
        await self._queue_for_retry(alert)

        # 3. If critical alert, escalate through alternative means
        if alert.severity == AlertSeverity.CRITICAL:
            await self._escalate_alert(alert)
```

#### Failure Recovery Patterns

**1. Exponential Backoff with Jitter**

```python
async def retry_with_backoff(func, max_retries=5, base_delay=1):
    """Retry with exponential backoff and jitter."""
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise

            # Calculate delay with exponential backoff and jitter
            delay = min(base_delay * (2 ** attempt), 60)  # Cap at 60s
            jitter = random.uniform(0, delay * 0.1)  # Add 10% jitter
            total_delay = delay + jitter

            logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {total_delay:.2f}s")
            await asyncio.sleep(total_delay)
```

**2. Local Spooling for Kafka Unavailability**

```python
class LocalSpoolManager:
    """Spool metrics locally when Kafka is unavailable."""

    def __init__(self, spool_dir: str = "/var/spool/gds-monitor"):
        self.spool_dir = Path(spool_dir)
        self.spool_dir.mkdir(parents=True, exist_ok=True)
        self.max_spool_size_gb = 10

    async def spool_metrics(self, metrics: List[Metric]):
        """Write metrics to local spool."""
        spool_file = self.spool_dir / f"metrics_{int(time.time())}.json"

        # Check spool size
        if await self._get_spool_size_gb() >= self.max_spool_size_gb:
            logger.error("Spool directory full, dropping metrics")
            return

        with open(spool_file, 'w') as f:
            json.dump([asdict(m) for m in metrics], f)

        logger.info(f"Spooled {len(metrics)} metrics to {spool_file}")

    async def replay_spooled_metrics(self, kafka_producer):
        """Replay spooled metrics when Kafka is back online."""
        spool_files = sorted(self.spool_dir.glob("metrics_*.json"))

        for spool_file in spool_files:
            try:
                with open(spool_file, 'r') as f:
                    metrics_data = json.load(f)

                for metric_dict in metrics_data:
                    metric = Metric(**metric_dict)
                    await kafka_producer.send(metric)

                # Delete spool file after successful replay
                spool_file.unlink()
                logger.info(f"Replayed and deleted {spool_file}")

            except Exception as e:
                logger.error(f"Failed to replay {spool_file}: {e}")
```

### Capacity Planning

```python
class CapacityPlanner:
    """Monitor and plan for capacity needs."""

    def __init__(self):
        self.kafka_capacity_threshold = 0.75  # 75%
        self.disk_capacity_threshold = 0.80  # 80%
        self.memory_capacity_threshold = 0.85  # 85%

    async def check_kafka_capacity(self):
        """Check Kafka cluster capacity."""
        # Check disk usage per broker
        for broker in self.kafka_brokers:
            disk_usage = await self._get_broker_disk_usage(broker)

            if disk_usage > self.kafka_capacity_threshold:
                await self._alert_kafka_capacity(broker, disk_usage)

                # Calculate time to full
                growth_rate = await self._calculate_growth_rate(broker)
                days_to_full = self._estimate_days_to_full(disk_usage, growth_rate)

                logger.warning(
                    f"Broker {broker} at {disk_usage*100}% capacity. "
                    f"Estimated {days_to_full} days until full"
                )

    async def forecast_resource_needs(self, days_ahead: int = 90):
        """Forecast resource needs based on trends."""
        # Get historical metrics
        metrics_history = await self._get_metrics_history(days=30)

        # Calculate growth rates
        metrics_per_day_growth = self._calculate_metric_volume_growth(metrics_history)
        kafka_throughput_growth = self._calculate_throughput_growth(metrics_history)

        # Project future needs
        current_throughput = await self._get_current_throughput()
        projected_throughput = current_throughput * (1 + kafka_throughput_growth) ** (days_ahead / 30)

        # Calculate required resources
        required_brokers = math.ceil(projected_throughput / self.broker_capacity)
        required_storage_gb = projected_throughput * days_ahead * self.bytes_per_metric / 1024**3

        return {
            "current_throughput_msg_per_sec": current_throughput,
            "projected_throughput_msg_per_sec": projected_throughput,
            "required_brokers": required_brokers,
            "required_storage_gb": required_storage_gb,
            "recommendation": self._generate_recommendation(required_brokers, required_storage_gb)
        }

    def _estimate_days_to_full(self, current_usage: float, daily_growth_rate: float) -> int:
        """Estimate days until capacity is full."""
        if daily_growth_rate <= 0:
            return float('inf')

        remaining_capacity = 1.0 - current_usage
        days = remaining_capacity / daily_growth_rate

        return int(days)
```

### Performance Benchmarks and SLAs

#### Service Level Objectives (SLOs)

| Service | Metric | Target | Measurement Window |
|---------|--------|--------|-------------------|
| Metric Collection | Success Rate | ≥ 99.9% | 30 days |
| Metric Collection | Latency (p95) | < 5 seconds | 24 hours |
| Metric Collection | Throughput | ≥ 10,000 metrics/sec | 1 hour |
| Kafka Publishing | Success Rate | ≥ 99.99% | 30 days |
| Kafka Publishing | Latency (p95) | < 100 ms | 24 hours |
| Alert Evaluation | Latency (p95) | < 1 minute | 24 hours |
| Alert Evaluation | Success Rate | ≥ 99.95% | 30 days |
| Alert Delivery | Success Rate | ≥ 99.5% | 30 days |
| Alert Delivery | Latency (p95) | < 2 minutes | 24 hours |
| System Availability | Uptime | ≥ 99.9% | 30 days |
| Data Loss | Rate | 0% | Always |

#### Performance Targets

```python
PERFORMANCE_TARGETS = {
    "metric_collection": {
        "throughput_metrics_per_second": 10000,
        "latency_p50_ms": 1000,
        "latency_p95_ms": 5000,
        "latency_p99_ms": 10000,
        "cpu_usage_percent": 70,
        "memory_usage_percent": 80,
    },
    "kafka_producer": {
        "throughput_messages_per_second": 50000,
        "latency_p50_ms": 10,
        "latency_p95_ms": 100,
        "latency_p99_ms": 500,
    },
    "alert_evaluation": {
        "throughput_alerts_per_second": 1000,
        "latency_p50_ms": 100,
        "latency_p95_ms": 1000,
        "latency_p99_ms": 5000,
    },
    "alert_delivery": {
        "throughput_alerts_per_second": 500,
        "latency_p50_ms": 500,
        "latency_p95_ms": 2000,
        "latency_p99_ms": 5000,
    }
}

class SLOMonitor:
    """Monitor SLO compliance and error budgets."""

    def __init__(self, prometheus_client):
        self.prometheus = prometheus_client
        self.slo_targets = {
            "metric_collection_success_rate": 0.999,  # 99.9%
            "alert_delivery_success_rate": 0.995,     # 99.5%
            "system_availability": 0.999,              # 99.9%
        }

    async def check_slo_compliance(self, slo_name: str, window_days: int = 30):
        """Check if SLO is being met."""
        # Query actual performance from Prometheus
        actual_value = await self._query_slo_metric(slo_name, window_days)
        target_value = self.slo_targets[slo_name]

        # Calculate error budget
        total_budget = 1.0 - target_value
        consumed_budget = max(0, target_value - actual_value)
        budget_remaining = max(0, total_budget - consumed_budget)
        budget_percent = (budget_remaining / total_budget * 100) if total_budget > 0 else 100

        compliant = actual_value >= target_value

        result = {
            "slo_name": slo_name,
            "target": target_value,
            "actual": actual_value,
            "compliant": compliant,
            "error_budget_remaining_percent": budget_percent,
            "window_days": window_days
        }

        # Alert if SLO violated or error budget low
        if not compliant:
            await self._alert_slo_violation(result)
        elif budget_percent < 10:
            await self._alert_low_error_budget(result)

        return result
```

## Is This a Best Practice Architecture?

### Examples and Schemas

- Example alert rules: `examples/monitoring/rules.yaml`
- Synthetic metrics generator: `examples/monitoring/generate_synthetic_metrics.py`
- Schema registry stub: `schemas/metrics-value.avsc` with notes in `schemas/README.md`
- E2E tutorial: `docs/tutorials/monitoring_e2e_synthetic_metrics.md`

### Industry Standards and Best Practices

**YES**, this enhanced architecture represents **enterprise-grade best practices** and aligns with modern distributed systems patterns used by major technology companies:

#### Industry Examples

1. **LinkedIn's Monitoring Stack**:
   - **Kafka**: Central message bus for all telemetry data
   - **Samza**: Real-time stream processing for alerting
   - **Druid**: Analytics database for historical analysis
   - **Alerting**: Real-time anomaly detection and notifications

2. **Netflix's Data Pipeline**:
   - **Kafka**: Unified data pipeline for all metrics and events
   - **Multiple Consumers**: Alerting, analytics, ML models, dashboards
   - **Real-time + Batch**: Serves both immediate and historical use cases

3. **Uber's Observability Platform**:
   - **Kafka**: Central message bus for all observability data
   - **Microservices Architecture**: Independent scaling of collection, processing, storage
   - **Multi-tenant**: Different teams consume the same data for different purposes

4. **Modern Cloud-Native Patterns**:
   - **Event-Driven Architecture**: Loose coupling through message queues
   - **Polyglot Persistence**: Different storage solutions for different needs
   - **Consumer-Driven Contracts**: API evolution through schema compatibility

#### Theoretical Foundation

**Event-Driven Architecture Principles**:

- **Loose Coupling**: Producers and consumers don't know about each other
- **Scalability**: Horizontal scaling of producers and consumers independently
- **Reliability**: Message persistence ensures no data loss
- **Extensibility**: New consumers can be added without affecting producers

**Data Mesh Principles**:

- **Domain Ownership**: Each component owns its data and logic
- **Data as Product**: Metrics are a product consumed by multiple teams
- **Self-Serve Platform**: Easy to build new consumers and analytics

### Enhanced Architecture Benefits

#### 1. **Unified Data Pipeline**

- **Single Source of Truth**: All metrics flow through one pipeline
- **Data Consistency**: Same data serves alerting, analytics, and compliance
- **Cost Efficiency**: One collection system, multiple consumers
- **Maintenance**: Single point for data quality and schema evolution

#### 2. **Real-time + Historical Processing**

- **Immediate Response**: Real-time alerting for operational issues
- **Trend Analysis**: Historical data for capacity planning and optimization
- **Predictive Analytics**: ML models trained on historical patterns
- **Compliance**: Complete audit trails and reporting

#### 3. **Enterprise Scalability**

- **Horizontal Scaling**: Add more consumers as needs grow
- **Fault Tolerance**: Components can fail independently
- **Performance Isolation**: Slow consumers don't affect fast ones
- **Resource Optimization**: Scale each component based on its workload

#### 4. **Business Value Maximization**

- **Multiple Stakeholders**: Operations, engineering, business intelligence, finance
- **ROI Optimization**: Single investment serves multiple business needs
- **Innovation Enablement**: Easy to experiment with new analytics use cases
- **Future-Proofing**: Architecture supports evolving business requirements

### Benefits of This Architecture

#### 1. **Scalability**

- **Monitoring**: May need high-frequency collection (every 30 seconds)
- **Alerting**: Rule evaluation can be less frequent but needs low latency
- **Notification**: Can be asynchronous with queuing
- Each can scale independently based on load patterns

#### 2. **Maintainability**

- **Independent Updates**: Fix monitoring bugs without touching alerting logic
- **Technology Evolution**: Upgrade notification system without affecting monitoring
- **Team Autonomy**: Different teams can own different components

#### 3. **Reliability**

- **Failure Isolation**: Monitoring failure doesn't break alerting
- **Circuit Breakers**: Alerting can continue if notification service is down
- **Graceful Degradation**: Fallback mechanisms for each component

#### 4. **Flexibility**

- **Multiple Notification Channels**: Easy to add SMS, Slack, PagerDuty
- **Different Alerting Strategies**: Threshold, anomaly detection, correlation
- **Pluggable Components**: Swap implementations without changing interfaces

#### 5. **Testability**

- **Unit Testing**: Test each component in isolation
- **Integration Testing**: Test component interactions
- **Mock Dependencies**: Easy to mock external services

### Potential Drawbacks and Mitigations

#### 1. **Increased Complexity**

- **Mitigation**: Well-defined interfaces and comprehensive documentation
- **Benefit**: Complexity is managed through clear boundaries

#### 2. **Network Latency**

- **Mitigation**: Async communication, batching, local caching
- **Context**: In monitoring systems, sub-second latency is usually acceptable

#### 3. **Deployment Complexity**

- **Mitigation**: Container orchestration, infrastructure as code
- **Benefit**: Each service can be deployed independently

#### 4. **Debugging Challenges**

- **Mitigation**: Comprehensive logging, distributed tracing, correlation IDs
- **Tools**: Use monitoring to monitor the monitoring system itself

### When This Architecture Excels

This separation is particularly beneficial when:

- **Scale**: Large number of monitored systems (>100 servers/databases)
- **Complexity**: Sophisticated alerting rules and escalation policies
- **Teams**: Multiple development teams with different specializations
- **Reliability Requirements**: High availability and fault tolerance needed
- **Evolution**: System expected to evolve with new requirements

### Alternative Approaches Considered

#### 1. **Monolithic Approach**

```python
class MonitoringSystem:
    def collect_metrics(self): pass
    def evaluate_alerts(self): pass
    def send_notifications(self): pass
```

**Pros**: Simple, fast development
**Cons**: Tight coupling, hard to scale, difficult to test

#### 2. **Two-Tier Approach** (Monitor + Alert/Notify)

**Pros**: Simpler than three-tier
**Cons**: Alerting and notification scaling together, mixed responsibilities

#### 3. **Microservices Extreme**

**Pros**: Maximum flexibility
**Cons**: Over-engineering for smaller systems

### Conclusion: Recommended for This Use Case

**YES, this is a best practice architecture** for the following reasons:

1. **Event-Driven Design**: Kafka as central message bus enables real-time processing
2. **Existing Infrastructure**: Integrates cleanly with enterprise notification platforms
3. **Scalability**: Each component can scale independently with Kafka's partitioning
4. **Industry Alignment**: Follows modern event-driven patterns used by major platforms
5. **Future-Proofing**: Easy to add new consumers (analytics, dashboards, etc.)
6. **Reliability**: Kafka's persistence and replay capabilities ensure no metric loss

The architecture balances separation of concerns with practical integration through Kafka messaging and HTTP APIs, creating a robust, scalable monitoring system that serves both operational alerting and analytical use cases through a unified data pipeline.

---

## References

- Google SRE Book – Monitoring Distributed Systems: <https://sre.google/sre-book/monitoring-distributed-systems/>
- Google SRE Workbook – Monitoring: <https://sre.google/workbook/monitoring/>
- Prometheus – Alerting Best Practices: <https://prometheus.io/docs/practices/alerting/>
- AWS Well-Architected Framework – Reliability: <https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html>
- Azure Monitor – Best Practices: <https://learn.microsoft.com/azure/azure-monitor/best-practices>
- Kafka – Design & Reliability Patterns (Confluent Blog): <https://www.confluent.io/blog/>
- PagerDuty – Alerting & Incident Response Best Practices: <https://response.pagerduty.com/best_practices/>
