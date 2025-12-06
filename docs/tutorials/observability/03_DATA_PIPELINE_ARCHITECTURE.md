# Part 3: Data Pipeline Architecture

## What You'll Learn

In this part, you'll learn:

- Event-driven streaming architecture (Kappa)
- Kafka as the telemetry backbone
- Topic design and partitioning strategies
- Consumer groups and offset management
- Schema evolution and versioning
- Data warehouse integration

---

## Overview

A telemetry pipeline is the infrastructure that moves observability data from producers (applications) to consumers (storage, alerting, analytics). The recommended architecture uses **event-driven streaming** with Kafka as the backbone.

```
┌─────────────────────────────────────────────────────────────────┐
│                   TELEMETRY PIPELINE OVERVIEW                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  PRODUCERS                                                       │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                          │
│  │ Python  │  │PowerShell│  │  Other  │                          │
│  │ Service │  │ Scripts │  │ Sources │                          │
│  └────┬────┘  └────┬────┘  └────┬────┘                          │
│       │            │            │                                │
│       └────────────┼────────────┘                                │
│                    │                                             │
│                    ▼                                             │
│  ┌─────────────────────────────────────┐                        │
│  │      OpenTelemetry Collector        │                        │
│  │        (Telemetry Aggregator)       │                        │
│  └─────────────────┬───────────────────┘                        │
│                    │                                             │
│                    ▼                                             │
│  ┌─────────────────────────────────────┐                        │
│  │             KAFKA                   │    ← Single Source     │
│  │        (Message Backbone)           │      of Truth          │
│  └─────────────────┬───────────────────┘                        │
│                    │                                             │
│       ┌────────────┼────────────┬────────────┐                  │
│       │            │            │            │                   │
│       ▼            ▼            ▼            ▼                   │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐             │
│  │ Alert   │  │ Data    │  │Analytics│  │Real-time│             │
│  │ Service │  │Warehouse│  │ Engine  │  │Dashboard│             │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘             │
│  CONSUMERS                                                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Event-Driven Streaming (Kappa Architecture)

### Why Event-Driven?

Traditional batch processing:

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ Collect  │ ──► │  Store   │ ──► │  Batch   │ ──► │  Query   │
│  Data    │     │ (Files)  │     │ Process  │     │ Results  │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
                                       │
                                   Hours delay
```

Event-driven streaming:

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│ Produce  │ ──► │  Stream  │ ──► │ Consume  │
│  Event   │     │ (Kafka)  │     │ (Real-   │
└──────────┘     └──────────┘     │  time)   │
                                  └──────────┘
                      │
                  Seconds delay
```

### Benefits of Event-Driven Telemetry

| Benefit | Description |
|---------|-------------|
| **Real-time** | Telemetry available in seconds, not hours |
| **Decoupling** | Producers and consumers are independent |
| **Replay** | Re-process historical data when needed |
| **Fan-out** | Multiple consumers from single stream |
| **Durability** | Kafka persists events for configurable period |
| **Backpressure** | Natural handling of slow consumers |

### Kappa Architecture

The Kappa architecture simplifies data pipelines by using a **single streaming layer** for both real-time and batch processing:

```
┌─────────────────────────────────────────────────────────────────┐
│                      KAPPA ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│                       ┌──────────────┐                          │
│                       │    Events    │                          │
│                       │   (Kafka)    │                          │
│                       └──────┬───────┘                          │
│                              │                                   │
│           ┌──────────────────┼──────────────────┐               │
│           │                  │                  │               │
│           ▼                  ▼                  ▼               │
│   ┌───────────────┐  ┌───────────────┐  ┌───────────────┐      │
│   │  Real-time    │  │   Batch       │  │  Historical   │      │
│   │  Processing   │  │  Processing   │  │  Replay       │      │
│   │  (Current)    │  │  (Replay old  │  │  (Backfill)   │      │
│   │               │  │   events)     │  │               │      │
│   └───────────────┘  └───────────────┘  └───────────────┘      │
│                                                                  │
│   All processing uses the SAME stream!                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Kafka as the Telemetry Backbone

### Why Kafka?

Kafka is ideal for telemetry because it provides:

| Feature | Benefit for Telemetry |
|---------|----------------------|
| **High throughput** | Handle millions of events per second |
| **Durability** | Events persisted to disk with replication |
| **Ordering** | Guaranteed ordering within partitions |
| **Replay** | Reprocess historical data when needed |
| **Consumer groups** | Multiple independent consumers |
| **Scalability** | Add partitions and brokers as needed |

### Kafka Concepts

```
┌─────────────────────────────────────────────────────────────────┐
│                      KAFKA CONCEPTS                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  TOPIC: A category of messages (e.g., "metrics")                │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Topic: gds.metrics.postgresql                           │    │
│  │ ┌─────────────────────────────────────────────────────┐ │    │
│  │ │ Partition 0: [msg1][msg4][msg7][msg10]...           │ │    │
│  │ └─────────────────────────────────────────────────────┘ │    │
│  │ ┌─────────────────────────────────────────────────────┐ │    │
│  │ │ Partition 1: [msg2][msg5][msg8][msg11]...           │ │    │
│  │ └─────────────────────────────────────────────────────┘ │    │
│  │ ┌─────────────────────────────────────────────────────┐ │    │
│  │ │ Partition 2: [msg3][msg6][msg9][msg12]...           │ │    │
│  │ └─────────────────────────────────────────────────────┘ │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  PARTITION: Ordered, immutable sequence of messages             │
│  OFFSET: Position of a message within a partition               │
│  CONSUMER GROUP: Set of consumers that share partition load     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Topic Design

### Naming Convention

Use a consistent naming scheme for topics:

```
{organization}.{domain}.{type}.{environment}

Examples:
gds.metrics.postgresql.production
gds.metrics.mongodb.staging
gds.logs.application.production
gds.traces.all.production
```

### Topic Structure Options

**Option 1: By Database Type**

```
gds.metrics.postgresql
gds.metrics.mongodb
gds.metrics.mssql
gds.metrics.snowflake
```

**Option 2: By Environment**

```
gds.metrics.production
gds.metrics.staging
gds.metrics.development
```

**Option 3: Combined**

```
gds.metrics.postgresql.production
gds.metrics.mongodb.staging
```

> [!TIP]
> **Recommendation**: Use Option 3 (combined) for flexibility. This allows consumers to subscribe to:
>
> - All metrics: `gds.metrics.*`
> - All PostgreSQL: `gds.metrics.postgresql.*`
> - Specific: `gds.metrics.postgresql.production`

### Partitioning Strategy

Partitions enable parallel processing. Choose partition keys carefully:

| Strategy | Key | Use Case |
|----------|-----|----------|
| **By Instance** | `instance_id` | Preserve per-instance ordering |
| **By Metric Type** | `metric_name` | Group related metrics |
| **By Tenant** | `tenant_id` | Multi-tenant isolation |
| **Random** | None | Maximum parallelism |

**Recommended**: Use `instance_id` as partition key:

```python
# Metrics from same instance go to same partition
key = f"{database_type}:{instance_id}"
producer.send(topic, key=key, value=metric)
```

Benefits:

- Metrics from same instance are ordered
- Enables stateful processing per instance
- Consumers can be assigned specific instances

---

## Message Schema

### Standard Metric Message

```json
{
  "timestamp": "2025-01-15T10:30:00.000Z",
  "database_type": "postgresql",
  "instance_id": "prod-db-01",
  "metric_name": "cpu_usage_percent",
  "value": 85.5,
  "tags": {
    "environment": "production",
    "region": "us-east-1",
    "cluster": "primary"
  },
  "metadata": {
    "collection_duration_ms": 150,
    "version": "1.0",
    "correlation_id": "7f9c1c7e-8b61-4d9d-9a10-9b3a6a7b1234"
  }
}
```

### Schema Fields Explained

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `timestamp` | ISO-8601 | Yes | When metric was collected (UTC) |
| `database_type` | string | Yes | Type of database |
| `instance_id` | string | Yes | Unique identifier for the instance |
| `metric_name` | string | Yes | Name of the metric |
| `value` | number | Yes | Metric value |
| `tags` | object | No | Dimensions for filtering |
| `metadata` | object | No | Additional context |

### Standard Log Message

```json
{
  "timestamp": "2025-01-15T10:30:00.123Z",
  "level": "ERROR",
  "message": "Database connection failed",
  "service": "telemetry-collector",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7",
  "context": {
    "db.system": "postgresql",
    "db.instance": "prod-db-01",
    "error.type": "ConnectionTimeout",
    "error.message": "timeout after 30s"
  }
}
```

---

## Schema Evolution

As your system evolves, schemas will change. Follow these principles:

### Compatibility Rules

| Type | Rule | Example |
|------|------|---------|
| **Backward** | New schema reads old data | Add optional fields |
| **Forward** | Old schema reads new data | Remove optional fields |
| **Full** | Both directions | Safe for all changes |

### Adding Fields (Backward Compatible)

✅ **Safe**: Add optional fields with defaults

```json
// Version 1
{
  "timestamp": "...",
  "metric_name": "cpu_usage",
  "value": 85.5
}

// Version 2 (backward compatible)
{
  "timestamp": "...",
  "metric_name": "cpu_usage",
  "value": 85.5,
  "collection_method": "agent"  // New optional field
}
```

### Breaking Changes

When breaking changes are unavoidable:

1. **Create new topic version**: `gds.metrics.v2.postgresql`
2. **Dual write**: Produce to both old and new topics
3. **Migrate consumers**: Update consumers to read from new topic
4. **Deprecate old topic**: Stop writing after migration period

```
Timeline:
Day 1:  Enable dual write (v1 + v2)
Day 7:  All consumers migrated to v2
Day 14: Disable writes to v1
Day 30: Delete v1 topic
```

### Using Schema Registry

For production, use a schema registry (e.g., Confluent Schema Registry):

```python
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer

# Register schema
schema_registry = SchemaRegistryClient({'url': 'http://schema-registry:8081'})

# Schema validation happens automatically
serializer = AvroSerializer(schema_registry, schema_str, to_dict)

producer.produce(
    topic='gds.metrics.postgresql',
    value=serializer(metric),  # Validates against registered schema
)
```

---

## Consumer Groups

### How Consumer Groups Work

Consumer groups enable parallel processing and load balancing:

```
┌─────────────────────────────────────────────────────────────────┐
│                     CONSUMER GROUPS                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Topic: gds.metrics.production (8 partitions)                   │
│  ┌───┐┌───┐┌───┐┌───┐┌───┐┌───┐┌───┐┌───┐                      │
│  │P0 ││P1 ││P2 ││P3 ││P4 ││P5 ││P6 ││P7 │                      │
│  └─┬─┘└─┬─┘└─┬─┘└─┬─┘└─┬─┘└─┬─┘└─┬─┘└─┬─┘                      │
│    │    │    │    │    │    │    │    │                         │
│    └────┴────┘    └────┴────┘    └────┴────┘                    │
│         │              │              │                          │
│    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐                    │
│    │Consumer │    │Consumer │    │Consumer │                    │
│    │   A1    │    │   A2    │    │   A3    │                    │
│    └─────────┘    └─────────┘    └─────────┘                    │
│    Group: gds-alerting (3 consumers, 8 partitions)              │
│                                                                  │
│  ════════════════════════════════════════════════               │
│                                                                  │
│  Same topic, different consumer group:                          │
│  ┌───┐┌───┐┌───┐┌───┐┌───┐┌───┐┌───┐┌───┐                      │
│  │P0 ││P1 ││P2 ││P3 ││P4 ││P5 ││P6 ││P7 │                      │
│  └─┬─┘└─┬─┘└─┬─┘└─┬─┘└─┬─┘└─┬─┘└─┬─┘└─┬─┘                      │
│    └────┴────┴────┴────┴────┴────┴────┴────┘                    │
│                       │                                          │
│                  ┌────▼────┐                                     │
│                  │Consumer │                                     │
│                  │   B1    │                                     │
│                  └─────────┘                                     │
│    Group: gds-warehouse (1 consumer, 8 partitions)              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Consumer Group Best Practices

| Group | Purpose | Consumers |
|-------|---------|-----------|
| `gds-alerting` | Evaluate alert rules | Scale with load |
| `gds-warehouse` | Load to Snowflake | Fewer, batch-oriented |
| `gds-analytics` | Real-time dashboards | Scale with query load |
| `gds-archive` | Long-term storage | Fewer, high throughput |

---

## Offset Management

### What are Offsets?

An **offset** is the position of a message within a partition:

```
Partition 0:
Offset:  0    1    2    3    4    5    6    7    8    9
        ┌────┬────┬────┬────┬────┬────┬────┬────┬────┬────┐
        │msg0│msg1│msg2│msg3│msg4│msg5│msg6│msg7│msg8│msg9│
        └────┴────┴────┴────┴────┴────┴────┴────┴────┴────┘
                              ↑
                    Committed offset: 4
                    (Consumer has processed 0-3)
```

### Offset Commit Strategies

**Auto-commit** (simple but risky):

```python
consumer = KafkaConsumer(
    'gds.metrics.production',
    enable_auto_commit=True,
    auto_commit_interval_ms=5000  # Every 5 seconds
)
```

**Manual commit** (recommended for reliability):

```python
consumer = KafkaConsumer(
    'gds.metrics.production',
    enable_auto_commit=False  # Manual control
)

for message in consumer:
    process_message(message)  # Process first
    consumer.commit()          # Then commit
```

### Exactly-Once Processing

For critical systems, implement idempotent processing:

```python
# Idempotent processor using message ID
processed_ids = redis_client  # Track processed messages

for message in consumer:
    msg_id = f"{message.topic}:{message.partition}:{message.offset}"

    if not processed_ids.exists(msg_id):
        process_message(message)
        processed_ids.set(msg_id, "1", ex=3600)  # Expire after 1 hour

    consumer.commit()
```

---

## Dead Letter Queue (DLQ)

Messages that fail processing should go to a DLQ for investigation:

```
┌─────────────────────────────────────────────────────────────────┐
│                    DEAD LETTER QUEUE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Main Topic                           DLQ Topic                  │
│  ┌─────────────────────────┐         ┌─────────────────────────┐│
│  │ gds.metrics.production  │         │ gds.metrics.dlq         ││
│  │ ┌───┬───┬───┬───┬───┐   │         │ ┌───────────────────┐   ││
│  │ │ ✓ │ ✓ │ ✗ │ ✓ │ ✓ │   │   ──►   │ │ Failed message +  │   ││
│  │ └───┴───┴───┴───┴───┘   │         │ │ error context     │   ││
│  └─────────────────────────┘         │ └───────────────────┘   ││
│          │                           └─────────────────────────┘│
│          │                                      │               │
│          ▼                                      ▼               │
│  ┌─────────────────┐                 ┌─────────────────┐        │
│  │    Consumer     │                 │   DLQ Monitor   │        │
│  │ (Alert Service) │                 │   (Dashboard)   │        │
│  └─────────────────┘                 └─────────────────┘        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### DLQ Message Format

```json
{
  "original_topic": "gds.metrics.production",
  "original_partition": 3,
  "original_offset": 12345,
  "original_key": "postgresql:prod-db-01",
  "original_value": "{...}",
  "error": "JSON parse error: unexpected token",
  "error_type": "MalformedMessageError",
  "timestamp": "2025-01-15T10:30:00Z",
  "retry_count": 3,
  "consumer_id": "gds-alerting-consumer-1"
}
```

---

## Data Warehouse Integration

### Loading to Snowflake

```
┌─────────────────────────────────────────────────────────────────┐
│                 SNOWFLAKE INTEGRATION                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Kafka ──► Consumer ──► S3 (Staging) ──► Snowflake              │
│                                │                                 │
│           Batch every          │        COPY INTO command        │
│           5-15 minutes    ┌────▼────┐                           │
│                           │ Parquet │                           │
│                           │  Files  │                           │
│                           └─────────┘                           │
│                                                                  │
│  OR: Direct via Snowflake Kafka Connector                       │
│                                                                  │
│  Kafka ──► Kafka Connect ──► Snowflake                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Use Cases

| Consumer | Purpose | Latency |
|----------|---------|---------|
| Alert Service | Real-time alerting | Seconds |
| Analytics Dashboard | Live monitoring | Seconds |
| Data Warehouse | Historical analysis | Minutes |
| Archive (S3) | Long-term storage | Minutes |

---

## Kafka Configuration

### Producer Configuration

```python
producer_config = {
    # Reliability
    'acks': 'all',               # Wait for all replicas
    'enable.idempotence': True,  # Exactly-once semantics
    'retries': 2147483647,       # Retry indefinitely

    # Performance
    'compression.type': 'lz4',   # Fast compression
    'linger.ms': 100,            # Batch for 100ms
    'batch.size': 16384,         # 16KB batches

    # Connection
    'bootstrap.servers': 'kafka-1:9092,kafka-2:9092,kafka-3:9092',
}
```

### Consumer Configuration

```python
consumer_config = {
    # Group management
    'group.id': 'gds-alerting',
    'enable.auto.commit': False,  # Manual commits
    'auto.offset.reset': 'earliest',

    # Performance
    'fetch.min.bytes': 1024,      # Wait for 1KB
    'max.poll.records': 500,      # Process 500 at a time

    # Connection
    'bootstrap.servers': 'kafka-1:9092,kafka-2:9092,kafka-3:9092',
}
```

### Topic Configuration

```python
topic_config = {
    'num.partitions': 12,          # Based on parallelism needs
    'replication.factor': 3,       # 3 replicas for durability
    'min.insync.replicas': 2,      # At least 2 must acknowledge
    'retention.ms': 604800000,     # 7 days
    'cleanup.policy': 'delete',    # Delete old messages
}
```

---

## Summary

| Concept | Key Points |
|---------|------------|
| **Kappa Architecture** | Single streaming layer for all processing |
| **Kafka** | Durable, high-throughput message backbone |
| **Topic Design** | Naming convention, partitioning strategy |
| **Message Schema** | Consistent format with evolution strategy |
| **Consumer Groups** | Parallel processing with independent progress |
| **Offset Management** | Manual commits for reliability |
| **DLQ** | Handle failed messages gracefully |

### Key Takeaways

1. **Use event-driven streaming** for real-time observability
2. **Design topics carefully**—naming and partitioning matter
3. **Plan for schema evolution** from the start
4. **Use consumer groups** for parallel processing and fan-out
5. **Implement DLQ** for error handling
6. **Choose appropriate configurations** for reliability vs performance

---

## What's Next?

Part 4 will dive deep into **OpenTelemetry**, the standard for collecting and exporting telemetry data.

[Continue to Part 4: OpenTelemetry Deep Dive →](04_OPENTELEMETRY.md)
