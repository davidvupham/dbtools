# Part 7: Kafka Streaming

## What You'll Learn

In this part, you'll learn:

- Kafka fundamentals for telemetry streaming
- Producer and consumer configuration
- Topic design and partitioning
- Offset management and exactly-once semantics
- Dead letter queues and error handling
- Production best practices

---

## Why Kafka for Telemetry?

Kafka provides key capabilities for telemetry pipelines:

| Feature | Benefit |
|---------|---------|
| **High throughput** | Handle millions of events/second |
| **Durability** | Persist events to disk with replication |
| **Ordering** | Guaranteed order within partitions |
| **Replay** | Re-process historical data |
| **Fan-out** | Multiple independent consumers |
| **Backpressure** | Natural handling of slow consumers |

---

## Producer Configuration

### Python Producer Setup

```python
from confluent_kafka import Producer
import json

def create_producer(bootstrap_servers: str) -> Producer:
    """Create a configured Kafka producer."""

    config = {
        # Connection
        'bootstrap.servers': bootstrap_servers,
        'client.id': 'telemetry-producer',

        # Reliability
        'acks': 'all',                    # Wait for all replicas
        'enable.idempotence': True,       # Exactly-once semantics
        'retries': 2147483647,            # Retry indefinitely
        'delivery.timeout.ms': 120000,    # 2 minute timeout

        # Performance
        'compression.type': 'lz4',        # Fast compression
        'linger.ms': 100,                 # Batch for 100ms
        'batch.size': 16384,              # 16KB batches
    }

    return Producer(config)

# Usage
producer = create_producer('kafka-1:9092,kafka-2:9092,kafka-3:9092')
```

### Sending Messages

```python
def send_metric(producer: Producer, topic: str, metric: dict):
    """Send a metric to Kafka."""

    # Use instance_id as key for partitioning
    key = f"{metric['database_type']}:{metric['instance_id']}"
    value = json.dumps(metric)

    def delivery_callback(err, msg):
        if err:
            print(f"Delivery failed: {err}")
        else:
            print(f"Delivered to {msg.topic()} [{msg.partition()}] @ {msg.offset()}")

    producer.produce(
        topic=topic,
        key=key.encode('utf-8'),
        value=value.encode('utf-8'),
        callback=delivery_callback
    )

    # Flush to ensure delivery (or use poll() in a loop)
    producer.flush()

# Send a metric
send_metric(producer, 'gds.metrics.production', {
    'timestamp': '2025-01-15T10:30:00Z',
    'database_type': 'postgresql',
    'instance_id': 'prod-db-01',
    'metric_name': 'cpu_usage_percent',
    'value': 85.5,
    'tags': {'environment': 'production'}
})
```

### Batch Sending

```python
def send_metrics_batch(producer: Producer, topic: str, metrics: list):
    """Send multiple metrics efficiently."""

    for metric in metrics:
        key = f"{metric['database_type']}:{metric['instance_id']}"
        producer.produce(
            topic=topic,
            key=key.encode('utf-8'),
            value=json.dumps(metric).encode('utf-8')
        )

        # Poll to handle callbacks and prevent buffer full
        producer.poll(0)

    # Wait for all messages to be delivered
    remaining = producer.flush(timeout=30)
    if remaining > 0:
        print(f"Warning: {remaining} messages not delivered")
```

---

## Consumer Configuration

### Python Consumer Setup

```python
from confluent_kafka import Consumer, KafkaError
import json

def create_consumer(bootstrap_servers: str, group_id: str) -> Consumer:
    """Create a configured Kafka consumer."""

    config = {
        # Connection
        'bootstrap.servers': bootstrap_servers,
        'client.id': f'{group_id}-consumer',

        # Group management
        'group.id': group_id,
        'auto.offset.reset': 'earliest',  # Start from beginning

        # Offset management
        'enable.auto.commit': False,      # Manual commits

        # Performance
        'fetch.min.bytes': 1024,          # Wait for 1KB
        'fetch.wait.max.ms': 500,         # Or 500ms
        'max.poll.interval.ms': 300000,   # 5 min processing time
    }

    return Consumer(config)

# Usage
consumer = create_consumer('kafka:9092', 'gds-alerting')
consumer.subscribe(['gds.metrics.production'])
```

### Consuming Messages

```python
def consume_messages(consumer: Consumer, process_func):
    """Consume and process messages with manual commit."""

    try:
        while True:
            msg = consumer.poll(timeout=1.0)

            if msg is None:
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition
                    continue
                else:
                    print(f"Consumer error: {msg.error()}")
                    continue

            try:
                # Parse message
                key = msg.key().decode('utf-8') if msg.key() else None
                value = json.loads(msg.value().decode('utf-8'))

                # Process message
                process_func(key, value)

                # Commit offset after successful processing
                consumer.commit(asynchronous=False)

            except Exception as e:
                print(f"Processing error: {e}")
                # Handle error (send to DLQ, etc.)

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

# Example processor
def process_metric(key: str, metric: dict):
    """Process a single metric."""
    print(f"Received: {metric['metric_name']} = {metric['value']}")

    # Check against thresholds
    if metric['metric_name'] == 'cpu_usage_percent' and metric['value'] > 80:
        print(f"ALERT: High CPU on {metric['instance_id']}")

consume_messages(consumer, process_metric)
```

---

## Batch Processing

For higher throughput, process messages in batches:

```python
def consume_batch(consumer: Consumer, batch_size: int, timeout: float):
    """Consume a batch of messages."""

    messages = []
    deadline = time.time() + timeout

    while len(messages) < batch_size and time.time() < deadline:
        msg = consumer.poll(timeout=0.1)

        if msg is None:
            continue
        if msg.error():
            continue

        messages.append({
            'key': msg.key().decode('utf-8') if msg.key() else None,
            'value': json.loads(msg.value().decode('utf-8')),
            'partition': msg.partition(),
            'offset': msg.offset()
        })

    return messages

def process_batches(consumer: Consumer, process_batch_func):
    """Process messages in batches."""

    try:
        while True:
            batch = consume_batch(consumer, batch_size=100, timeout=5.0)

            if batch:
                try:
                    process_batch_func(batch)
                    consumer.commit(asynchronous=False)
                    print(f"Processed batch of {len(batch)} messages")
                except Exception as e:
                    print(f"Batch processing failed: {e}")

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

# Example batch processor
def process_metric_batch(batch: list):
    """Process a batch of metrics."""
    alerts = []

    for msg in batch:
        metric = msg['value']
        if metric['metric_name'] == 'cpu_usage_percent' and metric['value'] > 80:
            alerts.append(metric)

    if alerts:
        send_alerts(alerts)
```

---

## Topic Design

### Naming Convention

```
{organization}.{domain}.{signal}.{environment}

Examples:
gds.metrics.postgresql.production
gds.metrics.mongodb.staging
gds.logs.application.production
gds.traces.all.production
```

### Creating Topics

```python
from confluent_kafka.admin import AdminClient, NewTopic

def create_topics(bootstrap_servers: str, topics: list):
    """Create Kafka topics with proper configuration."""

    admin = AdminClient({'bootstrap.servers': bootstrap_servers})

    new_topics = [
        NewTopic(
            topic=topic_name,
            num_partitions=12,           # Based on parallelism needs
            replication_factor=3,         # 3 replicas for durability
            config={
                'retention.ms': '604800000',      # 7 days
                'min.insync.replicas': '2',       # At least 2 replicas
                'cleanup.policy': 'delete',
                'compression.type': 'lz4',
            }
        )
        for topic_name in topics
    ]

    futures = admin.create_topics(new_topics)

    for topic, future in futures.items():
        try:
            future.result()
            print(f"Created topic: {topic}")
        except Exception as e:
            print(f"Failed to create {topic}: {e}")

# Create topics
create_topics('kafka:9092', [
    'gds.metrics.production',
    'gds.logs.production',
    'gds.alerts.production',
    'gds.metrics.dlq',
])
```

### Partition Key Selection

| Strategy | Key | Use Case |
|----------|-----|----------|
| **By Instance** | `instance_id` | Per-instance ordering |
| **By Type** | `metric_name` | Group related metrics |
| **By Tenant** | `tenant_id` | Multi-tenant isolation |
| **Random** | `None` | Maximum parallelism |

```python
# By instance (preserves per-instance ordering)
key = f"{metric['database_type']}:{metric['instance_id']}"

# By metric type (groups similar metrics)
key = metric['metric_name']

# Random (maximum parallelism)
key = None  # Kafka uses round-robin
```

---

## Dead Letter Queue (DLQ)

Handle messages that fail processing:

```python
class DLQHandler:
    """Handle failed messages with Dead Letter Queue."""

    def __init__(self, producer: Producer, dlq_topic: str):
        self.producer = producer
        self.dlq_topic = dlq_topic
        self.max_retries = 3

    def send_to_dlq(self, original_msg: dict, error: Exception, attempt: int):
        """Send failed message to DLQ with context."""

        dlq_message = {
            'original_topic': original_msg.get('topic'),
            'original_partition': original_msg.get('partition'),
            'original_offset': original_msg.get('offset'),
            'original_key': original_msg.get('key'),
            'original_value': original_msg.get('value'),
            'error': str(error),
            'error_type': type(error).__name__,
            'attempt': attempt,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
        }

        self.producer.produce(
            topic=self.dlq_topic,
            key=original_msg.get('key', '').encode('utf-8'),
            value=json.dumps(dlq_message).encode('utf-8')
        )
        self.producer.flush()

        print(f"Sent to DLQ: {original_msg.get('key')}")

def process_with_dlq(consumer: Consumer, dlq_handler: DLQHandler):
    """Process messages with DLQ handling."""

    while True:
        msg = consumer.poll(timeout=1.0)

        if msg is None or msg.error():
            continue

        original = {
            'topic': msg.topic(),
            'partition': msg.partition(),
            'offset': msg.offset(),
            'key': msg.key().decode('utf-8') if msg.key() else None,
            'value': msg.value().decode('utf-8'),
        }

        for attempt in range(1, dlq_handler.max_retries + 1):
            try:
                value = json.loads(original['value'])
                process_metric(original['key'], value)
                consumer.commit()
                break

            except Exception as e:
                if attempt == dlq_handler.max_retries:
                    dlq_handler.send_to_dlq(original, e, attempt)
                    consumer.commit()  # Still commit to move forward
                else:
                    print(f"Retry {attempt}/{dlq_handler.max_retries}: {e}")
                    time.sleep(2 ** attempt)  # Exponential backoff
```

---

## Exactly-Once Semantics

### Idempotent Producer

```python
# Enable idempotence in producer config
config = {
    'enable.idempotence': True,
    'acks': 'all',
    'retries': 2147483647,
}
```

### Idempotent Consumer

```python
import redis

class IdempotentProcessor:
    """Process messages exactly once using Redis deduplication."""

    def __init__(self, redis_client):
        self.redis = redis_client
        self.ttl = 3600  # 1 hour deduplication window

    def process_if_new(self, message_id: str, process_func, *args) -> bool:
        """Process message only if not seen before."""

        # Try to set key (atomic operation)
        was_set = self.redis.set(
            f"processed:{message_id}",
            "1",
            ex=self.ttl,
            nx=True  # Only set if not exists
        )

        if was_set:
            # First time seeing this message
            process_func(*args)
            return True
        else:
            # Already processed
            print(f"Duplicate message: {message_id}")
            return False

# Usage
redis_client = redis.Redis()
processor = IdempotentProcessor(redis_client)

for msg in consumer:
    message_id = f"{msg.topic()}:{msg.partition()}:{msg.offset()}"

    processor.process_if_new(
        message_id,
        process_metric,
        msg.value()
    )
    consumer.commit()
```

### Transactional Producer

```python
from confluent_kafka import Producer

def create_transactional_producer(bootstrap_servers: str, transactional_id: str):
    """Create a transactional producer for exactly-once semantics."""

    config = {
        'bootstrap.servers': bootstrap_servers,
        'transactional.id': transactional_id,
        'enable.idempotence': True,
        'acks': 'all',
    }

    producer = Producer(config)
    producer.init_transactions()

    return producer

def send_transactional(producer: Producer, topic: str, messages: list):
    """Send messages in a transaction."""

    try:
        producer.begin_transaction()

        for msg in messages:
            producer.produce(
                topic=topic,
                key=msg['key'].encode('utf-8'),
                value=json.dumps(msg['value']).encode('utf-8')
            )

        producer.commit_transaction()
        print(f"Committed {len(messages)} messages")

    except Exception as e:
        producer.abort_transaction()
        print(f"Transaction aborted: {e}")
        raise
```

---

## Consumer Groups

### Multiple Consumers

```python
# Consumer Group: gds-alerting
# Multiple consumers share the workload

# Consumer 1
consumer1 = create_consumer('kafka:9092', 'gds-alerting')
consumer1.subscribe(['gds.metrics.production'])
# Handles partitions 0, 1, 2, 3

# Consumer 2
consumer2 = create_consumer('kafka:9092', 'gds-alerting')
consumer2.subscribe(['gds.metrics.production'])
# Handles partitions 4, 5, 6, 7

# Consumer 3
consumer3 = create_consumer('kafka:9092', 'gds-alerting')
consumer3.subscribe(['gds.metrics.production'])
# Handles partitions 8, 9, 10, 11
```

### Multiple Consumer Groups

```python
# Same messages go to multiple independent groups

# Alerting group
alerting_consumer = create_consumer('kafka:9092', 'gds-alerting')
alerting_consumer.subscribe(['gds.metrics.production'])

# Warehouse loading group
warehouse_consumer = create_consumer('kafka:9092', 'gds-warehouse')
warehouse_consumer.subscribe(['gds.metrics.production'])

# Analytics group
analytics_consumer = create_consumer('kafka:9092', 'gds-analytics')
analytics_consumer.subscribe(['gds.metrics.production'])

# All three groups receive ALL messages independently
```

---

## Monitoring Kafka

### Key Metrics to Watch

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| Consumer Lag | Messages behind latest | > 10,000 |
| Under-replicated Partitions | Replicas not in sync | > 0 |
| Request Latency | Producer/consumer latency | > 100ms p99 |
| Bytes In/Out | Network throughput | Capacity limits |

### Consumer Lag Monitoring

```python
from confluent_kafka import Consumer
from confluent_kafka.admin import AdminClient

def get_consumer_lag(bootstrap_servers: str, group_id: str, topic: str):
    """Get consumer lag for a group."""

    admin = AdminClient({'bootstrap.servers': bootstrap_servers})

    # Get committed offsets
    consumer = Consumer({
        'bootstrap.servers': bootstrap_servers,
        'group.id': group_id,
    })

    committed = consumer.committed([
        TopicPartition(topic, p)
        for p in range(12)  # Assuming 12 partitions
    ])

    # Get end offsets (high watermarks)
    consumer.subscribe([topic])

    total_lag = 0
    for tp in committed:
        if tp.offset >= 0:
            _, high = consumer.get_watermark_offsets(tp)
            lag = high - tp.offset
            total_lag += lag
            print(f"Partition {tp.partition}: lag = {lag}")

    print(f"Total lag: {total_lag}")
    return total_lag
```

---

## Production Checklist

### Producer Checklist

- [ ] `acks=all` for durability
- [ ] `enable.idempotence=true` for exactly-once
- [ ] `compression.type` configured (lz4/snappy)
- [ ] Appropriate `batch.size` and `linger.ms`
- [ ] Delivery callback handling
- [ ] Graceful shutdown with `flush()`

### Consumer Checklist

- [ ] `enable.auto.commit=false` for reliability
- [ ] Manual commit after processing
- [ ] Error handling with DLQ
- [ ] Graceful shutdown
- [ ] Lag monitoring
- [ ] Idempotent processing for exactly-once

### Topic Checklist

- [ ] Appropriate partition count
- [ ] `replication.factor >= 3`
- [ ] `min.insync.replicas >= 2`
- [ ] Retention configured
- [ ] Compression enabled

---

## Summary

| Topic | Key Points |
|-------|------------|
| **Producer** | acks=all, idempotence, batching |
| **Consumer** | Manual commits, batch processing |
| **Topics** | Naming, partitioning, replication |
| **DLQ** | Handle failures gracefully |
| **Exactly-Once** | Idempotent producer + consumer |
| **Consumer Groups** | Parallel processing, fan-out |

### Key Takeaways

1. **Configure for reliability** - acks=all, replicas, min.insync
2. **Use manual commits** - commit after successful processing
3. **Implement DLQ** - don't lose failed messages
4. **Choose partition keys carefully** - affects ordering and parallelism
5. **Monitor consumer lag** - detect processing issues early

---

## What's Next?

Part 8 covers **Alerting and Notification** patterns for acting on telemetry data.

[Continue to Part 8: Alerting and Notification →](08_ALERTING_NOTIFICATION.md)
