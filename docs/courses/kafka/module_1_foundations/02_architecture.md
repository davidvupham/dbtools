# Kafka Architecture Deep Dive

**[← Back to Introduction](./01_introduction.md)** | **[Next: Environment Setup →](./03_setup_environment.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Module](https://img.shields.io/badge/Module-1_Foundations-blue)

## Table of contents

- [Learning objectives](#learning-objectives)
- [High-level architecture](#high-level-architecture)
- [Topics and partitions](#topics-and-partitions)
- [Brokers and clusters](#brokers-and-clusters)
- [Replication](#replication)
- [Producers and consumers](#producers-and-consumers)
- [ZooKeeper vs KRaft](#zookeeper-vs-kraft)
- [Data flow walkthrough](#data-flow-walkthrough)
- [Key takeaways](#key-takeaways)
- [Knowledge check](#knowledge-check)

---

## Learning objectives

By the end of this lesson, you will be able to:

1. Describe the core components of Kafka architecture
2. Explain how topics and partitions enable scalability
3. Understand leader/follower replication for fault tolerance
4. Differentiate between ZooKeeper and KRaft modes
5. Trace the flow of a message through Kafka

---

## High-level architecture

Kafka's architecture is designed for distributed, fault-tolerant operation at massive scale. Here's the big picture:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      KAFKA ARCHITECTURE OVERVIEW                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PRODUCERS                   KAFKA CLUSTER                    CONSUMERS     │
│  ─────────                   ─────────────                    ─────────     │
│                                                                             │
│  ┌─────────┐            ┌───────────────────────┐          ┌─────────┐     │
│  │Producer │            │      Broker 1         │          │Consumer │     │
│  │   App   │──────┐     │  ┌────────────────┐   │    ┌────►│  App A  │     │
│  └─────────┘      │     │  │  Topic: orders │   │    │     └─────────┘     │
│                   │     │  │  Partition 0 ▲ │   │    │                     │
│  ┌─────────┐      │     │  │  [0][1][2][3] │   │    │     ┌─────────┐     │
│  │Producer │──────┼────►│  └────────────────┘   │────┼────►│Consumer │     │
│  │   App   │      │     └───────────────────────┘    │     │  App B  │     │
│  └─────────┘      │                                  │     └─────────┘     │
│                   │     ┌───────────────────────┐    │                     │
│  ┌─────────┐      │     │      Broker 2         │    │     ┌─────────┐     │
│  │Producer │──────┘     │  ┌────────────────┐   │    │     │Consumer │     │
│  │   App   │            │  │  Topic: orders │   │    └────►│  App C  │     │
│  └─────────┘            │  │  Partition 1 ▲ │   │          └─────────┘     │
│                         │  │  [0][1][2]     │   │                          │
│                         │  └────────────────┘   │                          │
│                         └───────────────────────┘                          │
│                                                                             │
│                         ┌───────────────────────┐                          │
│                         │      Broker 3         │                          │
│                         │  ┌────────────────┐   │                          │
│                         │  │  Topic: orders │   │                          │
│                         │  │  Partition 2 ▲ │   │                          │
│                         │  │  [0][1]        │   │                          │
│                         │  └────────────────┘   │                          │
│                         └───────────────────────┘                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Core components

| Component | Description |
|-----------|-------------|
| **Producer** | Client that publishes messages to topics |
| **Consumer** | Client that reads messages from topics |
| **Broker** | Server that stores messages and serves requests |
| **Topic** | Category/feed name for messages |
| **Partition** | Subset of topic for parallelism |
| **Cluster** | Group of brokers working together |

[↑ Back to Table of Contents](#table-of-contents)

---

## Topics and partitions

### Topics: The logical grouping

A **topic** is a named channel where messages are published. Think of it as a category or feed name:

```
Examples of Topics:
─────────────────────
• orders           - All order events
• user-signups     - New user registrations
• page-views       - Website analytics
• inventory-updates - Stock level changes
• payments         - Payment transactions
```

Topics are:
- **Append-only**: New messages are added to the end
- **Immutable**: Messages cannot be modified after writing
- **Identified by name**: Must be unique within a cluster

### Partitions: The unit of parallelism

Each topic is divided into **partitions**. Partitions are the key to Kafka's scalability:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        TOPIC: orders (3 partitions)                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Partition 0:  [0] [1] [2] [3] [4] [5] [6] [7] ──────►                      │
│                 │   │   │   │   │   │   │   │                               │
│               msg msg msg msg msg msg msg msg                               │
│                                                                             │
│  Partition 1:  [0] [1] [2] [3] [4] [5] ──────►                              │
│                                                                             │
│  Partition 2:  [0] [1] [2] [3] [4] [5] [6] [7] [8] [9] ──────►              │
│                                                                             │
│  Each partition is an ordered, immutable sequence of records.               │
│  Numbers in brackets [n] are OFFSETS - unique IDs within the partition.     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Partitions enable parallelism

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PARALLEL CONSUMPTION                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Topic: orders (3 partitions)                                               │
│                                                                             │
│  Partition 0 ───────────────────────► Consumer 1                            │
│                                                                             │
│  Partition 1 ───────────────────────► Consumer 2                            │
│                                                                             │
│  Partition 2 ───────────────────────► Consumer 3                            │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  3x throughput compared to single partition!                                │
│  Each consumer processes independently in parallel.                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### How messages are assigned to partitions

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PARTITION ASSIGNMENT                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Method 1: Key-based (Recommended for related messages)                     │
│  ─────────────────────────────────────────────────────                      │
│  partition = hash(key) % num_partitions                                     │
│                                                                             │
│  Key: "user-123" ──► hash ──► Partition 1                                   │
│  Key: "user-456" ──► hash ──► Partition 2                                   │
│  Key: "user-123" ──► hash ──► Partition 1  (same user, same partition)      │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  Method 2: Round-robin (No key provided)                                    │
│  ────────────────────────────────────────                                   │
│  Messages distributed evenly across partitions                              │
│                                                                             │
│  Message 1 ──► Partition 0                                                  │
│  Message 2 ──► Partition 1                                                  │
│  Message 3 ──► Partition 2                                                  │
│  Message 4 ──► Partition 0                                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

> [!IMPORTANT]
> **Ordering guarantee**: Messages are ordered within a partition, not across partitions. If order matters for related messages, use the same key to ensure they go to the same partition.

### Offsets: Message addresses

Each message within a partition has a unique **offset** - a sequential ID that acts as an address:

```
Partition 0:
┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐
│  0  │  1  │  2  │  3  │  4  │  5  │  6  │  7  │ ──► (new messages appended)
└─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘
  ▲                       ▲                   ▲
  │                       │                   │
  First                Consumer            Latest
  Offset               Position            Offset
```

Offsets are:
- **Immutable**: Once assigned, never changes
- **Monotonically increasing**: Always goes up
- **Per-partition**: Each partition has its own offset sequence

[↑ Back to Table of Contents](#table-of-contents)

---

## Brokers and clusters

### What is a broker?

A **broker** is a Kafka server. It:
- Receives messages from producers
- Stores messages on disk
- Serves messages to consumers
- Handles replication

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BROKER INTERNALS                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        BROKER (Server)                               │   │
│  │                                                                      │   │
│  │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │   │
│  │   │  Network     │  │  Request     │  │  Purgatory   │             │   │
│  │   │  Layer       │  │  Handler     │  │  (Waiting)   │             │   │
│  │   └──────────────┘  └──────────────┘  └──────────────┘             │   │
│  │           │                │                  │                     │   │
│  │           ▼                ▼                  ▼                     │   │
│  │   ┌────────────────────────────────────────────────────────────┐   │   │
│  │   │                    LOG MANAGER                              │   │   │
│  │   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │   │   │
│  │   │  │ Topic A     │  │ Topic B     │  │ Topic C     │        │   │   │
│  │   │  │ Partition 0 │  │ Partition 1 │  │ Partition 0 │        │   │   │
│  │   │  └─────────────┘  └─────────────┘  └─────────────┘        │   │   │
│  │   └────────────────────────────────────────────────────────────┘   │   │
│  │                                │                                    │   │
│  │                                ▼                                    │   │
│  │                         ┌─────────────┐                            │   │
│  │                         │    DISK     │                            │   │
│  │                         │  (Storage)  │                            │   │
│  │                         └─────────────┘                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Kafka cluster

A **cluster** is a group of brokers working together:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         KAFKA CLUSTER                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐                 │
│  │  Broker 0   │      │  Broker 1   │      │  Broker 2   │                 │
│  │  (ID: 0)    │◄────►│  (ID: 1)    │◄────►│  (ID: 2)    │                 │
│  │             │      │             │      │             │                 │
│  │ Partitions: │      │ Partitions: │      │ Partitions: │                 │
│  │ orders-0    │      │ orders-1    │      │ orders-2    │                 │
│  │ users-1     │      │ users-2     │      │ users-0     │                 │
│  │ events-2    │      │ events-0    │      │ events-1    │                 │
│  └─────────────┘      └─────────────┘      └─────────────┘                 │
│         │                    │                    │                         │
│         └────────────────────┴────────────────────┘                         │
│                              │                                              │
│                    ┌─────────────────┐                                      │
│                    │    Controller   │                                      │
│                    │  (Broker 1)     │                                      │
│                    │                 │                                      │
│                    │ • Manages       │                                      │
│                    │   partitions    │                                      │
│                    │ • Elects        │                                      │
│                    │   leaders       │                                      │
│                    └─────────────────┘                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Controller broker

One broker is elected as the **controller** and is responsible for:
- Assigning partitions to brokers
- Monitoring broker health
- Electing new partition leaders when brokers fail
- Managing cluster membership

> [!NOTE]
> If the controller fails, another broker is automatically elected as the new controller.

[↑ Back to Table of Contents](#table-of-contents)

---

## Replication

Replication is how Kafka achieves fault tolerance. Each partition is replicated across multiple brokers.

### Leader and followers

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    REPLICATION (Factor = 3)                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Topic: orders, Partition 0                                                 │
│                                                                             │
│  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐           │
│  │    Broker 0     │   │    Broker 1     │   │    Broker 2     │           │
│  │                 │   │                 │   │                 │           │
│  │  ┌───────────┐  │   │  ┌───────────┐  │   │  ┌───────────┐  │           │
│  │  │  LEADER   │  │   │  │ FOLLOWER  │  │   │  │ FOLLOWER  │  │           │
│  │  │ orders-0  │  │   │  │ orders-0  │  │   │  │ orders-0  │  │           │
│  │  │ [0][1][2] │◄─┼───┼─►│ [0][1][2] │◄─┼───┼─►│ [0][1][2] │  │           │
│  │  └───────────┘  │   │  └───────────┘  │   │  └───────────┘  │           │
│  │       ▲         │   │                 │   │                 │           │
│  └───────┼─────────┘   └─────────────────┘   └─────────────────┘           │
│          │                                                                  │
│    All reads/writes                                                         │
│    go to leader                                                             │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  If Leader (Broker 0) fails:                                                │
│  ─────────────────────────────                                              │
│  1. Controller detects failure                                              │
│  2. Elects Broker 1 or 2 as new leader                                      │
│  3. Clients redirect to new leader                                          │
│  4. No data loss (data was replicated)                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Replication factor

The **replication factor** determines how many copies of each partition exist:

| Factor | Brokers Required | Fault Tolerance |
|--------|------------------|-----------------|
| 1 | 1 | None (development only) |
| 2 | 2 | Can lose 1 broker |
| 3 | 3 | Can lose 2 brokers (recommended) |

### In-sync replicas (ISR)

The **ISR** is the set of replicas that are fully caught up with the leader:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      IN-SYNC REPLICAS (ISR)                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Scenario 1: All replicas in sync                                           │
│  ────────────────────────────────                                           │
│  Leader:   [0][1][2][3][4][5]                                               │
│  Follower1:[0][1][2][3][4][5]  ✓ In sync                                    │
│  Follower2:[0][1][2][3][4][5]  ✓ In sync                                    │
│                                                                             │
│  ISR = {Leader, Follower1, Follower2}                                       │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  Scenario 2: One replica behind                                             │
│  ─────────────────────────────────                                          │
│  Leader:   [0][1][2][3][4][5]                                               │
│  Follower1:[0][1][2][3][4][5]  ✓ In sync                                    │
│  Follower2:[0][1][2][3]        ✗ Behind (removed from ISR)                  │
│                                                                             │
│  ISR = {Leader, Follower1}                                                  │
│                                                                             │
│  When Follower2 catches up, it rejoins the ISR.                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

> [!IMPORTANT]
> Only ISR members can be elected as leader. This ensures no data loss during failover.

[↑ Back to Table of Contents](#table-of-contents)

---

## Producers and consumers

### Producer architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PRODUCER FLOW                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Application                                                                │
│       │                                                                     │
│       ▼                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        PRODUCER                                      │   │
│  │                                                                      │   │
│  │  1. Serialize    2. Partition     3. Batch         4. Send          │   │
│  │  ┌──────────┐   ┌──────────┐    ┌──────────┐    ┌──────────┐       │   │
│  │  │ Key/Val  │──►│ Select   │───►│ Collect  │───►│ Network  │       │   │
│  │  │ to bytes │   │ Partition│    │ Messages │    │ Send     │       │   │
│  │  └──────────┘   └──────────┘    └──────────┘    └──────────┘       │   │
│  │                      │                               │              │   │
│  │                      ▼                               ▼              │   │
│  │               ┌──────────┐                    ┌──────────┐         │   │
│  │               │ Metadata │                    │  Acks    │         │   │
│  │               │ (Topics, │                    │ Handling │         │   │
│  │               │ Leaders) │                    │          │         │   │
│  │               └──────────┘                    └──────────┘         │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                      │                                      │
│                                      ▼                                      │
│                               Kafka Brokers                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Acknowledgment levels (acks)

| Setting | Behavior | Durability | Latency |
|---------|----------|------------|---------|
| `acks=0` | Fire and forget | Lowest | Fastest |
| `acks=1` | Leader acknowledged | Medium | Medium |
| `acks=all` | All ISR acknowledged | Highest | Slowest |

### Consumer architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CONSUMER FLOW                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Kafka Brokers                                                              │
│       │                                                                     │
│       ▼                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        CONSUMER                                      │   │
│  │                                                                      │   │
│  │  1. Fetch        2. Deserialize   3. Process      4. Commit         │   │
│  │  ┌──────────┐   ┌──────────┐    ┌──────────┐    ┌──────────┐       │   │
│  │  │ Poll     │──►│ Bytes to │───►│ Business │───►│ Offset   │       │   │
│  │  │ Messages │   │ Key/Val  │    │ Logic    │    │ Commit   │       │   │
│  │  └──────────┘   └──────────┘    └──────────┘    └──────────┘       │   │
│  │       │                                               │             │   │
│  │       ▼                                               ▼             │   │
│  │  ┌──────────┐                                  ┌──────────┐        │   │
│  │  │ Offset   │                                  │ Consumer │        │   │
│  │  │ Position │                                  │ Group    │        │   │
│  │  │ Tracking │                                  │ Coord.   │        │   │
│  │  └──────────┘                                  └──────────┘        │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                      │                                      │
│                                      ▼                                      │
│                               Application                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Consumer groups

Consumer groups enable parallel consumption and fault tolerance:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      CONSUMER GROUPS                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Topic: orders (4 partitions)                                               │
│                                                                             │
│  Consumer Group A (3 consumers)        Consumer Group B (2 consumers)       │
│  ─────────────────────────────         ─────────────────────────────        │
│                                                                             │
│  P0 ────► Consumer A1                  P0 ────► Consumer B1                 │
│  P1 ────► Consumer A1                  P1 ────► Consumer B1                 │
│  P2 ────► Consumer A2                  P2 ────► Consumer B2                 │
│  P3 ────► Consumer A3                  P3 ────► Consumer B2                 │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  Key Rules:                                                                 │
│  • Each partition → exactly one consumer in the group                       │
│  • One consumer can handle multiple partitions                              │
│  • Different groups consume independently                                   │
│  • Adding consumers (up to partition count) increases parallelism           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

[↑ Back to Table of Contents](#table-of-contents)

---

## ZooKeeper vs KRaft

### The old way: ZooKeeper

Historically, Kafka depended on Apache ZooKeeper for:
- Cluster metadata storage
- Leader election
- Controller election
- Configuration management

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ZOOKEEPER MODE (Legacy)                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      ZOOKEEPER ENSEMBLE                              │   │
│  │   ┌────────┐      ┌────────┐      ┌────────┐                        │   │
│  │   │  ZK 1  │◄────►│  ZK 2  │◄────►│  ZK 3  │                        │   │
│  │   └────────┘      └────────┘      └────────┘                        │   │
│  └────────────────────────────────────┬────────────────────────────────┘   │
│                                       │                                     │
│                                       ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                       KAFKA CLUSTER                                  │   │
│  │   ┌────────┐      ┌────────┐      ┌────────┐                        │   │
│  │   │Broker 1│      │Broker 2│      │Broker 3│                        │   │
│  │   └────────┘      └────────┘      └────────┘                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Drawbacks:                                                                 │
│  • Two systems to operate                                                   │
│  • Metadata stored externally                                               │
│  • Limited scalability                                                      │
│  • Operational complexity                                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### The new way: KRaft

**KRaft** (Kafka Raft) eliminates ZooKeeper by building consensus into Kafka itself:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    KRAFT MODE (Modern - Recommended)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                       KAFKA CLUSTER                                  │   │
│  │                                                                      │   │
│  │   ┌────────────────┐  ┌────────────────┐  ┌────────────────┐       │   │
│  │   │   Broker 1     │  │   Broker 2     │  │   Broker 3     │       │   │
│  │   │                │  │                │  │                │       │   │
│  │   │  ┌──────────┐  │  │  ┌──────────┐  │  │  ┌──────────┐  │       │   │
│  │   │  │Controller│  │  │  │Controller│  │  │  │Controller│  │       │   │
│  │   │  │ (Leader) │◄─┼──┼─►│(Follower)│◄─┼──┼─►│(Follower)│  │       │   │
│  │   │  └──────────┘  │  │  └──────────┘  │  │  └──────────┘  │       │   │
│  │   │                │  │                │  │                │       │   │
│  │   │  ┌──────────┐  │  │  ┌──────────┐  │  │  ┌──────────┐  │       │   │
│  │   │  │  Broker  │  │  │  │  Broker  │  │  │  │  Broker  │  │       │   │
│  │   │  │  Process │  │  │  │  Process │  │  │  │  Process │  │       │   │
│  │   │  └──────────┘  │  │  └──────────┘  │  │  └──────────┘  │       │   │
│  │   └────────────────┘  └────────────────┘  └────────────────┘       │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Benefits:                                                                  │
│  • Single system to operate                                                 │
│  • Metadata stored internally                                               │
│  • Better scalability (millions of partitions)                              │
│  • Simpler deployment                                                       │
│  • Faster recovery                                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Comparison

| Feature | ZooKeeper Mode | KRaft Mode |
|---------|----------------|------------|
| External dependency | Yes (ZooKeeper) | No |
| Partition limit | ~200,000 | Millions |
| Recovery time | Minutes | Seconds |
| Operational complexity | Higher | Lower |
| Status | Deprecated | Recommended |

> [!IMPORTANT]
> **ZooKeeper is deprecated** and will be removed in Kafka 4.0. All new deployments should use KRaft mode.

[↑ Back to Table of Contents](#table-of-contents)

---

## Data flow walkthrough

Let's trace a message through the entire system:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MESSAGE FLOW: End-to-End                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  STEP 1: Application creates message                                        │
│  ────────────────────────────────────                                       │
│  ┌──────────────────────────────────────────────────┐                      │
│  │  order = {"id": "123", "item": "book", "qty": 2} │                      │
│  │  producer.send("orders", key="user-456", order)  │                      │
│  └──────────────────────────────────────────────────┘                      │
│                          │                                                  │
│                          ▼                                                  │
│  STEP 2: Producer determines partition                                      │
│  ─────────────────────────────────────                                      │
│  ┌──────────────────────────────────────────────────┐                      │
│  │  hash("user-456") % 3 = 1  → Partition 1         │                      │
│  └──────────────────────────────────────────────────┘                      │
│                          │                                                  │
│                          ▼                                                  │
│  STEP 3: Producer sends to partition leader                                 │
│  ──────────────────────────────────────────                                 │
│  ┌──────────────────────────────────────────────────┐                      │
│  │  Topic: orders                                    │                      │
│  │  Partition 1 Leader: Broker 2                     │                      │
│  │  Producer → Broker 2                              │                      │
│  └──────────────────────────────────────────────────┘                      │
│                          │                                                  │
│                          ▼                                                  │
│  STEP 4: Leader writes and replicates                                       │
│  ────────────────────────────────────                                       │
│  ┌──────────────────────────────────────────────────┐                      │
│  │  Broker 2 (Leader):                               │                      │
│  │    1. Writes to disk                              │                      │
│  │    2. Assigns offset: 42                          │                      │
│  │    3. Replicates to followers (Broker 1, 3)       │                      │
│  └──────────────────────────────────────────────────┘                      │
│                          │                                                  │
│                          ▼                                                  │
│  STEP 5: Acknowledgment sent                                                │
│  ───────────────────────────                                                │
│  ┌──────────────────────────────────────────────────┐                      │
│  │  (acks=all) Wait for ISR, then ACK to producer   │                      │
│  │  RecordMetadata: topic=orders, partition=1,      │                      │
│  │                  offset=42                        │                      │
│  └──────────────────────────────────────────────────┘                      │
│                          │                                                  │
│                          ▼                                                  │
│  STEP 6: Consumer reads message                                             │
│  ──────────────────────────────                                             │
│  ┌──────────────────────────────────────────────────┐                      │
│  │  Consumer (group: "order-processor"):             │                      │
│  │    1. poll() → fetches from Partition 1 Leader   │                      │
│  │    2. Deserializes message                        │                      │
│  │    3. Processes order                             │                      │
│  │    4. Commits offset 42                           │                      │
│  └──────────────────────────────────────────────────┘                      │
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
│  1. TOPICS AND PARTITIONS                                                   │
│     • Topics are logical categories for messages                            │
│     • Partitions enable parallelism and scalability                         │
│     • Ordering is guaranteed within a partition only                        │
│                                                                             │
│  2. BROKERS AND CLUSTERS                                                    │
│     • Brokers are Kafka servers that store and serve data                   │
│     • Clusters provide fault tolerance and scalability                      │
│     • One broker serves as controller for cluster management                │
│                                                                             │
│  3. REPLICATION                                                             │
│     • Each partition has one leader and multiple followers                  │
│     • ISR (In-Sync Replicas) ensures data durability                        │
│     • Replication factor of 3 is recommended for production                 │
│                                                                             │
│  4. PRODUCERS AND CONSUMERS                                                 │
│     • Producers write to partition leaders                                  │
│     • Consumers read from leaders in consumer groups                        │
│     • Offsets track consumer position                                       │
│                                                                             │
│  5. KRAFT                                                                   │
│     • KRaft replaces ZooKeeper for new deployments                          │
│     • Simpler operations and better scalability                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Knowledge check

Test your understanding before moving on:

1. What is the relationship between topics and partitions?
2. Why do messages with the same key go to the same partition?
3. What is the role of the ISR (In-Sync Replicas)?
4. What happens when a partition leader fails?
5. What is the difference between ZooKeeper mode and KRaft mode?

<details>
<summary>Click to reveal answers</summary>

1. **Topics and partitions:** A topic is a logical grouping of related messages. Each topic is divided into partitions, which are ordered logs that enable parallel processing. Messages are distributed across partitions.

2. **Same key, same partition:** Messages with the same key are hashed to the same partition, ensuring ordering for related messages. For example, all events for "user-123" will be in order because they're in the same partition.

3. **ISR role:** The ISR contains replicas that are fully caught up with the leader. When `acks=all` is used, the producer waits for all ISR members to acknowledge. Only ISR members can be elected as leader, preventing data loss.

4. **Leader failure:** When a leader fails:
   - The controller detects the failure
   - Selects a new leader from the ISR
   - Updates cluster metadata
   - Clients redirect to the new leader
   - No data loss because followers have replicated data

5. **ZooKeeper vs KRaft:**
   - ZooKeeper: External service for metadata and coordination (deprecated)
   - KRaft: Built-in consensus, no external dependency, simpler operations, better scalability (recommended)

</details>

---

**Next:** [Environment Setup →](./03_setup_environment.md)
