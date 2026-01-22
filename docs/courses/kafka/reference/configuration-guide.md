# Kafka Configuration Decision Guide

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Configuration-blue)

## Overview

This guide helps you make configuration decisions based on your use case. Use these tables to choose appropriate settings for your Kafka deployment.

---

## Table of contents

- [Use case profiles](#use-case-profiles)
- [Producer configurations](#producer-configurations)
- [Consumer configurations](#consumer-configurations)
- [Topic configurations](#topic-configurations)
- [Broker configurations](#broker-configurations)
- [Common mistakes](#common-mistakes)

---

## Use case profiles

### Choose your profile

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    WHICH PROFILE FITS YOUR USE CASE?                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  HIGH THROUGHPUT                   LOW LATENCY                              │
│  ─────────────────                 ───────────                              │
│  • Log aggregation                 • Real-time fraud detection              │
│  • Metrics collection              • Live dashboards                        │
│  • Click stream                    • Gaming events                          │
│  • IoT sensor data                 • Trading systems                        │
│                                                                             │
│  Priority: Volume over speed       Priority: Speed over volume              │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  HIGH DURABILITY                   BALANCED                                 │
│  ────────────────                  ────────                                 │
│  • Financial transactions          • E-commerce orders                      │
│  • Audit logs                      • User events                            │
│  • Order processing                • Notifications                          │
│  • Payment events                  • General messaging                      │
│                                                                             │
│  Priority: Never lose data         Priority: Good balance of all factors    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Producer configurations

### Configuration by use case

| Setting | High Throughput | Low Latency | High Durability | Balanced |
|---------|-----------------|-------------|-----------------|----------|
| `acks` | 1 | 1 | all | all |
| `enable.idempotence` | false | true | true | true |
| `batch.size` | 65536 (64KB) | 16384 (16KB) | 16384 (16KB) | 32768 (32KB) |
| `linger.ms` | 50-100 | 0 | 5 | 10-20 |
| `compression.type` | lz4 or zstd | none | lz4 | lz4 |
| `buffer.memory` | 67108864 (64MB) | 33554432 (32MB) | 33554432 (32MB) | 33554432 (32MB) |
| `retries` | 3 | 3 | 2147483647 | 2147483647 |
| `delivery.timeout.ms` | 30000 | 10000 | 120000 | 120000 |

### Producer configuration templates

**High Throughput (Metrics, Logs):**
```python
config = {
    'bootstrap.servers': 'localhost:9092',
    'acks': '1',
    'enable.idempotence': False,
    'batch.size': 65536,
    'linger.ms': 50,
    'compression.type': 'lz4',
    'buffer.memory': 67108864
}
```

**Low Latency (Real-time):**
```python
config = {
    'bootstrap.servers': 'localhost:9092',
    'acks': '1',
    'enable.idempotence': True,
    'batch.size': 16384,
    'linger.ms': 0,
    'compression.type': 'none'
}
```

**High Durability (Financial):**
```python
config = {
    'bootstrap.servers': 'localhost:9092',
    'acks': 'all',
    'enable.idempotence': True,
    'retries': 2147483647,
    'max.in.flight.requests.per.connection': 5,
    'delivery.timeout.ms': 120000
}
```

---

## Consumer configurations

### Configuration by use case

| Setting | High Throughput | Low Latency | Exactly-Once | Balanced |
|---------|-----------------|-------------|--------------|----------|
| `fetch.min.bytes` | 1048576 (1MB) | 1 | 1 | 1024 |
| `fetch.max.wait.ms` | 500 | 100 | 500 | 500 |
| `max.poll.records` | 1000 | 100 | 500 | 500 |
| `enable.auto.commit` | true | true | false | false |
| `auto.commit.interval.ms` | 5000 | 1000 | N/A | N/A |
| `auto.offset.reset` | latest | latest | earliest | earliest |
| `max.poll.interval.ms` | 300000 | 30000 | 300000 | 300000 |
| `session.timeout.ms` | 45000 | 10000 | 45000 | 45000 |

### Consumer configuration templates

**High Throughput:**
```python
config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'high-throughput-group',
    'fetch.min.bytes': 1048576,
    'fetch.max.wait.ms': 500,
    'max.poll.records': 1000,
    'enable.auto.commit': True,
    'auto.commit.interval.ms': 5000
}
```

**Low Latency:**
```python
config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'low-latency-group',
    'fetch.min.bytes': 1,
    'fetch.max.wait.ms': 100,
    'max.poll.records': 100,
    'enable.auto.commit': True,
    'auto.commit.interval.ms': 1000
}
```

**Exactly-Once Processing:**
```python
config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'exactly-once-group',
    'enable.auto.commit': False,  # Manual commits
    'isolation.level': 'read_committed',  # Only read committed transactions
    'auto.offset.reset': 'earliest'
}
```

---

## Topic configurations

### Partition count guidelines

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PARTITION COUNT DECISION                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  THROUGHPUT FORMULA                                                         │
│  ──────────────────                                                         │
│  partitions >= max(target_throughput / per_partition_throughput,            │
│                    desired_consumer_parallelism)                            │
│                                                                             │
│  Per partition: ~10 MB/s write, ~30 MB/s read (typical)                     │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  QUICK REFERENCE                                                            │
│  ───────────────                                                            │
│                                                                             │
│  Throughput          Partitions    Notes                                    │
│  ─────────────────────────────────────────────────────────────────────      │
│  < 10 MB/s           3-6           Room to grow                             │
│  10-50 MB/s          6-12          Standard production                      │
│  50-100 MB/s         12-24         High volume                              │
│  100-500 MB/s        24-60         Very high volume                         │
│  > 500 MB/s          60-100+       Enterprise scale                         │
│                                                                             │
│  CONSUMER PARALLELISM                                                       │
│  ────────────────────                                                       │
│  If you need N consumers processing in parallel, you need >= N partitions   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Replication and durability

| Environment | replication.factor | min.insync.replicas | acks | Fault Tolerance |
|-------------|-------------------|---------------------|------|-----------------|
| Development | 1 | 1 | 1 | None |
| Staging | 2 | 1 | 1 | 1 broker |
| Production | 3 | 2 | all | 1 broker |
| Critical | 3 | 2 | all | 1 broker |

### Retention configurations

| Use Case | retention.ms | retention.bytes | cleanup.policy |
|----------|--------------|-----------------|----------------|
| Real-time only | 3600000 (1h) | -1 | delete |
| Short-term | 86400000 (1d) | -1 | delete |
| Standard | 604800000 (7d) | -1 | delete |
| Long-term | 2592000000 (30d) | -1 | delete |
| Audit/Compliance | 31536000000 (1y) | -1 | delete |
| State/Changelog | -1 (forever) | -1 | compact |
| Session state | 86400000 (1d) | -1 | compact,delete |

### Topic configuration templates

**Event Stream (Standard):**
```bash
kafka-topics --create --topic events \
  --partitions 12 \
  --replication-factor 3 \
  --config retention.ms=604800000 \
  --config min.insync.replicas=2
```

**Compacted State:**
```bash
kafka-topics --create --topic user-profiles \
  --partitions 6 \
  --replication-factor 3 \
  --config cleanup.policy=compact \
  --config min.insync.replicas=2 \
  --config delete.retention.ms=86400000
```

**High-Throughput Logs:**
```bash
kafka-topics --create --topic application-logs \
  --partitions 24 \
  --replication-factor 2 \
  --config retention.ms=86400000 \
  --config compression.type=lz4
```

---

## Broker configurations

### Hardware recommendations

| Component | Development | Production (Small) | Production (Large) |
|-----------|-------------|-------------------|-------------------|
| **CPU** | 2 cores | 8 cores | 16+ cores |
| **RAM** | 4 GB | 32 GB | 64 GB |
| **Disk** | 50 GB HDD | 1 TB SSD | 4+ TB NVMe |
| **Network** | 1 Gbps | 10 Gbps | 25+ Gbps |
| **JVM Heap** | 1 GB | 6 GB | 8 GB (max) |

### Key broker settings

| Setting | Development | Production | Notes |
|---------|-------------|------------|-------|
| `num.network.threads` | 3 | 8 | Network I/O threads |
| `num.io.threads` | 8 | 16 | Disk I/O threads |
| `socket.send.buffer.bytes` | 102400 | 1048576 | Socket send buffer |
| `socket.receive.buffer.bytes` | 102400 | 1048576 | Socket receive buffer |
| `socket.request.max.bytes` | 104857600 | 104857600 | Max request size (100MB) |
| `log.retention.hours` | 168 | 168 | Default retention (7d) |
| `log.segment.bytes` | 1073741824 | 1073741824 | Segment size (1GB) |
| `num.partitions` | 1 | 3 | Default partition count |
| `default.replication.factor` | 1 | 3 | Default replication |
| `min.insync.replicas` | 1 | 2 | Minimum ISR |
| `unclean.leader.election.enable` | false | false | Prevent data loss |

---

## Common mistakes

### Producer mistakes

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PRODUCER ANTI-PATTERNS                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ✗ MISTAKE: Using acks=0 for important data                                 │
│  ✓ FIX: Use acks=all with enable.idempotence=true                           │
│                                                                             │
│  ✗ MISTAKE: Not handling delivery failures                                  │
│  ✓ FIX: Always implement delivery callbacks                                 │
│                                                                             │
│  ✗ MISTAKE: Not calling flush() before shutdown                             │
│  ✓ FIX: Always flush() to ensure all messages are sent                      │
│                                                                             │
│  ✗ MISTAKE: Using synchronous sends for high throughput                     │
│  ✓ FIX: Use async sends with batching                                       │
│                                                                             │
│  ✗ MISTAKE: Ignoring retries configuration                                  │
│  ✓ FIX: Set retries high (or MAX_INT) with delivery.timeout.ms             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Consumer mistakes

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CONSUMER ANTI-PATTERNS                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ✗ MISTAKE: Processing takes longer than max.poll.interval.ms               │
│  ✓ FIX: Increase max.poll.interval.ms or reduce max.poll.records            │
│                                                                             │
│  ✗ MISTAKE: Auto-commit with at-least-once requirements                     │
│  ✓ FIX: Use manual commits after successful processing                      │
│                                                                             │
│  ✗ MISTAKE: More consumers than partitions                                  │
│  ✓ FIX: Consumers <= partitions (extras will be idle)                       │
│                                                                             │
│  ✗ MISTAKE: Not handling rebalancing                                        │
│  ✓ FIX: Implement ConsumerRebalanceListener                                 │
│                                                                             │
│  ✗ MISTAKE: Ignoring consumer lag                                           │
│  ✓ FIX: Monitor lag and alert when it grows                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Topic mistakes

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TOPIC ANTI-PATTERNS                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ✗ MISTAKE: Single partition for ordered data                               │
│  ✓ FIX: Use keys for ordering - same key = same partition                   │
│                                                                             │
│  ✗ MISTAKE: Too few partitions for throughput                               │
│  ✓ FIX: Plan partitions based on throughput AND consumer parallelism        │
│                                                                             │
│  ✗ MISTAKE: Replication factor = 1 in production                            │
│  ✓ FIX: Always use replication factor >= 3 in production                    │
│                                                                             │
│  ✗ MISTAKE: Not setting min.insync.replicas                                 │
│  ✓ FIX: Set min.insync.replicas = replication.factor - 1                    │
│                                                                             │
│  ✗ MISTAKE: Retention too short, losing ability to replay                   │
│  ✓ FIX: Set retention based on replay requirements, not just storage        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Quick reference cheat sheet

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CONFIGURATION CHEAT SHEET                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PRODUCER: "I need durability"                                              │
│  → acks=all, enable.idempotence=true, retries=MAX                           │
│                                                                             │
│  PRODUCER: "I need throughput"                                              │
│  → acks=1, linger.ms=50, batch.size=64KB, compression=lz4                   │
│                                                                             │
│  PRODUCER: "I need low latency"                                             │
│  → acks=1, linger.ms=0, compression=none                                    │
│                                                                             │
│  CONSUMER: "I need exactly-once"                                            │
│  → enable.auto.commit=false, isolation.level=read_committed                 │
│                                                                             │
│  CONSUMER: "I need throughput"                                              │
│  → fetch.min.bytes=1MB, max.poll.records=1000                               │
│                                                                             │
│  CONSUMER: "I need low latency"                                             │
│  → fetch.min.bytes=1, fetch.max.wait.ms=100                                 │
│                                                                             │
│  TOPIC: "I need durability"                                                 │
│  → replication.factor=3, min.insync.replicas=2                              │
│                                                                             │
│  TOPIC: "I need state/changelog"                                            │
│  → cleanup.policy=compact                                                   │
│                                                                             │
│  TOPIC: "I need high throughput"                                            │
│  → More partitions (12-24+), compression=lz4                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

[↑ Back to Top](#kafka-configuration-decision-guide)
