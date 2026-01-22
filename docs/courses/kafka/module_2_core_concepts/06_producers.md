# Kafka Producers

**[← Back to Topics](./05_topics_partitions.md)** | **[Next: Consumers →](./07_consumers.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Module](https://img.shields.io/badge/Module-2_Core_Concepts-blue)

## Table of contents

- [Learning objectives](#learning-objectives)
- [Producer architecture](#producer-architecture)
- [Acknowledgment modes](#acknowledgment-modes)
- [Batching and compression](#batching-and-compression)
- [Idempotent producers](#idempotent-producers)
- [Error handling and retries](#error-handling-and-retries)
- [Producer configuration](#producer-configuration)
- [Python producer examples](#python-producer-examples)
- [Key takeaways](#key-takeaways)

---

## Learning objectives

By the end of this lesson, you will be able to:

1. Understand the producer send pipeline
2. Choose appropriate acknowledgment settings
3. Configure batching for optimal throughput
4. Implement idempotent producers for exactly-once semantics
5. Handle errors and implement retry strategies

---

## Producer architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PRODUCER ARCHITECTURE                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Application Code                                                           │
│       │                                                                     │
│       │ producer.send(topic, key, value)                                    │
│       ▼                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        KAFKA PRODUCER                                │   │
│  │                                                                      │   │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐             │   │
│  │  │ Serializer  │───►│ Partitioner │───►│   Batch     │             │   │
│  │  │             │    │             │    │  per Topic- │             │   │
│  │  │ Key + Value │    │ Select      │    │  Partition  │             │   │
│  │  │ → bytes     │    │ Partition   │    │             │             │   │
│  │  └─────────────┘    └─────────────┘    └──────┬──────┘             │   │
│  │                                               │                     │   │
│  │                          ┌────────────────────┴────────────────┐   │   │
│  │                          │         SENDER THREAD               │   │   │
│  │                          │                                     │   │   │
│  │                          │  • Manages connections to brokers   │   │   │
│  │                          │  • Sends batches when ready         │   │   │
│  │                          │  • Handles retries                  │   │   │
│  │                          │  • Processes acknowledgments        │   │   │
│  │                          └─────────────────────────────────────┘   │   │
│  │                                               │                     │   │
│  └───────────────────────────────────────────────┼─────────────────────┘   │
│                                                  │                         │
│                                                  ▼                         │
│                                          Kafka Brokers                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### The send pipeline

1. **Serialize**: Convert key and value to bytes
2. **Partition**: Determine target partition
3. **Batch**: Add to batch for the topic-partition
4. **Send**: Background thread sends when batch is ready
5. **Acknowledge**: Broker confirms receipt

[↑ Back to Table of Contents](#table-of-contents)

---

## Acknowledgment modes

The `acks` setting controls durability guarantees:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ACKNOWLEDGMENT MODES                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  acks=0 (Fire and Forget)                                                   │
│  ────────────────────────                                                   │
│  Producer ──► Broker                                                        │
│           (no wait)                                                         │
│                                                                             │
│  • Fastest throughput                                                       │
│  • No delivery guarantee                                                    │
│  • Use case: Metrics, logs where loss is acceptable                         │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  acks=1 (Leader Only)                                                       │
│  ─────────────────────                                                      │
│  Producer ──► Leader ──► ACK                                                │
│               (writes to disk, then ACK)                                    │
│                                                                             │
│  • Good balance of speed and durability                                     │
│  • Data safe on leader, may lose if leader dies before replication          │
│  • Use case: Most applications                                              │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  acks=all (All ISR)                                                         │
│  ──────────────────                                                         │
│  Producer ──► Leader ──► Replicate ──► ACK                                  │
│               (writes) (to all ISR)   (after all ISR acknowledge)           │
│                                                                             │
│  • Strongest durability guarantee                                           │
│  • Higher latency                                                           │
│  • Use case: Financial transactions, critical data                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Choosing acknowledgment settings

| Setting | Durability | Latency | Throughput | Use Case |
|---------|------------|---------|------------|----------|
| `acks=0` | None | Lowest | Highest | Metrics, non-critical logs |
| `acks=1` | Medium | Medium | Medium | General purpose |
| `acks=all` | Highest | Highest | Lowest | Financial, critical data |

> [!IMPORTANT]
> When using `acks=all`, also set `min.insync.replicas=2` on the topic to ensure at least 2 replicas must acknowledge.

[↑ Back to Table of Contents](#table-of-contents)

---

## Batching and compression

### Batching improves throughput

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    BATCHING BEHAVIOR                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Without Batching (inefficient)                                             │
│  ─────────────────────────────────                                          │
│  send(m1) ──► network ──► broker                                            │
│  send(m2) ──► network ──► broker                                            │
│  send(m3) ──► network ──► broker                                            │
│  3 network round trips                                                      │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  With Batching (efficient)                                                  │
│  ───────────────────────────                                                │
│  send(m1) ──┐                                                               │
│  send(m2) ──┼──► [batch: m1,m2,m3] ──► network ──► broker                   │
│  send(m3) ──┘                                                               │
│  1 network round trip                                                       │
│                                                                             │
│  Batch sent when:                                                           │
│  • batch.size reached (default 16KB)                                        │
│  • linger.ms expires (default 0ms)                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Batch configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `batch.size` | 16384 (16KB) | Max batch size in bytes |
| `linger.ms` | 0 | Wait time for more messages |
| `buffer.memory` | 33554432 (32MB) | Total buffer memory |

**For high throughput:**
```python
producer = Producer({
    'bootstrap.servers': 'localhost:9092',
    'batch.size': 65536,      # 64KB batches
    'linger.ms': 20,          # Wait up to 20ms
    'compression.type': 'lz4' # Compress batches
})
```

### Compression types

| Type | CPU | Compression Ratio | Speed |
|------|-----|-------------------|-------|
| none | None | 1:1 | Fastest |
| gzip | High | Best (~5:1) | Slowest |
| snappy | Low | Good (~3:1) | Fast |
| lz4 | Low | Good (~3:1) | Fastest |
| zstd | Medium | Better (~4:1) | Fast |

**Recommendation:** Use `lz4` for best balance, `zstd` for better compression.

[↑ Back to Table of Contents](#table-of-contents)

---

## Idempotent producers

Idempotent producers guarantee exactly-once delivery within a session, preventing duplicates from retries.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    IDEMPOTENT PRODUCER                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Without Idempotence (possible duplicates)                                  │
│  ─────────────────────────────────────────                                  │
│  Producer sends msg ──► Broker receives, writes                             │
│        │                     │                                              │
│        │ (ACK lost in network)                                              │
│        │                     │                                              │
│  Producer retries ──────────►Broker writes AGAIN (duplicate!)               │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  With Idempotence (exactly-once)                                            │
│  ────────────────────────────────                                           │
│  Producer sends msg ──► Broker receives, writes, tracks (PID=1, seq=5)      │
│        │                     │                                              │
│        │ (ACK lost in network)                                              │
│        │                     │                                              │
│  Producer retries ──────────►Broker sees (PID=1, seq=5) already exists      │
│                              → Returns success, no duplicate                │
│                                                                             │
│  Each message has: ProducerID (PID) + SequenceNumber                        │
│  Broker deduplicates based on this pair.                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Enable idempotence

```python
producer = Producer({
    'bootstrap.servers': 'localhost:9092',
    'enable.idempotence': True  # Enables exactly-once semantics
})
```

When idempotence is enabled:
- `acks` is automatically set to `all`
- `retries` is set to a high value
- `max.in.flight.requests.per.connection` is capped at 5

[↑ Back to Table of Contents](#table-of-contents)

---

## Error handling and retries

### Retryable vs non-retryable errors

| Error Type | Retryable | Examples |
|------------|-----------|----------|
| **Network** | Yes | Connection timeout, leader not available |
| **Transient** | Yes | Not enough replicas, request timeout |
| **Configuration** | No | Invalid topic, authorization failure |
| **Serialization** | No | Schema incompatible, serialization failed |

### Retry configuration

```python
producer = Producer({
    'bootstrap.servers': 'localhost:9092',
    'retries': 10,                    # Number of retries
    'retry.backoff.ms': 100,          # Wait between retries
    'delivery.timeout.ms': 120000,    # Total time to deliver
    'request.timeout.ms': 30000       # Single request timeout
})
```

### Handling delivery failures

```python
from confluent_kafka import Producer

def delivery_callback(err, msg):
    if err is not None:
        print(f"Delivery failed: {err}")
        # Handle error: log, alert, dead letter queue
    else:
        print(f"Delivered to {msg.topic()}[{msg.partition()}] @ {msg.offset()}")

producer = Producer({'bootstrap.servers': 'localhost:9092'})

# Send with callback
producer.produce(
    'my-topic',
    key='key1',
    value='value1',
    callback=delivery_callback
)

# Wait for all messages to be delivered
producer.flush()
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Producer configuration

### Configuration reference

| Configuration | Default | Description |
|---------------|---------|-------------|
| `bootstrap.servers` | - | Broker addresses |
| `acks` | 1 | Acknowledgment mode (0, 1, all) |
| `retries` | 2147483647 | Retry count |
| `batch.size` | 16384 | Batch size bytes |
| `linger.ms` | 0 | Batch wait time |
| `buffer.memory` | 33554432 | Total buffer memory |
| `compression.type` | none | Compression algorithm |
| `enable.idempotence` | false | Enable exactly-once |
| `max.in.flight.requests.per.connection` | 5 | Concurrent requests |

### Configuration profiles

**High throughput:**
```python
config = {
    'bootstrap.servers': 'localhost:9092',
    'acks': 1,
    'batch.size': 65536,
    'linger.ms': 20,
    'compression.type': 'lz4'
}
```

**High durability:**
```python
config = {
    'bootstrap.servers': 'localhost:9092',
    'acks': 'all',
    'enable.idempotence': True,
    'retries': 10,
    'max.in.flight.requests.per.connection': 5
}
```

**Low latency:**
```python
config = {
    'bootstrap.servers': 'localhost:9092',
    'acks': 1,
    'linger.ms': 0,
    'batch.size': 16384
}
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Python producer examples

### Basic producer

```python
from confluent_kafka import Producer
import json

# Configuration
config = {
    'bootstrap.servers': 'localhost:9092',
    'acks': 'all',
    'enable.idempotence': True
}

# Create producer
producer = Producer(config)

# Delivery callback
def on_delivery(err, msg):
    if err:
        print(f"Failed: {err}")
    else:
        print(f"Sent: {msg.topic()}[{msg.partition()}]@{msg.offset()}")

# Send messages
for i in range(10):
    data = {'event': 'test', 'id': i}
    producer.produce(
        topic='events',
        key=str(i),
        value=json.dumps(data),
        callback=on_delivery
    )

# Wait for delivery
producer.flush()
print("All messages sent!")
```

### Async producer with batching

```python
from confluent_kafka import Producer
import json
import time

config = {
    'bootstrap.servers': 'localhost:9092',
    'batch.size': 65536,
    'linger.ms': 50,
    'compression.type': 'lz4'
}

producer = Producer(config)

# Track delivery
delivered = 0
failed = 0

def on_delivery(err, msg):
    global delivered, failed
    if err:
        failed += 1
    else:
        delivered += 1

# Send 100,000 messages
start = time.time()
for i in range(100000):
    producer.produce(
        'high-volume',
        value=json.dumps({'id': i}),
        callback=on_delivery
    )
    # Periodically poll to process callbacks
    if i % 10000 == 0:
        producer.poll(0)

# Final flush
producer.flush()

elapsed = time.time() - start
print(f"Sent: {delivered}, Failed: {failed}")
print(f"Throughput: {100000/elapsed:.0f} msg/sec")
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Key takeaways

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        KEY TAKEAWAYS                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. acks=all + min.insync.replicas=2 for maximum durability                 │
│                                                                             │
│  2. Enable idempotence to prevent duplicates from retries                   │
│                                                                             │
│  3. Use batching (linger.ms > 0) for high throughput                        │
│                                                                             │
│  4. lz4 compression offers best speed/ratio balance                         │
│                                                                             │
│  5. Always handle delivery failures with callbacks                          │
│                                                                             │
│  6. flush() before shutdown to ensure all messages sent                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

**Next:** [Consumers →](./07_consumers.md)
