# Topics and Partitions Deep Dive

**[← Back to Module 2](./README.md)** | **[Next: Producers →](./06_producers.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Module](https://img.shields.io/badge/Module-2_Core_Concepts-blue)

## Table of contents

- [Learning objectives](#learning-objectives)
- [Topic design principles](#topic-design-principles)
- [Partition strategies](#partition-strategies)
- [Retention policies](#retention-policies)
- [Log compaction](#log-compaction)
- [Topic configuration](#topic-configuration)
- [Best practices](#best-practices)
- [Key takeaways](#key-takeaways)

---

## Learning objectives

By the end of this lesson, you will be able to:

1. Design topic schemas based on use case requirements
2. Choose appropriate partition counts and strategies
3. Configure retention policies for different scenarios
4. Understand and implement log compaction
5. Apply topic configuration best practices

---

## Topic design principles

### What belongs in a topic?

A topic should contain **related events of the same type**. Think of a topic as a category or channel.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TOPIC DESIGN PATTERNS                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  GOOD: One topic per event type                                             │
│  ─────────────────────────────────                                          │
│  • orders.created         - New order events                                │
│  • orders.shipped         - Shipping events                                 │
│  • payments.processed     - Payment completions                             │
│  • users.registered       - New user sign-ups                               │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  BAD: Mixed event types in one topic                                        │
│  ─────────────────────────────────────                                      │
│  • all-events             - Everything mixed together                       │
│  • user-stuff             - Registrations, logins, updates mixed            │
│                                                                             │
│  WHY?                                                                       │
│  • Different consumers need different events                                │
│  • Schema evolution is harder with mixed types                              │
│  • Harder to reason about message ordering                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Topic naming conventions

Establish a consistent naming convention:

```
Pattern: <domain>.<entity>.<event>

Examples:
• ecommerce.orders.created
• ecommerce.orders.updated
• ecommerce.orders.cancelled
• logistics.shipments.dispatched
• logistics.shipments.delivered
• analytics.pageviews.raw
• analytics.pageviews.enriched
```

| Convention | Example | Use Case |
|------------|---------|----------|
| Domain-first | `payments.transactions` | Large organizations |
| Service-first | `order-service.events` | Microservices |
| Event-first | `user-registered` | Simple applications |

[↑ Back to Table of Contents](#table-of-contents)

---

## Partition strategies

### How many partitions?

Partitions determine parallelism. Consider:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PARTITION COUNT FACTORS                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. THROUGHPUT REQUIREMENTS                                                 │
│     ────────────────────────                                                │
│     • Single partition: ~10 MB/s writes                                     │
│     • Need 100 MB/s? → Minimum 10 partitions                                │
│     • Formula: partitions ≥ target_throughput / partition_throughput        │
│                                                                             │
│  2. CONSUMER PARALLELISM                                                    │
│     ─────────────────────                                                   │
│     • Max active consumers = partition count                                │
│     • 6 partitions = max 6 parallel consumers                               │
│     • Plan for future scaling                                               │
│                                                                             │
│  3. ORDERING REQUIREMENTS                                                   │
│     ────────────────────                                                    │
│     • Total order needed? → 1 partition (limits throughput)                 │
│     • Order per entity? → Use keys (many partitions OK)                     │
│                                                                             │
│  4. BROKER CAPACITY                                                         │
│     ───────────────────                                                     │
│     • Each partition = files, memory, connections                           │
│     • Recommended: <4000 partitions per broker                              │
│     • Recommended: <200,000 partitions per cluster                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Partition count guidelines

| Use Case | Suggested Partitions | Reasoning |
|----------|---------------------|-----------|
| Development/Testing | 1-3 | Simplicity |
| Low volume (<1K/sec) | 3-6 | Room to grow |
| Medium volume | 6-12 | Good parallelism |
| High volume | 12-30 | More consumers |
| Very high volume | 30-100+ | Maximum throughput |

> [!WARNING]
> You can only increase partitions, never decrease. Start conservative, scale up when needed.

### Partitioning strategies

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PARTITIONING STRATEGIES                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. KEY-BASED (Default with key)                                            │
│     ─────────────────────────────                                           │
│     partition = hash(key) % num_partitions                                  │
│                                                                             │
│     Pros: Related messages stay together, ordering preserved                │
│     Cons: Potential hot spots if keys uneven                                │
│                                                                             │
│     Example: key=user_id → all events for user in same partition            │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  2. ROUND-ROBIN (No key)                                                    │
│     ─────────────────────                                                   │
│     Messages distributed evenly in rotation                                 │
│                                                                             │
│     Pros: Even distribution, maximum throughput                             │
│     Cons: No ordering guarantee for related messages                        │
│                                                                             │
│     Example: Independent log events                                         │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  3. CUSTOM PARTITIONER                                                      │
│     ─────────────────────                                                   │
│     Implement your own logic                                                │
│                                                                             │
│     Example: Route to partition based on geography                          │
│              US orders → P0-P2, EU orders → P3-P5                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Hot partition problem

When one key has much more traffic than others:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    HOT PARTITION PROBLEM                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Topic: user-events (4 partitions)                                          │
│  Key: user_id                                                               │
│                                                                             │
│  Problem: Celebrity user has 1M followers, normal users have 100            │
│                                                                             │
│  P0: ████████████████████████████████████ 10,000,000 events (celebrity)     │
│  P1: ██ 200 events                                                          │
│  P2: ███ 300 events                                                         │
│  P3: ██ 250 events                                                          │
│                                                                             │
│  Result: P0's consumer is overwhelmed, others idle                          │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  SOLUTIONS:                                                                 │
│  ───────────                                                                │
│  1. Composite key: "user_id:event_type" spreads load                        │
│  2. Random suffix: "user_id:random(10)" distributes to 10 partitions        │
│  3. Separate topic: Route high-volume users to dedicated topic              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Retention policies

### Time-based retention

```bash
# Keep messages for 7 days (default)
kafka-topics --bootstrap-server localhost:9092 \
  --create --topic events \
  --config retention.ms=604800000

# Keep messages for 30 days
kafka-topics --bootstrap-server localhost:9092 \
  --create --topic audit-logs \
  --config retention.ms=2592000000

# Keep messages for 1 hour (short-lived)
kafka-topics --bootstrap-server localhost:9092 \
  --create --topic temp-events \
  --config retention.ms=3600000
```

### Size-based retention

```bash
# Keep up to 1GB per partition
kafka-topics --bootstrap-server localhost:9092 \
  --create --topic large-events \
  --config retention.bytes=1073741824

# Combine time and size (whichever triggers first)
kafka-topics --bootstrap-server localhost:9092 \
  --create --topic mixed-retention \
  --config retention.ms=604800000 \
  --config retention.bytes=10737418240
```

### Retention strategy by use case

| Use Case | Time | Size | Notes |
|----------|------|------|-------|
| Real-time streams | 1-24 hours | Small | Fast processing, no replay |
| Event sourcing | Forever | Unlimited | Complete history needed |
| Audit logs | 7+ years | Unlimited | Compliance requirements |
| Analytics | 30-90 days | Medium | Balance storage vs replay |
| Temp/Debug | 1 hour | Small | Cleanup quickly |

[↑ Back to Table of Contents](#table-of-contents)

---

## Log compaction

Log compaction retains only the **latest value for each key**, perfect for changelogs and state snapshots.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LOG COMPACTION                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  BEFORE COMPACTION                                                          │
│  ────────────────────                                                       │
│  [K1:A] [K2:B] [K1:C] [K3:D] [K2:E] [K1:F] [K3:G]                           │
│     │      │      │      │      │      │      │                             │
│   user1  user2  user1  user3  user2  user1  user3                           │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  AFTER COMPACTION                                                           │
│  ────────────────────                                                       │
│  [K1:F] [K2:E] [K3:G]                                                       │
│     │      │      │                                                         │
│   user1  user2  user3                                                       │
│   (latest)(latest)(latest)                                                  │
│                                                                             │
│  Compaction keeps only the LATEST value for each key.                       │
│  Earlier versions are removed during cleanup.                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Enable log compaction

```bash
# Create compacted topic
kafka-topics --bootstrap-server localhost:9092 \
  --create --topic user-profiles \
  --config cleanup.policy=compact

# Combine deletion and compaction
kafka-topics --bootstrap-server localhost:9092 \
  --create --topic user-sessions \
  --config cleanup.policy=compact,delete \
  --config retention.ms=86400000
```

### Tombstones (deleting keys)

To delete a key from a compacted topic, produce a message with `null` value:

```python
# Python example - sending a tombstone
producer.produce(
    topic='user-profiles',
    key='user-123',
    value=None  # Tombstone - marks key for deletion
)
```

### Compaction use cases

| Use Case | cleanup.policy | Description |
|----------|----------------|-------------|
| User profiles | compact | Latest state per user |
| Configuration | compact | Current config values |
| Session state | compact,delete | State with TTL |
| Event logs | delete | Time-based retention |
| Audit trails | delete | Long-term storage |

[↑ Back to Table of Contents](#table-of-contents)

---

## Topic configuration

### Common configurations

```bash
# View all topic configurations
kafka-configs --bootstrap-server localhost:9092 \
  --entity-type topics \
  --entity-name my-topic \
  --describe --all
```

| Configuration | Default | Description |
|---------------|---------|-------------|
| `retention.ms` | 604800000 (7d) | Time to keep messages |
| `retention.bytes` | -1 (unlimited) | Max size per partition |
| `cleanup.policy` | delete | delete, compact, or both |
| `max.message.bytes` | 1048576 (1MB) | Max message size |
| `min.insync.replicas` | 1 | Min replicas for acks=all |
| `segment.bytes` | 1073741824 (1GB) | Log segment size |
| `compression.type` | producer | producer, gzip, snappy, lz4, zstd |

### Modify topic configuration

```bash
# Set configuration
kafka-configs --bootstrap-server localhost:9092 \
  --entity-type topics \
  --entity-name my-topic \
  --alter \
  --add-config retention.ms=86400000,max.message.bytes=2097152

# Remove configuration (revert to default)
kafka-configs --bootstrap-server localhost:9092 \
  --entity-type topics \
  --entity-name my-topic \
  --alter \
  --delete-config retention.ms
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Best practices

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TOPIC BEST PRACTICES                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. NAMING                                                                  │
│     • Use consistent naming convention                                      │
│     • Include domain/service prefix                                         │
│     • Avoid special characters (stick to a-z, 0-9, -, .)                    │
│                                                                             │
│  2. PARTITIONS                                                              │
│     • Start with 3-6 for new topics                                         │
│     • Plan for 2-3x expected consumer count                                 │
│     • Use keys when ordering matters                                        │
│     • Monitor for hot partitions                                            │
│                                                                             │
│  3. REPLICATION                                                             │
│     • Production: replication.factor=3                                      │
│     • Set min.insync.replicas=2 for durability                              │
│     • Match replication to broker count (max = broker count)                │
│                                                                             │
│  4. RETENTION                                                               │
│     • Define based on replay requirements                                   │
│     • Consider compliance/audit needs                                       │
│     • Monitor disk usage                                                    │
│                                                                             │
│  5. GOVERNANCE                                                              │
│     • Document topic ownership                                              │
│     • Use Schema Registry for data contracts                                │
│     • Implement topic lifecycle management                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Key takeaways

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        KEY TAKEAWAYS                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. One topic = one event type for clean architecture                       │
│                                                                             │
│  2. Partition count determines max parallelism - plan ahead                 │
│                                                                             │
│  3. Use keys when message ordering matters for related data                 │
│                                                                             │
│  4. Retention policies balance storage cost vs replay capability            │
│                                                                             │
│  5. Log compaction keeps only latest values - ideal for state               │
│                                                                             │
│  6. min.insync.replicas + acks=all = strong durability                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

**Next:** [Producers →](./06_producers.md)
