# Lesson 07: Kafka consumers

**[← Back to Module 2](./README.md)** | **[Next: Consumer Groups →](./08_consumer_groups.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Consumers-blue)

## Overview

This lesson covers Kafka consumers in depth. You'll learn how consumers read messages from topics, manage offsets, and handle various failure scenarios.

**Learning objectives:**
- Understand the consumer architecture and lifecycle
- Learn offset management strategies
- Implement reliable message processing
- Handle consumer failures gracefully

**Prerequisites:** Lesson 06 (Producers)

**Estimated time:** 45 minutes

---

## Table of contents

- [Consumer fundamentals](#consumer-fundamentals)
- [Consumer configuration](#consumer-configuration)
- [Offset management](#offset-management)
- [Message processing patterns](#message-processing-patterns)
- [Error handling](#error-handling)
- [Performance tuning](#performance-tuning)
- [Hands-on exercises](#hands-on-exercises)
- [Key takeaways](#key-takeaways)

---

## Consumer fundamentals

### What is a Kafka consumer?

A Kafka consumer is a client that reads (consumes) messages from Kafka topics. Consumers subscribe to one or more topics and process the stream of records published to them.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CONSUMER ARCHITECTURE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                          KAFKA CLUSTER                                      │
│    ┌─────────────────────────────────────────────────────────────┐         │
│    │  Topic: orders                                               │         │
│    │  ┌───────────┐ ┌───────────┐ ┌───────────┐                 │         │
│    │  │Partition 0│ │Partition 1│ │Partition 2│                 │         │
│    │  │  [0,1,2]  │ │  [0,1,2]  │ │  [0,1,2]  │                 │         │
│    │  └─────┬─────┘ └─────┬─────┘ └─────┬─────┘                 │         │
│    │        │             │             │                        │         │
│    └────────┼─────────────┼─────────────┼────────────────────────┘         │
│             │             │             │                                   │
│             │    FETCH    │             │                                   │
│             ▼             ▼             ▼                                   │
│       ┌─────────────────────────────────────────┐                          │
│       │              CONSUMER                    │                          │
│       │  ┌─────────────────────────────────┐    │                          │
│       │  │        Consumer Record           │    │                          │
│       │  │  - topic: "orders"               │    │                          │
│       │  │  - partition: 0                  │    │                          │
│       │  │  - offset: 42                    │    │                          │
│       │  │  - key: "order-123"              │    │                          │
│       │  │  - value: {...}                  │    │                          │
│       │  │  - timestamp: 1705891200000      │    │                          │
│       │  │  - headers: [...]                │    │                          │
│       │  └─────────────────────────────────┘    │                          │
│       └─────────────────────────────────────────┘                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Consumer lifecycle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CONSUMER LIFECYCLE                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│    ┌──────────┐    ┌───────────┐    ┌──────────┐    ┌──────────────┐       │
│    │  CREATE  │───►│ SUBSCRIBE │───►│  POLL    │───►│   PROCESS    │       │
│    │ Consumer │    │ to Topics │    │ Records  │    │   Records    │       │
│    └──────────┘    └───────────┘    └────┬─────┘    └──────┬───────┘       │
│                                          │                  │               │
│                                          │                  │               │
│                                          ▼                  ▼               │
│                                    ┌───────────┐     ┌────────────┐        │
│                                    │  COMMIT   │◄────│  Continue  │        │
│                                    │  Offset   │     │   or Exit  │        │
│                                    └───────────┘     └────────────┘        │
│                                          │                                  │
│                                          ▼                                  │
│                                    ┌───────────┐                           │
│                                    │   CLOSE   │                           │
│                                    │ Consumer  │                           │
│                                    └───────────┘                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Basic consumer example (Python)

```python
from confluent_kafka import Consumer, KafkaError

# Create consumer configuration
config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'my-consumer-group',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': True,
    'auto.commit.interval.ms': 5000
}

# Create consumer instance
consumer = Consumer(config)

# Subscribe to topics
consumer.subscribe(['orders', 'payments'])

try:
    while True:
        # Poll for messages (timeout in seconds)
        msg = consumer.poll(1.0)

        if msg is None:
            continue

        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # End of partition event
                print(f'Reached end of partition {msg.partition()}')
            else:
                raise Exception(msg.error())
        else:
            # Process the message
            print(f'Received: key={msg.key()}, value={msg.value()}')
            print(f'  Topic: {msg.topic()}, Partition: {msg.partition()}, Offset: {msg.offset()}')

finally:
    # Close consumer gracefully
    consumer.close()
```

---

## Consumer configuration

### Essential configuration parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `bootstrap.servers` | - | Kafka broker addresses |
| `group.id` | - | Consumer group identifier |
| `auto.offset.reset` | latest | Where to start when no offset exists |
| `enable.auto.commit` | true | Automatically commit offsets |
| `auto.commit.interval.ms` | 5000 | Auto-commit frequency |
| `max.poll.records` | 500 | Max records per poll |
| `max.poll.interval.ms` | 300000 | Max time between polls |
| `session.timeout.ms` | 45000 | Consumer session timeout |
| `heartbeat.interval.ms` | 3000 | Heartbeat frequency |

### Configuration by use case

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CONSUMER CONFIGURATION PROFILES                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  HIGH THROUGHPUT                       LOW LATENCY                          │
│  ────────────────                      ───────────                          │
│  fetch.min.bytes: 1048576 (1MB)        fetch.min.bytes: 1                   │
│  fetch.max.wait.ms: 500                fetch.max.wait.ms: 100               │
│  max.poll.records: 1000                max.poll.records: 100                │
│  enable.auto.commit: true              enable.auto.commit: true             │
│                                                                             │
│  Best for: Log aggregation,            Best for: Real-time dashboards,      │
│  batch processing                      alerting, gaming                     │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  EXACTLY-ONCE                          AT-LEAST-ONCE                        │
│  ───────────                           ─────────────                        │
│  enable.auto.commit: false             enable.auto.commit: false            │
│  isolation.level: read_committed       auto.offset.reset: earliest          │
│  Manual commit after processing        Commit after successful processing   │
│                                                                             │
│  Best for: Financial transactions,     Best for: Order processing,          │
│  inventory updates                     notifications                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### auto.offset.reset options

When a consumer starts and has no committed offset (new group or reset):

| Value | Behavior | Use Case |
|-------|----------|----------|
| `earliest` | Start from beginning | Replay all history |
| `latest` | Start from newest | Only new messages |
| `none` | Throw exception | Require explicit offset |

```python
# Start from the beginning (process all historical data)
config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'new-consumer-group',
    'auto.offset.reset': 'earliest'  # Will read from offset 0
}

# Start from the end (only new messages)
config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'realtime-consumer-group',
    'auto.offset.reset': 'latest'  # Will skip historical messages
}
```

---

## Offset management

### What are offsets?

An offset is a unique identifier for each message within a partition. Offsets are:
- Sequential integers starting from 0
- Immutable once assigned
- Used to track consumer position

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         OFFSET CONCEPTS                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│    Partition 0:                                                             │
│    ┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐           │
│    │  0  │  1  │  2  │  3  │  4  │  5  │  6  │  7  │  8  │  9  │           │
│    └─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘           │
│              ▲                       ▲                       ▲              │
│              │                       │                       │              │
│         Committed               Current                 Log End             │
│          Offset                Position                 Offset              │
│          (2)                     (5)                     (9)                │
│                                                                             │
│    ────────────────────────────────────────────────────────────────────    │
│                                                                             │
│    OFFSET TERMINOLOGY:                                                      │
│                                                                             │
│    • Committed Offset: Last offset successfully processed and saved         │
│    • Current Position: Offset the consumer will read next                   │
│    • Log End Offset: Newest message in the partition                        │
│    • Consumer Lag: Log End Offset - Committed Offset (here: 9 - 2 = 7)     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Auto-commit vs manual commit

**Auto-commit (default):**
- Offsets committed automatically at interval
- Simple but may lose messages on failure
- Risk of duplicate processing after restart

```python
# Auto-commit enabled (default)
config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'auto-commit-group',
    'enable.auto.commit': True,
    'auto.commit.interval.ms': 5000  # Commit every 5 seconds
}
```

**Manual commit (recommended for reliability):**
- You control when offsets are committed
- Commit after successful processing
- Ensures at-least-once delivery

```python
from confluent_kafka import Consumer

config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'manual-commit-group',
    'enable.auto.commit': False  # Disable auto-commit
}

consumer = Consumer(config)
consumer.subscribe(['orders'])

try:
    while True:
        msg = consumer.poll(1.0)

        if msg is None:
            continue
        if msg.error():
            continue

        # Process the message
        process_order(msg.value())

        # Commit AFTER successful processing
        consumer.commit(msg)

finally:
    consumer.close()
```

### Commit strategies

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         COMMIT STRATEGIES                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  STRATEGY 1: Commit after each message                                      │
│  ─────────────────────────────────────                                      │
│  [Read] → [Process] → [Commit] → [Read] → [Process] → [Commit]              │
│                                                                             │
│  Pros: Minimal duplicate processing                                         │
│  Cons: High overhead, slow                                                  │
│  Use: Financial transactions, critical data                                 │
│                                                                             │
│  ───────────────────────────────────────────────────────────────────────   │
│                                                                             │
│  STRATEGY 2: Commit after batch                                             │
│  ─────────────────────────────────                                          │
│  [Read 100] → [Process All] → [Commit]                                      │
│                                                                             │
│  Pros: Better throughput                                                    │
│  Cons: More duplicates on failure                                           │
│  Use: Log processing, analytics                                             │
│                                                                             │
│  ───────────────────────────────────────────────────────────────────────   │
│                                                                             │
│  STRATEGY 3: Async commit with sync on close                                │
│  ───────────────────────────────────────────                                │
│  [Read] → [Process] → [Async Commit] → ... → [Sync Commit on Shutdown]      │
│                                                                             │
│  Pros: Good balance of throughput and reliability                           │
│  Cons: More complex implementation                                          │
│  Use: General purpose applications                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Synchronous vs asynchronous commits

```python
from confluent_kafka import Consumer

consumer = Consumer(config)
consumer.subscribe(['orders'])

try:
    while True:
        messages = consumer.consume(num_messages=100, timeout=1.0)

        for msg in messages:
            if msg.error():
                continue
            process_message(msg)

        # Asynchronous commit (non-blocking, better throughput)
        consumer.commit(asynchronous=True)

finally:
    # Synchronous commit before closing (ensure all commits complete)
    consumer.commit(asynchronous=False)
    consumer.close()
```

### Seeking to specific offsets

```python
from confluent_kafka import Consumer, TopicPartition

consumer = Consumer(config)

# Assign specific partitions (not subscribe)
partitions = [
    TopicPartition('orders', 0),
    TopicPartition('orders', 1)
]
consumer.assign(partitions)

# Seek to beginning
consumer.seek(TopicPartition('orders', 0, 0))  # Partition 0, offset 0

# Seek to end
consumer.seek_to_end([TopicPartition('orders', 0)])

# Seek to specific offset
consumer.seek(TopicPartition('orders', 0, 1000))  # Partition 0, offset 1000

# Seek by timestamp
import time
timestamp_ms = int((time.time() - 3600) * 1000)  # 1 hour ago
offsets = consumer.offsets_for_times([
    TopicPartition('orders', 0, timestamp_ms)
])
for tp in offsets:
    consumer.seek(tp)
```

---

## Message processing patterns

### At-most-once delivery

Messages may be lost but never duplicated.

```python
# At-most-once: Commit BEFORE processing
consumer = Consumer(config)
consumer.subscribe(['events'])

while True:
    msg = consumer.poll(1.0)
    if msg is None or msg.error():
        continue

    # Commit first (if we crash after this, message is lost)
    consumer.commit(msg)

    # Then process (if we crash here, message won't be reprocessed)
    process_event(msg.value())
```

### At-least-once delivery (recommended)

Messages may be duplicated but never lost.

```python
# At-least-once: Commit AFTER processing
consumer = Consumer(config)
consumer.subscribe(['orders'])

while True:
    msg = consumer.poll(1.0)
    if msg is None or msg.error():
        continue

    # Process first
    process_order(msg.value())

    # Commit after (if we crash before commit, message will be reprocessed)
    consumer.commit(msg)
```

### Exactly-once processing

Each message processed exactly once (requires idempotent processing or transactions).

```python
# Exactly-once with idempotent processing
config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'exactly-once-group',
    'enable.auto.commit': False,
    'isolation.level': 'read_committed'  # Only read committed transactions
}

consumer = Consumer(config)
consumer.subscribe(['transactions'])

while True:
    msg = consumer.poll(1.0)
    if msg is None or msg.error():
        continue

    transaction = parse_transaction(msg.value())

    # Idempotent processing with deduplication
    if not already_processed(transaction.id):
        process_transaction(transaction)
        mark_as_processed(transaction.id)

    consumer.commit(msg)
```

---

## Error handling

### Common consumer errors

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    COMMON CONSUMER ERRORS                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ERROR                          CAUSE                  SOLUTION             │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  _PARTITION_EOF                 End of partition       Normal, continue     │
│                                 reached                polling              │
│                                                                             │
│  _UNKNOWN_TOPIC_OR_PART         Topic doesn't exist    Create topic or      │
│                                                        check name           │
│                                                                             │
│  OFFSET_OUT_OF_RANGE            Requested offset       Use auto.offset.     │
│                                 not available          reset to recover     │
│                                                                             │
│  GROUP_COORDINATOR_NOT_         Coordinator not        Retry with backoff   │
│  _AVAILABLE                     available                                   │
│                                                                             │
│  REBALANCE_IN_PROGRESS          Consumer group         Wait for rebalance   │
│                                 rebalancing            to complete          │
│                                                                             │
│  COMMIT_FAILED                  Commit rejected        Rebalance occurred,  │
│                                                        partitions revoked   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Robust error handling pattern

```python
from confluent_kafka import Consumer, KafkaError, KafkaException
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'robust-consumer',
    'enable.auto.commit': False,
    'auto.offset.reset': 'earliest'
}

def create_consumer():
    return Consumer(config)

def process_message(msg):
    """Process a single message. Raises on failure."""
    data = msg.value().decode('utf-8')
    # Your processing logic here
    logger.info(f"Processed: {data}")

def run_consumer():
    consumer = create_consumer()
    consumer.subscribe(['events'])

    consecutive_errors = 0
    max_consecutive_errors = 10

    try:
        while True:
            try:
                msg = consumer.poll(1.0)

                if msg is None:
                    continue

                if msg.error():
                    error = msg.error()

                    if error.code() == KafkaError._PARTITION_EOF:
                        # Normal - end of partition
                        logger.debug(f"Reached end of {msg.topic()}[{msg.partition()}]")
                        continue
                    elif error.code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
                        logger.error(f"Unknown topic: {msg.topic()}")
                        continue
                    else:
                        raise KafkaException(error)

                # Process the message
                try:
                    process_message(msg)
                    consumer.commit(msg)
                    consecutive_errors = 0
                except Exception as e:
                    logger.error(f"Processing error: {e}")
                    consecutive_errors += 1

                    if consecutive_errors >= max_consecutive_errors:
                        logger.critical("Too many consecutive errors, exiting")
                        break

                    # Don't commit - message will be reprocessed
                    time.sleep(1)  # Brief pause before retry

            except KafkaException as e:
                logger.error(f"Kafka error: {e}")
                consecutive_errors += 1
                time.sleep(5)  # Longer pause for infrastructure issues

    finally:
        logger.info("Closing consumer")
        consumer.close()

if __name__ == '__main__':
    run_consumer()
```

### Dead letter queue pattern

Handle poison messages that can't be processed:

```python
from confluent_kafka import Consumer, Producer

config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'dlq-consumer',
    'enable.auto.commit': False
}

consumer = Consumer(config)
dlq_producer = Producer({'bootstrap.servers': 'localhost:9092'})

consumer.subscribe(['orders'])

MAX_RETRIES = 3

while True:
    msg = consumer.poll(1.0)
    if msg is None or msg.error():
        continue

    retries = 0
    success = False

    while retries < MAX_RETRIES and not success:
        try:
            process_order(msg.value())
            success = True
        except Exception as e:
            retries += 1
            logger.warning(f"Retry {retries}/{MAX_RETRIES}: {e}")
            time.sleep(2 ** retries)  # Exponential backoff

    if not success:
        # Send to dead letter queue
        dlq_producer.produce(
            'orders-dlq',
            key=msg.key(),
            value=msg.value(),
            headers=[
                ('original_topic', msg.topic().encode()),
                ('original_partition', str(msg.partition()).encode()),
                ('original_offset', str(msg.offset()).encode()),
                ('error', str(e).encode())
            ]
        )
        dlq_producer.flush()
        logger.error(f"Message sent to DLQ: {msg.offset()}")

    consumer.commit(msg)
```

---

## Performance tuning

### Fetch configuration

```python
# High-throughput consumer
high_throughput_config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'high-throughput',

    # Fetch settings
    'fetch.min.bytes': 1048576,       # Wait for 1MB of data
    'fetch.max.wait.ms': 500,          # Or 500ms, whichever comes first
    'fetch.max.bytes': 52428800,       # Max 50MB per fetch
    'max.partition.fetch.bytes': 1048576,  # Max 1MB per partition

    # Polling settings
    'max.poll.records': 1000,          # Process 1000 records per poll
    'max.poll.interval.ms': 300000,    # 5 minutes max between polls
}

# Low-latency consumer
low_latency_config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'low-latency',

    # Minimal fetch delay
    'fetch.min.bytes': 1,              # Fetch immediately
    'fetch.max.wait.ms': 100,          # Max 100ms wait

    # Smaller batches for faster processing
    'max.poll.records': 100,           # Process 100 records per poll
}
```

### Consumer lag monitoring

```python
from confluent_kafka import Consumer
from confluent_kafka.admin import AdminClient

def get_consumer_lag(consumer, topics):
    """Calculate consumer lag for all assigned partitions."""
    lag_info = {}

    # Get assigned partitions
    assignment = consumer.assignment()

    for tp in assignment:
        # Get current position
        position = consumer.position([tp])[0].offset

        # Get end offset (high watermark)
        low, high = consumer.get_watermark_offsets(tp)

        lag = high - position if position >= 0 else high

        lag_info[f"{tp.topic}-{tp.partition}"] = {
            'current_offset': position,
            'end_offset': high,
            'lag': lag
        }

    return lag_info

# Usage
consumer = Consumer(config)
consumer.subscribe(['orders'])

# After some polling...
lag = get_consumer_lag(consumer, ['orders'])
for partition, info in lag.items():
    print(f"{partition}: lag={info['lag']} messages")
```

### Session and heartbeat tuning

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SESSION AND HEARTBEAT TIMING                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Timeline:                                                                  │
│  ─────────                                                                  │
│                                                                             │
│  0s    3s    6s    9s    12s   15s   ...   45s                             │
│  │     │     │     │      │     │           │                              │
│  HB    HB    HB    HB     HB    HB          TIMEOUT                        │
│  ▼     ▼     ▼     ▼      ▼     ▼           ▼                              │
│  ┌─────┬─────┬─────┬──────┬─────┬───────────┐                              │
│  │     │     │     │      │     │           │                              │
│  └─────┴─────┴─────┴──────┴─────┴───────────┘                              │
│        ▲                                    ▲                               │
│        │                                    │                               │
│  heartbeat.interval.ms: 3000     session.timeout.ms: 45000                 │
│                                                                             │
│  RULE: session.timeout.ms >= 3 * heartbeat.interval.ms                     │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  TUNING GUIDELINES:                                                         │
│                                                                             │
│  Fast Detection (unstable network):   Slow Detection (stable network):     │
│  session.timeout.ms: 10000            session.timeout.ms: 45000            │
│  heartbeat.interval.ms: 3000          heartbeat.interval.ms: 15000         │
│                                                                             │
│  Fast detection = quicker failover but more false positives                 │
│  Slow detection = fewer false positives but slower failover                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Hands-on exercises

### Exercise 1: Basic consumer

Create a consumer that reads and prints all messages from a topic.

```bash
# First, create a topic and produce some messages
docker exec -it kafka kafka-topics --create --topic exercise-consumer \
    --bootstrap-server localhost:9092 --partitions 3

docker exec -it kafka kafka-console-producer --topic exercise-consumer \
    --bootstrap-server localhost:9092
# Type some messages, then Ctrl+D
```

```python
# exercise_basic_consumer.py
from confluent_kafka import Consumer

config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'exercise-group',
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(config)
consumer.subscribe(['exercise-consumer'])

try:
    message_count = 0
    while message_count < 10:  # Read 10 messages
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Error: {msg.error()}")
            continue

        print(f"[{msg.partition()}:{msg.offset()}] {msg.value().decode()}")
        message_count += 1
finally:
    consumer.close()
```

### Exercise 2: Manual offset commit

Modify the consumer to use manual commits:

```python
# exercise_manual_commit.py
from confluent_kafka import Consumer

config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'manual-commit-exercise',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False  # Disable auto-commit
}

consumer = Consumer(config)
consumer.subscribe(['exercise-consumer'])

try:
    batch = []
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            if batch:
                # Process and commit batch
                for m in batch:
                    print(f"Processing: {m.value().decode()}")
                consumer.commit()
                print(f"Committed {len(batch)} messages")
                batch = []
            continue
        if msg.error():
            continue

        batch.append(msg)

        if len(batch) >= 5:  # Commit every 5 messages
            for m in batch:
                print(f"Processing: {m.value().decode()}")
            consumer.commit()
            print(f"Committed {len(batch)} messages")
            batch = []

except KeyboardInterrupt:
    pass
finally:
    if batch:
        consumer.commit()
    consumer.close()
```

### Exercise 3: Seeking to offset

Practice seeking to different positions:

```python
# exercise_seek.py
from confluent_kafka import Consumer, TopicPartition
import time

config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'seek-exercise-' + str(int(time.time())),  # Unique group
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(config)

# Assign partition 0 directly
tp = TopicPartition('exercise-consumer', 0)
consumer.assign([tp])

# Get watermarks
low, high = consumer.get_watermark_offsets(tp)
print(f"Partition 0: offsets {low} to {high}")

# Seek to middle
middle = (low + high) // 2
consumer.seek(TopicPartition('exercise-consumer', 0, middle))
print(f"Seeking to offset {middle}")

# Read a few messages
for _ in range(3):
    msg = consumer.poll(1.0)
    if msg and not msg.error():
        print(f"Offset {msg.offset()}: {msg.value().decode()}")

consumer.close()
```

---

## Key takeaways

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CONSUMER KEY TAKEAWAYS                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ✓ Consumers read messages from topics and track progress via offsets      │
│                                                                             │
│  ✓ Use manual commits for at-least-once delivery (commit AFTER processing) │
│                                                                             │
│  ✓ auto.offset.reset controls where new consumers start:                   │
│    - 'earliest' = from beginning                                            │
│    - 'latest' = only new messages                                           │
│                                                                             │
│  ✓ Monitor consumer lag to detect processing bottlenecks                   │
│                                                                             │
│  ✓ Use dead letter queues for poison messages that can't be processed      │
│                                                                             │
│  ✓ Tune fetch.min.bytes and fetch.max.wait.ms for your latency needs       │
│                                                                             │
│  ✓ Set max.poll.interval.ms based on your processing time requirements     │
│                                                                             │
│  ✓ Always close consumers gracefully to trigger proper cleanup             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

**[← Back to Producers](./06_producers.md)** | **[Next: Consumer Groups →](./08_consumer_groups.md)**

[↑ Back to Top](#lesson-07-kafka-consumers)
