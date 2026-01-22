# Lesson 12: Exactly-once semantics

**[← Back to Serialization](./11_serialization.md)** | **[Next: Module 4 →](../module_4_advanced/README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Exactly_Once-blue)

## Overview

Exactly-once semantics (EOS) ensures that messages are processed exactly one time - no duplicates, no data loss. This lesson covers idempotent producers, transactions, and the exactly-once consumer pattern.

**Learning objectives:**
- Understand the three delivery guarantees in messaging
- Implement idempotent producers to prevent duplicates
- Use Kafka transactions for atomic multi-partition writes
- Build exactly-once processing pipelines

**Prerequisites:** Lessons 09-11 completed

**Estimated time:** 45 minutes

---

## Table of contents

- [Delivery guarantees](#delivery-guarantees)
- [Idempotent producers](#idempotent-producers)
- [Kafka transactions](#kafka-transactions)
- [Exactly-once consumers](#exactly-once-consumers)
- [Kafka Streams EOS](#kafka-streams-eos)
- [Production considerations](#production-considerations)
- [Hands-on exercises](#hands-on-exercises)
- [Key takeaways](#key-takeaways)

---

## Delivery guarantees

### The three guarantees

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DELIVERY GUARANTEES                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  AT-MOST-ONCE (may lose messages)                                           │
│  ────────────────────────────────                                           │
│                                                                             │
│  Producer ──► Broker (no ack waited)                                        │
│                                                                             │
│  Messages: [1] [2] [3] [?] [5]    ← Message 4 may be lost                  │
│                                                                             │
│  Config: acks=0                                                             │
│  Use case: Metrics where occasional loss is acceptable                      │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  AT-LEAST-ONCE (may have duplicates)                                        │
│  ───────────────────────────────────                                        │
│                                                                             │
│  Producer ──► Broker ──► Ack ──► Producer retries if no ack                │
│                                                                             │
│  Messages: [1] [2] [3] [3] [4] [5]    ← Message 3 sent twice (retry)       │
│                                                                             │
│  Config: acks=all, retries=MAX                                              │
│  Use case: Most applications (handle duplicates in consumer)                │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  EXACTLY-ONCE (no loss, no duplicates)                                      │
│  ─────────────────────────────────────                                      │
│                                                                             │
│  Producer ──► Broker (idempotent) ──► Consumer (transactional)             │
│                                                                             │
│  Messages: [1] [2] [3] [4] [5]    ← Each message processed exactly once    │
│                                                                             │
│  Config: enable.idempotence=true, transactional.id set                      │
│  Use case: Financial transactions, inventory, critical data                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Why is exactly-once hard?

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    THE DUPLICATE PROBLEM                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  SCENARIO: Producer retry after timeout                                     │
│                                                                             │
│  Time                                                                       │
│  ─────►                                                                     │
│                                                                             │
│  Producer                    Broker                                         │
│  ────────                    ──────                                         │
│                                                                             │
│  1. Send msg-1 ─────────────► Receives & writes                            │
│                                     │                                       │
│  2. Timeout (no ack)                ▼                                       │
│     waiting...              ACK sent ────► Network drops ACK!              │
│                                                                             │
│  3. Retry msg-1 ────────────► Receives & writes AGAIN                      │
│                                     │                                       │
│  4. Receives ack ◄────────── ACK sent                                      │
│                                                                             │
│  RESULT: msg-1 written TWICE to the log!                                    │
│                                                                             │
│  [msg-1] [msg-1] [msg-2] [msg-3] ...   ← DUPLICATE!                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Idempotent producers

### How idempotence works

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    IDEMPOTENT PRODUCER                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Each producer gets a unique Producer ID (PID)                              │
│  Each message gets a sequence number per partition                          │
│                                                                             │
│  Producer (PID: 1)                Broker                                    │
│  ─────────────────                ──────                                    │
│                                                                             │
│  1. Send (PID=1, seq=0) ────────► Store: expects seq=0 ✓                   │
│                                   Written to partition                      │
│                                                                             │
│  2. Send (PID=1, seq=1) ────────► Store: expects seq=1 ✓                   │
│                                   Written to partition                      │
│                                                                             │
│  3. Timeout, retry                                                          │
│     Send (PID=1, seq=1) ────────► Store: already has seq=1                 │
│                                   DUPLICATE DETECTED!                       │
│                                   Returns ack, no write                     │
│                                                                             │
│  LOG STATE:                                                                 │
│  ┌───────────┬───────────┬───────────┐                                     │
│  │ PID=1     │ PID=1     │           │                                     │
│  │ seq=0     │ seq=1     │  (empty)  │  ← No duplicate written!            │
│  │ msg-1     │ msg-2     │           │                                     │
│  └───────────┴───────────┴───────────┘                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Enabling idempotence

```python
from confluent_kafka import Producer

# Idempotent producer configuration
config = {
    'bootstrap.servers': 'localhost:9092',

    # Enable idempotence
    'enable.idempotence': True,

    # These are automatically set when idempotence is enabled:
    # 'acks': 'all',
    # 'retries': 2147483647,  # MAX_INT
    # 'max.in.flight.requests.per.connection': 5
}

producer = Producer(config)

def delivery_callback(err, msg):
    if err is not None:
        print(f"Delivery failed: {err}")
    else:
        print(f"Delivered to {msg.topic()} [{msg.partition()}] @ {msg.offset()}")

# Produce messages - duplicates are automatically prevented
for i in range(100):
    producer.produce(
        'orders',
        key=f'order-{i}'.encode(),
        value=f'{{"id": {i}, "amount": {i * 10}}}'.encode(),
        callback=delivery_callback
    )
    producer.poll(0)

producer.flush()
```

### Idempotence limitations

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    IDEMPOTENCE SCOPE                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  WHAT IDEMPOTENCE GUARANTEES:                                               │
│  ✓ No duplicates within a single producer session                          │
│  ✓ Ordering preserved within a partition                                    │
│  ✓ Retries are safe                                                         │
│                                                                             │
│  WHAT IDEMPOTENCE DOES NOT GUARANTEE:                                       │
│  ✗ Cross-session deduplication (producer restart = new PID)                 │
│  ✗ Atomicity across multiple partitions                                     │
│  ✗ End-to-end exactly-once (need transactions for that)                     │
│                                                                             │
│  EXAMPLE - Idempotence fails across restart:                                │
│                                                                             │
│  Session 1 (PID=1):  [seq=0: msg-A] [seq=1: msg-B] ── CRASH                │
│                                                                             │
│  Session 2 (PID=2):  [seq=0: msg-B] ← msg-B sent again with new PID        │
│                       ^ DUPLICATE! Different PID, broker accepts it         │
│                                                                             │
│  SOLUTION: Use transactions for cross-session exactly-once                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Kafka transactions

### Transaction overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    KAFKA TRANSACTIONS                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Transactions enable ATOMIC writes across multiple partitions/topics        │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                        TRANSACTION                                    │  │
│  │                                                                       │  │
│  │    ┌─────────────┐     ┌─────────────┐     ┌─────────────┐          │  │
│  │    │  Write to   │     │  Write to   │     │   Commit    │          │  │
│  │    │  Topic A    │     │  Topic B    │     │   Offset    │          │  │
│  │    │  Partition 0│     │  Partition 2│     │  to Topic C │          │  │
│  │    └─────────────┘     └─────────────┘     └─────────────┘          │  │
│  │                                                                       │  │
│  │                    ALL OR NOTHING                                     │  │
│  │                                                                       │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                              │                                              │
│                              ▼                                              │
│              ┌───────────────────────────────────┐                         │
│              │          COMMIT or ABORT          │                         │
│              │                                   │                         │
│              │  COMMIT: All writes visible       │                         │
│              │  ABORT:  All writes discarded     │                         │
│              └───────────────────────────────────┘                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Transactional producer

```python
from confluent_kafka import Producer
import uuid

# Transactional producer configuration
config = {
    'bootstrap.servers': 'localhost:9092',

    # Unique transactional ID (survives restarts)
    'transactional.id': f'order-processor-{uuid.uuid4()}',

    # Idempotence is automatically enabled
    'enable.idempotence': True,

    # Transaction timeout
    'transaction.timeout.ms': 60000
}

producer = Producer(config)

# Initialize transactions (must be called once before any transactions)
producer.init_transactions()

def process_order_transactionally(order):
    """Process an order with exactly-once guarantees."""

    try:
        # Begin transaction
        producer.begin_transaction()

        # Write to multiple topics atomically
        producer.produce(
            'orders',
            key=order['id'].encode(),
            value=str(order).encode()
        )

        producer.produce(
            'order-events',
            key=order['id'].encode(),
            value=f'{{"event": "created", "order_id": "{order["id"]}"}}'.encode()
        )

        producer.produce(
            'notifications',
            key=order['customer_id'].encode(),
            value=f'{{"type": "order_created", "order_id": "{order["id"]}"}}'.encode()
        )

        # Commit transaction - all writes become visible
        producer.commit_transaction()
        print(f"Transaction committed for order {order['id']}")

    except Exception as e:
        # Abort transaction - all writes discarded
        producer.abort_transaction()
        print(f"Transaction aborted for order {order['id']}: {e}")
        raise

# Example usage
orders = [
    {'id': 'ORD-001', 'customer_id': 'C-1', 'amount': 99.99},
    {'id': 'ORD-002', 'customer_id': 'C-2', 'amount': 149.99},
]

for order in orders:
    process_order_transactionally(order)
```

### Read-process-write pattern

The most common exactly-once pattern: consume from one topic, process, write to another.

```python
from confluent_kafka import Consumer, Producer, TopicPartition

# Consumer configuration
consumer_config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'order-enricher',
    'enable.auto.commit': False,  # Manual commit via transaction
    'isolation.level': 'read_committed'  # Only read committed messages
}

# Transactional producer
producer_config = {
    'bootstrap.servers': 'localhost:9092',
    'transactional.id': 'order-enricher-tx-1',
    'enable.idempotence': True
}

consumer = Consumer(consumer_config)
producer = Producer(producer_config)

# Initialize transactions
producer.init_transactions()

consumer.subscribe(['raw-orders'])

try:
    while True:
        msg = consumer.poll(1.0)

        if msg is None:
            continue
        if msg.error():
            continue

        try:
            # Begin transaction
            producer.begin_transaction()

            # Process message
            order = process_raw_order(msg.value())

            # Write enriched order to output topic
            producer.produce(
                'enriched-orders',
                key=msg.key(),
                value=str(order).encode()
            )

            # Send consumer offset as part of transaction
            producer.send_offsets_to_transaction(
                [TopicPartition(msg.topic(), msg.partition(), msg.offset() + 1)],
                consumer.consumer_group_metadata()
            )

            # Commit transaction
            producer.commit_transaction()

        except Exception as e:
            producer.abort_transaction()
            print(f"Transaction aborted: {e}")

finally:
    consumer.close()
```

---

## Exactly-once consumers

### Transactional consumer configuration

```python
from confluent_kafka import Consumer

config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'exactly-once-consumers',
    'auto.offset.reset': 'earliest',

    # Critical for exactly-once
    'enable.auto.commit': False,

    # Only read committed (completed) transactions
    'isolation.level': 'read_committed'
}

consumer = Consumer(config)
```

### Isolation levels explained

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ISOLATION LEVELS                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  read_uncommitted (default):                                                │
│  ────────────────────────────                                               │
│  Consumer sees ALL messages including uncommitted transactions              │
│                                                                             │
│  Partition:  [1] [2] [TX-START] [3] [4] [TX-END] [5]                       │
│  Consumer:   ▲   ▲       ▲       ▲   ▲     ▲      ▲                        │
│              Sees everything (including uncommitted 3, 4)                   │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  read_committed:                                                            │
│  ───────────────                                                            │
│  Consumer only sees committed transactions                                  │
│                                                                             │
│  Partition:  [1] [2] [TX-START] [3] [4] [TX-END] [5]                       │
│                                                                             │
│  If TX commits:                                                             │
│  Consumer:   ▲   ▲              ▲   ▲            ▲                         │
│              Sees 1, 2, waits..., then 3, 4, 5                             │
│                                                                             │
│  If TX aborts:                                                              │
│  Consumer:   ▲   ▲                               ▲                         │
│              Sees 1, 2, (skips 3, 4), then 5                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Idempotent consumer pattern

When you can't use transactions, make your consumer idempotent:

```python
from confluent_kafka import Consumer
import redis

# Use Redis (or database) for deduplication
redis_client = redis.Redis(host='localhost', port=6379)

config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'idempotent-processor',
    'enable.auto.commit': False,
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(config)
consumer.subscribe(['orders'])

def is_duplicate(message_id: str) -> bool:
    """Check if message was already processed."""
    return redis_client.exists(f"processed:{message_id}")

def mark_processed(message_id: str, ttl_seconds: int = 86400):
    """Mark message as processed with TTL."""
    redis_client.setex(f"processed:{message_id}", ttl_seconds, "1")

def process_order(order: dict) -> bool:
    """Process order with idempotency check."""
    order_id = order['id']

    if is_duplicate(order_id):
        print(f"Skipping duplicate: {order_id}")
        return False

    # Process the order
    print(f"Processing order: {order_id}")

    # Business logic here...

    # Mark as processed AFTER successful processing
    mark_processed(order_id)
    return True

try:
    while True:
        msg = consumer.poll(1.0)

        if msg is None:
            continue
        if msg.error():
            continue

        order = json.loads(msg.value())
        process_order(order)

        # Commit offset after processing
        consumer.commit(msg)

finally:
    consumer.close()
```

---

## Kafka Streams EOS

### Enabling exactly-once in Kafka Streams

Kafka Streams provides the simplest exactly-once experience:

```java
// Java Kafka Streams configuration
Properties props = new Properties();
props.put(StreamsConfig.APPLICATION_ID_CONFIG, "order-processor");
props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");

// Enable exactly-once semantics
props.put(StreamsConfig.PROCESSING_GUARANTEE_CONFIG,
          StreamsConfig.EXACTLY_ONCE_V2);  // Use V2 for Kafka 2.5+

// Build topology
StreamsBuilder builder = new StreamsBuilder();

builder.stream("raw-orders")
    .mapValues(order -> enrichOrder(order))
    .to("enriched-orders");

KafkaStreams streams = new KafkaStreams(builder.build(), props);
streams.start();
```

### How Kafka Streams achieves EOS

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    KAFKA STREAMS EXACTLY-ONCE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Kafka Streams automatically:                                               │
│                                                                             │
│  1. Uses transactional producer internally                                  │
│  2. Commits consumer offsets within the transaction                         │
│  3. Uses read_committed isolation level                                     │
│  4. Handles state store updates atomically                                  │
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                     KAFKA STREAMS TASK                              │    │
│  │                                                                     │    │
│  │  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐     │    │
│  │  │  Read    │───►│ Process  │───►│  Update  │───►│  Write   │     │    │
│  │  │  Input   │    │  Record  │    │  State   │    │  Output  │     │    │
│  │  └──────────┘    └──────────┘    └──────────┘    └──────────┘     │    │
│  │                                                                     │    │
│  │                  ALL WRAPPED IN TRANSACTION                         │    │
│  │                                                                     │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  If any step fails → Transaction aborts → No partial updates               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Production considerations

### Performance impact

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    EXACTLY-ONCE PERFORMANCE                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  IDEMPOTENT PRODUCER:                                                       │
│  • Overhead: ~3-5% latency increase                                         │
│  • Throughput: Minimal impact                                               │
│  • Recommendation: Enable by default for all producers                      │
│                                                                             │
│  TRANSACTIONS:                                                              │
│  • Overhead: ~10-20% latency increase                                       │
│  • Throughput: Reduced due to synchronization                               │
│  • Recommendation: Use when atomicity required                              │
│                                                                             │
│  read_committed CONSUMER:                                                   │
│  • Latency: May wait for transaction commit                                 │
│  • Throughput: Same as read_uncommitted once committed                      │
│  • Recommendation: Use when consuming transactional topics                  │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  BENCHMARK COMPARISON (1M messages):                                        │
│                                                                             │
│  Configuration                 Throughput      Latency (p99)                │
│  ─────────────────────────────────────────────────────────────────────     │
│  acks=1, no idempotence        180,000 msg/s   5ms                          │
│  acks=all, idempotent          165,000 msg/s   8ms                          │
│  acks=all, transactional       120,000 msg/s   15ms                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### When to use each approach

| Scenario | Approach | Config |
|----------|----------|--------|
| **General production** | Idempotent producer | `enable.idempotence=true` |
| **Multi-topic writes** | Transactions | `transactional.id` set |
| **Read-process-write** | Full EOS | Transaction + offset commit |
| **Stream processing** | Kafka Streams EOS | `exactly_once_v2` |
| **Legacy systems** | Idempotent consumer | Deduplication logic |

### Troubleshooting

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    COMMON ISSUES                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ISSUE: ProducerFencedException                                             │
│  CAUSE: Another producer with same transactional.id is active               │
│  FIX: Use unique transactional.id per producer instance                     │
│       transactional.id = f"processor-{hostname}-{instance}"                 │
│                                                                             │
│  ISSUE: Transaction timeout                                                 │
│  CAUSE: Transaction took longer than transaction.timeout.ms                 │
│  FIX: Increase timeout or process smaller batches                           │
│       transaction.timeout.ms = 120000  # 2 minutes                          │
│                                                                             │
│  ISSUE: InvalidTxnStateException                                            │
│  CAUSE: Transaction operations out of order                                 │
│  FIX: Ensure init_transactions() called before begin_transaction()          │
│                                                                             │
│  ISSUE: Consumer stuck (no messages)                                        │
│  CAUSE: Reading uncommitted topic with read_committed                       │
│  FIX: Ensure producer commits transactions, or use read_uncommitted         │
│                                                                             │
│  ISSUE: OutOfOrderSequenceException                                         │
│  CAUSE: Sequence number gap (producer restart without clean shutdown)       │
│  FIX: Handle exception, recreate producer with new transactional.id         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Hands-on exercises

### Exercise 1: Enable idempotence

```python
# exercise_idempotent.py
# TODO: Create an idempotent producer and verify no duplicates

from confluent_kafka import Producer, Consumer
import time

def create_idempotent_producer():
    config = {
        'bootstrap.servers': 'localhost:9092',
        # TODO: Add idempotence configuration
    }
    return Producer(config)

def simulate_network_issues(producer, topic, message):
    """Simulate sending same message multiple times (like network retry)."""
    # In real scenario, this would happen due to network timeout
    for attempt in range(3):
        producer.produce(topic, value=message.encode())
        producer.poll(0)
        print(f"Attempt {attempt + 1}: Sent message")

    producer.flush()

# TODO: Verify that despite 3 send attempts, only 1 message exists in topic
```

### Exercise 2: Transactional producer

```python
# exercise_transaction.py
# TODO: Implement atomic writes to multiple topics

from confluent_kafka import Producer

def transfer_funds(from_account, to_account, amount):
    """
    Atomically:
    1. Debit from_account
    2. Credit to_account
    3. Log the transaction
    """
    producer = Producer({
        'bootstrap.servers': 'localhost:9092',
        'transactional.id': 'fund-transfer-1',
        'enable.idempotence': True
    })

    producer.init_transactions()

    try:
        producer.begin_transaction()

        # TODO: Write debit event to 'account-debits' topic
        # TODO: Write credit event to 'account-credits' topic
        # TODO: Write audit log to 'transactions' topic

        producer.commit_transaction()
        return True

    except Exception as e:
        producer.abort_transaction()
        return False

# Test with intentional failure in the middle
```

### Exercise 3: Read-process-write exactly-once

Build a complete pipeline that:
1. Consumes orders from `raw-orders`
2. Enriches with customer data
3. Writes to `enriched-orders`
4. Guarantees exactly-once end-to-end

---

## Key takeaways

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    EXACTLY-ONCE KEY TAKEAWAYS                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ✓ Enable idempotence for ALL producers (enable.idempotence=true)          │
│                                                                             │
│  ✓ Use transactions when writing atomically to multiple topics/partitions  │
│                                                                             │
│  ✓ For read-process-write, commit offsets within the transaction           │
│                                                                             │
│  ✓ Consumers reading transactional topics should use read_committed        │
│                                                                             │
│  ✓ Kafka Streams provides the simplest exactly-once experience             │
│                                                                             │
│  ✓ transactional.id must be unique per producer instance                   │
│                                                                             │
│  ✓ Exactly-once has ~10-20% performance overhead - use when needed         │
│                                                                             │
│  ✓ When transactions aren't possible, make consumers idempotent            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

**[← Back to Serialization](./11_serialization.md)** | **[Next: Module 4 - Advanced →](../module_4_advanced/README.md)**

[↑ Back to Top](#lesson-12-exactly-once-semantics)
