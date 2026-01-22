# Lesson 08: Consumer groups

**[← Back to Module 2](./README.md)** | **[Next: Module 3 →](../module_3_intermediate/README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Consumer_Groups-blue)

## Overview

Consumer groups enable scalable, fault-tolerant message processing in Kafka. This lesson covers how consumer groups work, rebalancing, and best practices for building reliable consumer applications.

**Learning objectives:**
- Understand consumer group mechanics and partition assignment
- Learn how rebalancing works and how to handle it
- Implement cooperative rebalancing for minimal disruption
- Design consumer applications for high availability

**Prerequisites:** Lesson 07 (Consumers)

**Estimated time:** 45 minutes

---

## Table of contents

- [Consumer group fundamentals](#consumer-group-fundamentals)
- [Partition assignment](#partition-assignment)
- [Rebalancing](#rebalancing)
- [Group coordinator](#group-coordinator)
- [Static membership](#static-membership)
- [Multi-topic consumption](#multi-topic-consumption)
- [Monitoring consumer groups](#monitoring-consumer-groups)
- [Hands-on exercises](#hands-on-exercises)
- [Key takeaways](#key-takeaways)

---

## Consumer group fundamentals

### What is a consumer group?

A consumer group is a set of consumers that work together to consume messages from topics. Each partition is assigned to exactly one consumer within the group, enabling parallel processing.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CONSUMER GROUP CONCEPT                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│    Topic: orders (6 partitions)                                             │
│    ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                        │
│    │ P0  │ │ P1  │ │ P2  │ │ P3  │ │ P4  │ │ P5  │                        │
│    └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘                        │
│       │       │       │       │       │       │                            │
│       └───────┴───────┼───────┴───────┴───────┘                            │
│                       │                                                     │
│                       ▼                                                     │
│    ┌─────────────────────────────────────────────────────────────┐         │
│    │                   Consumer Group: order-processors           │         │
│    │                                                              │         │
│    │    ┌──────────┐    ┌──────────┐    ┌──────────┐             │         │
│    │    │Consumer 1│    │Consumer 2│    │Consumer 3│             │         │
│    │    │  P0, P1  │    │  P2, P3  │    │  P4, P5  │             │         │
│    │    └──────────┘    └──────────┘    └──────────┘             │         │
│    │                                                              │         │
│    └─────────────────────────────────────────────────────────────┘         │
│                                                                             │
│    KEY RULES:                                                               │
│    • Each partition → exactly ONE consumer in the group                     │
│    • Each consumer → can have MULTIPLE partitions                           │
│    • No partition → consumed by multiple consumers in same group            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Consumer group vs independent consumers

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              CONSUMER GROUP vs INDEPENDENT CONSUMERS                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  CONSUMER GROUP (Same group.id)         INDEPENDENT (Different group.id)   │
│  ───────────────────────────────        ─────────────────────────────────   │
│                                                                             │
│    Topic                                  Topic                             │
│    ┌─────┬─────┬─────┐                   ┌─────┬─────┬─────┐               │
│    │ P0  │ P1  │ P2  │                   │ P0  │ P1  │ P2  │               │
│    └──┬──┴──┬──┴──┬──┘                   └──┬──┴──┬──┴──┬──┘               │
│       │     │     │                         │     │     │                   │
│       │     │     │                         ├─────┼─────┤                   │
│       ▼     ▼     ▼                         │     │     │                   │
│    ┌────┐ ┌────┐ ┌────┐                  ┌──▼──┐ │     │                   │
│    │ C1 │ │ C2 │ │ C3 │                  │ C1  │◄┴─────┘                   │
│    └────┘ └────┘ └────┘                  └─────┘                           │
│                                             ▲                               │
│    Each message                          ┌──┴──┐                           │
│    processed ONCE                        │ C2  │◄───────                   │
│                                          └─────┘                           │
│                                                                             │
│                                          Each message                       │
│                                          processed by BOTH                  │
│                                                                             │
│  USE CASE: Load balancing               USE CASE: Fan-out / Pub-Sub        │
│  (order processing)                     (multiple independent systems)     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Scaling with consumer groups

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SCALING CONSUMERS                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  SCENARIO 1: 3 Partitions, 1 Consumer                                       │
│  ┌─────┐ ┌─────┐ ┌─────┐                                                   │
│  │ P0  │ │ P1  │ │ P2  │ ───────────► ┌────────────┐                       │
│  └─────┘ └─────┘ └─────┘              │ Consumer 1 │  ← All partitions     │
│                                        └────────────┘                       │
│                                                                             │
│  SCENARIO 2: 3 Partitions, 2 Consumers                                      │
│  ┌─────┐ ┌─────┐                                                           │
│  │ P0  │ │ P1  │ ──────────────────► ┌────────────┐                        │
│  └─────┘ └─────┘                      │ Consumer 1 │  ← 2 partitions       │
│  ┌─────┐                              └────────────┘                        │
│  │ P2  │ ──────────────────────────► ┌────────────┐                        │
│  └─────┘                              │ Consumer 2 │  ← 1 partition        │
│                                        └────────────┘                       │
│                                                                             │
│  SCENARIO 3: 3 Partitions, 3 Consumers (Optimal)                            │
│  ┌─────┐                              ┌────────────┐                        │
│  │ P0  │ ──────────────────────────► │ Consumer 1 │  ← 1 partition        │
│  └─────┘                              └────────────┘                        │
│  ┌─────┐                              ┌────────────┐                        │
│  │ P1  │ ──────────────────────────► │ Consumer 2 │  ← 1 partition        │
│  └─────┘                              └────────────┘                        │
│  ┌─────┐                              ┌────────────┐                        │
│  │ P2  │ ──────────────────────────► │ Consumer 3 │  ← 1 partition        │
│  └─────┘                              └────────────┘                        │
│                                                                             │
│  SCENARIO 4: 3 Partitions, 4 Consumers (Over-provisioned)                   │
│  ┌─────┐                              ┌────────────┐                        │
│  │ P0  │ ──────────────────────────► │ Consumer 1 │                        │
│  └─────┘                              └────────────┘                        │
│  ┌─────┐                              ┌────────────┐                        │
│  │ P1  │ ──────────────────────────► │ Consumer 2 │                        │
│  └─────┘                              └────────────┘                        │
│  ┌─────┐                              ┌────────────┐                        │
│  │ P2  │ ──────────────────────────► │ Consumer 3 │                        │
│  └─────┘                              └────────────┘                        │
│                                        ┌────────────┐                        │
│                     (nothing) ───────► │ Consumer 4 │  ← IDLE!             │
│                                        └────────────┘                        │
│                                                                             │
│  RULE: Consumers > Partitions = Idle consumers (wasted resources)           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Partition assignment

### Assignment strategies

Kafka supports multiple partition assignment strategies:

| Strategy | Description | Use Case |
|----------|-------------|----------|
| `RangeAssignor` | Assigns partitions in ranges per topic | Default, simple |
| `RoundRobinAssignor` | Distributes partitions evenly | Multi-topic consumers |
| `StickyAssignor` | Minimizes partition movement | Reduce rebalance impact |
| `CooperativeStickyAssignor` | Incremental rebalance | Production recommended |

```python
# Configure partition assignment strategy
config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'my-group',
    'partition.assignment.strategy': 'cooperative-sticky'  # Recommended
}
```

### Range assignment

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RANGE ASSIGNMENT                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Topics: orders (3 partitions), payments (3 partitions)                     │
│  Consumers: C1, C2                                                          │
│                                                                             │
│  Step 1: Sort partitions by topic, then by partition number                 │
│  Step 2: Assign ranges to each consumer                                     │
│                                                                             │
│    orders                    payments                                       │
│    ┌────┬────┬────┐         ┌────┬────┬────┐                               │
│    │ P0 │ P1 │ P2 │         │ P0 │ P1 │ P2 │                               │
│    └─┬──┴─┬──┴──┬─┘         └─┬──┴─┬──┴──┬─┘                               │
│      │    │     │             │    │     │                                  │
│      │    ▼     ▼             │    ▼     ▼                                  │
│      │  ┌──────────┐          │  ┌──────────┐                               │
│      │  │ C2       │          │  │ C2       │                               │
│      │  │ orders-1 │          │  │payments-1│                               │
│      │  │ orders-2 │          │  │payments-2│                               │
│      │  └──────────┘          │  └──────────┘                               │
│      ▼                        ▼                                             │
│    ┌──────────┐             ┌──────────┐                                   │
│    │ C1       │             │ C1       │                                   │
│    │ orders-0 │             │payments-0│                                   │
│    └──────────┘             └──────────┘                                   │
│                                                                             │
│  Result: C1 gets 2 partitions, C2 gets 4 partitions (uneven!)              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Round-robin assignment

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ROUND-ROBIN ASSIGNMENT                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Topics: orders (3 partitions), payments (3 partitions)                     │
│  Consumers: C1, C2                                                          │
│                                                                             │
│  All partitions sorted: orders-0, orders-1, orders-2,                       │
│                         payments-0, payments-1, payments-2                  │
│                                                                             │
│  Round-robin assignment:                                                    │
│    orders-0   → C1                                                          │
│    orders-1   → C2                                                          │
│    orders-2   → C1                                                          │
│    payments-0 → C2                                                          │
│    payments-1 → C1                                                          │
│    payments-2 → C2                                                          │
│                                                                             │
│    ┌──────────────┐         ┌──────────────┐                               │
│    │ C1           │         │ C2           │                               │
│    │ orders-0     │         │ orders-1     │                               │
│    │ orders-2     │         │ payments-0   │                               │
│    │ payments-1   │         │ payments-2   │                               │
│    └──────────────┘         └──────────────┘                               │
│                                                                             │
│  Result: C1 gets 3 partitions, C2 gets 3 partitions (even!)                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Rebalancing

### What triggers a rebalance?

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         REBALANCE TRIGGERS                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. CONSUMER JOINS GROUP                                                    │
│     New consumer calls subscribe() → Rebalance                              │
│                                                                             │
│  2. CONSUMER LEAVES GROUP                                                   │
│     Consumer calls close() or unsubscribe() → Rebalance                     │
│                                                                             │
│  3. CONSUMER FAILS                                                          │
│     No heartbeat for session.timeout.ms → Rebalance                         │
│     No poll() for max.poll.interval.ms → Rebalance                          │
│                                                                             │
│  4. TOPIC CHANGES                                                           │
│     Partition added to subscribed topic → Rebalance                         │
│     Topic matching subscription pattern created → Rebalance                 │
│                                                                             │
│  5. GROUP COORDINATOR FAILOVER                                              │
│     Coordinator broker fails → New coordinator → Rebalance                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Eager vs cooperative rebalancing

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    EAGER vs COOPERATIVE REBALANCING                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  EAGER (Stop-the-World)                                                     │
│  ──────────────────────                                                     │
│                                                                             │
│  Time ─────────────────────────────────────────────────────────────►        │
│                                                                             │
│  C1: [Processing P0,P1] ─STOP─ [Waiting] ─RESUME─ [Processing P0]          │
│  C2: [Processing P2]    ─STOP─ [Waiting] ─RESUME─ [Processing P1,P2]       │
│                                  ▲                                          │
│                                  │                                          │
│                        ALL consumers stop                                   │
│                        (processing paused)                                  │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  COOPERATIVE (Incremental)                                                  │
│  ─────────────────────────                                                  │
│                                                                             │
│  Time ─────────────────────────────────────────────────────────────►        │
│                                                                             │
│  C1: [Processing P0,P1] ──────► [Revoke P1] ──────► [Processing P0]        │
│  C2: [Processing P2]    ──────► [Unchanged] ──────► [Assign P1,P2]         │
│                                      ▲                                      │
│                                      │                                      │
│                        Only affected partitions                             │
│                        (minimal disruption)                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Handling rebalances in code

```python
from confluent_kafka import Consumer, TopicPartition

class RebalanceHandler:
    def __init__(self, consumer):
        self.consumer = consumer

    def on_assign(self, consumer, partitions):
        """Called when partitions are assigned to this consumer."""
        print(f"Assigned partitions: {[f'{p.topic}-{p.partition}' for p in partitions]}")

        # Optionally seek to specific offsets
        for partition in partitions:
            # Example: seek to beginning
            # partition.offset = 0
            pass

    def on_revoke(self, consumer, partitions):
        """Called when partitions are revoked from this consumer."""
        print(f"Revoked partitions: {[f'{p.topic}-{p.partition}' for p in partitions]}")

        # Commit offsets for revoked partitions before they're taken away
        consumer.commit(asynchronous=False)

    def on_lost(self, consumer, partitions):
        """Called when partitions are lost (not cleanly revoked)."""
        print(f"Lost partitions: {[f'{p.topic}-{p.partition}' for p in partitions]}")
        # No need to commit - partitions were lost abnormally

# Usage
config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'rebalance-aware-group',
    'enable.auto.commit': False,
    'partition.assignment.strategy': 'cooperative-sticky'
}

consumer = Consumer(config)
handler = RebalanceHandler(consumer)

consumer.subscribe(
    ['orders'],
    on_assign=handler.on_assign,
    on_revoke=handler.on_revoke,
    on_lost=handler.on_lost
)

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            continue

        process_message(msg)
        consumer.commit(msg)
finally:
    consumer.close()
```

### Avoiding rebalance storms

```python
# Configuration to reduce rebalance frequency
config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'stable-group',

    # Session management
    'session.timeout.ms': 45000,       # 45 seconds (default)
    'heartbeat.interval.ms': 15000,    # 15 seconds

    # Poll interval (critical for slow processing)
    'max.poll.interval.ms': 300000,    # 5 minutes
    'max.poll.records': 500,           # Limit records per poll

    # Use cooperative rebalancing
    'partition.assignment.strategy': 'cooperative-sticky'
}
```

---

## Group coordinator

### How the coordinator works

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         GROUP COORDINATOR                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  The Group Coordinator is a broker responsible for managing consumer        │
│  group membership and partition assignment.                                 │
│                                                                             │
│    KAFKA CLUSTER                                                            │
│    ┌─────────────────────────────────────────────────────────────┐         │
│    │                                                              │         │
│    │  Broker 1           Broker 2              Broker 3          │         │
│    │  ┌──────────┐       ┌──────────┐          ┌──────────┐     │         │
│    │  │          │       │COORDINATOR│◄────────│          │     │         │
│    │  │          │       │for group-A│         │          │     │         │
│    │  └──────────┘       └────┬─────┘          └──────────┘     │         │
│    │                          │                                  │         │
│    └──────────────────────────┼──────────────────────────────────┘         │
│                               │                                             │
│              ┌────────────────┼────────────────┐                           │
│              │                │                │                            │
│              ▼                ▼                ▼                            │
│         ┌─────────┐      ┌─────────┐      ┌─────────┐                      │
│         │Consumer1│      │Consumer2│      │Consumer3│                      │
│         │ ♥ ♥ ♥   │      │ ♥ ♥ ♥   │      │ ♥ ♥ ♥   │                      │
│         └─────────┘      └─────────┘      └─────────┘                      │
│                                                                             │
│    COORDINATOR RESPONSIBILITIES:                                            │
│    • Receive heartbeats from consumers                                      │
│    • Detect failed consumers (no heartbeat)                                 │
│    • Trigger rebalances when membership changes                             │
│    • Receive partition assignment from group leader                         │
│    • Store committed offsets in __consumer_offsets topic                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Finding the coordinator

```bash
# Find the coordinator for a consumer group
docker exec -it kafka kafka-consumer-groups \
    --bootstrap-server localhost:9092 \
    --describe --group my-consumer-group
```

---

## Static membership

### What is static membership?

Static membership allows consumers to rejoin the group without triggering a rebalance by using a persistent `group.instance.id`.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STATIC vs DYNAMIC MEMBERSHIP                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  DYNAMIC MEMBERSHIP (Default)                                               │
│  ────────────────────────────                                               │
│                                                                             │
│  Consumer restarts → Gets new member ID → Rebalance triggered              │
│                                                                             │
│  Time: [C1 running] ─RESTART─ [C1 rejoins as new member] → REBALANCE       │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  STATIC MEMBERSHIP (group.instance.id set)                                  │
│  ─────────────────────────────────────────                                  │
│                                                                             │
│  Consumer restarts → Same instance ID → No rebalance (within timeout)       │
│                                                                             │
│  Time: [C1 running] ─RESTART─ [C1 rejoins with same ID] → NO REBALANCE     │
│                       │                                                     │
│                       ├── Must rejoin within session.timeout.ms            │
│                       └── Retains same partitions                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Configuring static membership

```python
import socket

config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'static-group',

    # Static membership configuration
    'group.instance.id': f'consumer-{socket.gethostname()}',  # Unique per instance
    'session.timeout.ms': 300000,  # 5 minutes - longer for restarts

    # Use cooperative rebalancing with static membership
    'partition.assignment.strategy': 'cooperative-sticky'
}
```

### When to use static membership

| Use Case | Recommendation |
|----------|----------------|
| Kubernetes deployments | Yes - pods restart frequently |
| Rolling deployments | Yes - avoid cascading rebalances |
| Spot/preemptible instances | Yes - instances come and go |
| Stateful consumers | Yes - maintain partition affinity |
| Development/testing | No - dynamic is simpler |

---

## Multi-topic consumption

### Subscribing to multiple topics

```python
from confluent_kafka import Consumer

config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'multi-topic-group',
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(config)

# Subscribe to specific topics
consumer.subscribe(['orders', 'payments', 'shipments'])

# Or use pattern matching
consumer.subscribe(['^order-.*'])  # All topics starting with 'order-'

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            continue

        # Handle different topics
        if msg.topic() == 'orders':
            process_order(msg.value())
        elif msg.topic() == 'payments':
            process_payment(msg.value())
        elif msg.topic() == 'shipments':
            process_shipment(msg.value())
        else:
            print(f"Unknown topic: {msg.topic()}")

finally:
    consumer.close()
```

### Topic-specific processing

```python
from confluent_kafka import Consumer
from typing import Callable, Dict

class MultiTopicConsumer:
    def __init__(self, config: dict, handlers: Dict[str, Callable]):
        self.consumer = Consumer(config)
        self.handlers = handlers
        self.consumer.subscribe(list(handlers.keys()))

    def run(self):
        try:
            while True:
                msg = self.consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    continue

                handler = self.handlers.get(msg.topic())
                if handler:
                    handler(msg)
                else:
                    print(f"No handler for topic: {msg.topic()}")

                self.consumer.commit(msg)
        finally:
            self.consumer.close()

# Usage
def handle_order(msg):
    print(f"Order: {msg.value()}")

def handle_payment(msg):
    print(f"Payment: {msg.value()}")

consumer = MultiTopicConsumer(
    config={'bootstrap.servers': 'localhost:9092', 'group.id': 'multi', 'enable.auto.commit': False},
    handlers={
        'orders': handle_order,
        'payments': handle_payment
    }
)
consumer.run()
```

---

## Monitoring consumer groups

### CLI commands

```bash
# List all consumer groups
docker exec -it kafka kafka-consumer-groups \
    --bootstrap-server localhost:9092 --list

# Describe a consumer group
docker exec -it kafka kafka-consumer-groups \
    --bootstrap-server localhost:9092 \
    --describe --group my-consumer-group

# Example output:
# GROUP           TOPIC     PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG    CONSUMER-ID
# my-group        orders    0          1000            1050            50     consumer-1-xxx
# my-group        orders    1          2000            2010            10     consumer-2-xxx
# my-group        orders    2          1500            1500            0      consumer-3-xxx

# Show group members
docker exec -it kafka kafka-consumer-groups \
    --bootstrap-server localhost:9092 \
    --describe --group my-consumer-group --members

# Show group state
docker exec -it kafka kafka-consumer-groups \
    --bootstrap-server localhost:9092 \
    --describe --group my-consumer-group --state
```

### Key metrics to monitor

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CONSUMER GROUP METRICS                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  METRIC                          DESCRIPTION                ALERT THRESHOLD │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  Consumer Lag                    Messages behind producer   > 10000         │
│  (LOG-END-OFFSET - CURRENT)                                                 │
│                                                                             │
│  Lag Trend                       Is lag growing or          Growing         │
│                                  shrinking?                                 │
│                                                                             │
│  Partition Assignment            Are partitions evenly      Uneven          │
│                                  distributed?                               │
│                                                                             │
│  Consumer Count                  Number of active           Changes         │
│                                  consumers                                  │
│                                                                             │
│  Rebalance Rate                  Rebalances per hour        > 5/hour        │
│                                                                             │
│  Commit Rate                     Commits per second         Unusual drop    │
│                                                                             │
│  Poll Latency                    Time between polls         Approaching     │
│                                                             max.poll.       │
│                                                             interval.ms     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Programmatic monitoring

```python
from confluent_kafka.admin import AdminClient, ConsumerGroupDescription
from confluent_kafka import TopicPartition

admin = AdminClient({'bootstrap.servers': 'localhost:9092'})

def get_consumer_group_lag(group_id: str, topics: list):
    """Calculate lag for all partitions in a consumer group."""

    # Get group description
    groups = admin.describe_consumer_groups([group_id])
    group_desc = groups[group_id].result()

    print(f"Group: {group_id}")
    print(f"State: {group_desc.state}")
    print(f"Members: {len(group_desc.members)}")

    # Get committed offsets
    offsets = admin.list_consumer_group_offsets([group_id])
    committed = offsets[group_id].result()

    total_lag = 0

    for tp, offset_meta in committed.items():
        if tp.topic in topics:
            # Get end offset
            consumer = Consumer({
                'bootstrap.servers': 'localhost:9092',
                'group.id': 'lag-checker'
            })
            low, high = consumer.get_watermark_offsets(tp)
            consumer.close()

            lag = high - offset_meta.offset if offset_meta.offset >= 0 else high
            total_lag += lag

            print(f"  {tp.topic}[{tp.partition}]: offset={offset_meta.offset}, end={high}, lag={lag}")

    print(f"Total lag: {total_lag}")
    return total_lag

# Usage
get_consumer_group_lag('my-consumer-group', ['orders'])
```

### Resetting offsets

```bash
# Reset to earliest (beginning)
docker exec -it kafka kafka-consumer-groups \
    --bootstrap-server localhost:9092 \
    --group my-consumer-group \
    --topic orders \
    --reset-offsets --to-earliest \
    --execute

# Reset to latest (end)
docker exec -it kafka kafka-consumer-groups \
    --bootstrap-server localhost:9092 \
    --group my-consumer-group \
    --topic orders \
    --reset-offsets --to-latest \
    --execute

# Reset to specific offset
docker exec -it kafka kafka-consumer-groups \
    --bootstrap-server localhost:9092 \
    --group my-consumer-group \
    --topic orders:0 \
    --reset-offsets --to-offset 1000 \
    --execute

# Reset to timestamp
docker exec -it kafka kafka-consumer-groups \
    --bootstrap-server localhost:9092 \
    --group my-consumer-group \
    --topic orders \
    --reset-offsets --to-datetime 2026-01-20T00:00:00.000 \
    --execute

# Shift by offset (relative)
docker exec -it kafka kafka-consumer-groups \
    --bootstrap-server localhost:9092 \
    --group my-consumer-group \
    --topic orders \
    --reset-offsets --shift-by -100 \
    --execute
```

---

## Hands-on exercises

### Exercise 1: Consumer group basics

Create a consumer group with multiple consumers and observe partition assignment.

```bash
# Terminal 1: Create topic with 4 partitions
docker exec -it kafka kafka-topics --create --topic group-exercise \
    --bootstrap-server localhost:9092 --partitions 4

# Produce some messages
docker exec -it kafka kafka-console-producer --topic group-exercise \
    --bootstrap-server localhost:9092
# Type messages: msg1, msg2, msg3, msg4 (one per line), then Ctrl+D
```

```python
# exercise_consumer_group.py - Run this in 2 terminals
from confluent_kafka import Consumer
import time
import socket

consumer_id = f"{socket.gethostname()}-{time.time()}"

config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'exercise-group',
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(config)
consumer.subscribe(['group-exercise'])

print(f"Consumer {consumer_id} started")

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            # Print assignment periodically
            assignment = consumer.assignment()
            partitions = [p.partition for p in assignment]
            print(f"Assigned partitions: {partitions}")
            continue
        if msg.error():
            continue

        print(f"[P{msg.partition()}] {msg.value().decode()}")
except KeyboardInterrupt:
    pass
finally:
    consumer.close()
```

### Exercise 2: Rebalance handling

Implement rebalance callbacks and observe behavior.

```python
# exercise_rebalance.py
from confluent_kafka import Consumer
import time

class RebalanceTracker:
    def __init__(self):
        self.rebalance_count = 0

    def on_assign(self, consumer, partitions):
        self.rebalance_count += 1
        partition_list = [f"{p.topic}-{p.partition}" for p in partitions]
        print(f"[ASSIGN #{self.rebalance_count}] Partitions: {partition_list}")

    def on_revoke(self, consumer, partitions):
        partition_list = [f"{p.topic}-{p.partition}" for p in partitions]
        print(f"[REVOKE] Partitions: {partition_list}")
        # Commit before losing partitions
        consumer.commit(asynchronous=False)

config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'rebalance-exercise',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False,
    'partition.assignment.strategy': 'cooperative-sticky'
}

consumer = Consumer(config)
tracker = RebalanceTracker()

consumer.subscribe(
    ['group-exercise'],
    on_assign=tracker.on_assign,
    on_revoke=tracker.on_revoke
)

try:
    print("Consumer started. Start/stop other consumers to trigger rebalances.")
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            continue

        print(f"Received: {msg.value().decode()}")
        consumer.commit(msg)
except KeyboardInterrupt:
    print(f"\nTotal rebalances: {tracker.rebalance_count}")
finally:
    consumer.close()
```

### Exercise 3: Monitor consumer lag

Build a simple lag monitor.

```python
# exercise_lag_monitor.py
from confluent_kafka import Consumer, TopicPartition
from confluent_kafka.admin import AdminClient
import time

def monitor_lag(group_id: str, topic: str, interval: int = 5):
    """Monitor consumer group lag continuously."""

    admin = AdminClient({'bootstrap.servers': 'localhost:9092'})

    print(f"Monitoring lag for group '{group_id}' on topic '{topic}'")
    print("-" * 60)

    while True:
        try:
            # Get committed offsets
            offsets_future = admin.list_consumer_group_offsets([group_id])
            committed = offsets_future[group_id].result()

            # Create a temporary consumer to get watermarks
            temp_consumer = Consumer({
                'bootstrap.servers': 'localhost:9092',
                'group.id': 'lag-monitor-temp'
            })

            total_lag = 0
            partition_lags = []

            for tp, offset_meta in committed.items():
                if tp.topic == topic:
                    low, high = temp_consumer.get_watermark_offsets(tp)
                    lag = high - offset_meta.offset if offset_meta.offset >= 0 else high
                    total_lag += lag
                    partition_lags.append((tp.partition, offset_meta.offset, high, lag))

            temp_consumer.close()

            # Print results
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] Total lag: {total_lag:,}")
            for partition, offset, end, lag in sorted(partition_lags):
                bar = "█" * min(lag // 100, 20)
                print(f"  P{partition}: {offset:>8} / {end:>8} (lag: {lag:>6}) {bar}")

            time.sleep(interval)

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(interval)

if __name__ == '__main__':
    monitor_lag('exercise-group', 'group-exercise')
```

---

## Key takeaways

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CONSUMER GROUP KEY TAKEAWAYS                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ✓ Consumer groups enable parallel processing of partitions                │
│                                                                             │
│  ✓ Each partition is consumed by exactly ONE consumer in the group         │
│                                                                             │
│  ✓ Consumers > Partitions = Idle consumers (plan partition count wisely)   │
│                                                                             │
│  ✓ Use cooperative-sticky assignment to minimize rebalance disruption      │
│                                                                             │
│  ✓ Implement rebalance callbacks to handle partition changes gracefully    │
│                                                                             │
│  ✓ Use static membership for Kubernetes/container deployments              │
│                                                                             │
│  ✓ Monitor consumer lag - it's the key health metric for consumers         │
│                                                                             │
│  ✓ Set max.poll.interval.ms based on your longest processing time          │
│                                                                             │
│  ✓ Different groups can independently consume the same topic (fan-out)     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

**[← Back to Consumers](./07_consumers.md)** | **[Next: Module 3 - Kafka Connect →](../module_3_intermediate/09_kafka_connect.md)**

[↑ Back to Top](#lesson-08-consumer-groups)
