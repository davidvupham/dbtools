# Kafka Glossary

**[← Back to Course Index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Apache_Kafka-blue)

> [!IMPORTANT]
> **Related Docs:** [Quick Reference](./quick_reference.md) | [Course Overview](./course_overview.md)

## Table of contents

- [Core concepts](#core-concepts)
- [Architecture terms](#architecture-terms)
- [Producer terms](#producer-terms)
- [Consumer terms](#consumer-terms)
- [Kafka Connect terms](#kafka-connect-terms)
- [Kafka Streams terms](#kafka-streams-terms)
- [Security terms](#security-terms)
- [Operations terms](#operations-terms)

---

## Core concepts

### Broker
A Kafka server that stores data and serves client requests. A Kafka cluster consists of one or more brokers. Each broker is identified by a unique ID.

```
┌──────────────────────────────────────────┐
│            KAFKA CLUSTER                 │
│  ┌────────┐  ┌────────┐  ┌────────┐     │
│  │Broker 1│  │Broker 2│  │Broker 3│     │
│  │ ID: 1  │  │ ID: 2  │  │ ID: 3  │     │
│  └────────┘  └────────┘  └────────┘     │
└──────────────────────────────────────────┘
```

### Topic
A named category or feed to which records are published. Topics are append-only, immutable logs of events. Topics are identified by unique names within a cluster.

### Partition
A topic is split into partitions, which are ordered, immutable sequences of records. Each partition is an independent log. Partitions enable parallel processing and scalability.

```
Topic: orders
┌────────────────────────────────────────┐
│  Partition 0: [0][1][2][3][4][5]...    │
│  Partition 1: [0][1][2][3]...          │
│  Partition 2: [0][1][2][3][4][5][6]... │
└────────────────────────────────────────┘
```

### Offset
A unique sequential ID for each record within a partition. Offsets are immutable and never reused. Consumers use offsets to track their position.

### Record (Message)
The fundamental unit of data in Kafka. A record consists of:
- **Key** (optional): Used for partitioning
- **Value**: The actual data payload
- **Timestamp**: When the record was created
- **Headers** (optional): Key-value metadata

### Producer
A client application that publishes records to Kafka topics.

### Consumer
A client application that reads records from Kafka topics.

### Consumer Group
A group of consumers that work together to consume records from topics. Each partition is consumed by only one consumer in the group, enabling parallel processing.

[↑ Back to Table of Contents](#table-of-contents)

---

## Architecture terms

### Cluster
A group of Kafka brokers working together. Clusters provide fault tolerance and scalability.

### Controller
A broker elected to manage administrative tasks like partition leadership assignment and broker failure detection. In KRaft mode, this is managed by the quorum controller.

### Leader
The broker responsible for all reads and writes for a partition. Each partition has exactly one leader.

### Follower
A broker that replicates data from the leader. Followers can become leaders if the current leader fails.

### ISR (In-Sync Replicas)
The set of replicas that are fully caught up with the leader. Only ISR members can be elected as the new leader.

```
Partition Leadership
┌─────────────────────────────────────────────────┐
│  Partition 0:                                   │
│    Leader: Broker 1                             │
│    Followers: Broker 2, Broker 3                │
│    ISR: [1, 2, 3]                               │
│                                                 │
│  Partition 1:                                   │
│    Leader: Broker 2                             │
│    Followers: Broker 1, Broker 3                │
│    ISR: [2, 1, 3]                               │
└─────────────────────────────────────────────────┘
```

### Replication Factor
The number of copies of each partition across brokers. A replication factor of 3 means each partition exists on 3 different brokers.

### ZooKeeper
A distributed coordination service historically used by Kafka for cluster metadata and leader election. Being phased out in favor of KRaft.

### KRaft (Kafka Raft)
Kafka's built-in consensus protocol that replaces ZooKeeper. Uses the Raft algorithm for leader election and metadata management. Production-ready since Kafka 3.3.

### Log Segment
The physical storage unit for partition data. Partitions are divided into segments (typically 1GB each) for easier management.

### Retention
How long Kafka keeps data. Can be configured by time (e.g., 7 days) or size (e.g., 100GB).

[↑ Back to Table of Contents](#table-of-contents)

---

## Producer terms

### Acknowledgment (acks)
Producer configuration that controls durability guarantees:
- `acks=0`: Fire and forget (no acknowledgment)
- `acks=1`: Leader acknowledged
- `acks=all` or `acks=-1`: All ISR replicas acknowledged

### Batch
Producers group records into batches for efficiency. Controlled by `batch.size` and `linger.ms` settings.

### Partitioner
Logic that determines which partition a record goes to. Default uses key hash or round-robin.

### Idempotent Producer
A producer that guarantees exactly-once delivery by assigning sequence numbers to records. Enabled with `enable.idempotence=true`.

### Transactional Producer
A producer that can send records atomically across multiple partitions using transactions.

[↑ Back to Table of Contents](#table-of-contents)

---

## Consumer terms

### Poll
The action of fetching records from Kafka. Consumers call `poll()` to retrieve batches of records.

### Commit
Saving the current offset position so the consumer can resume from that point. Can be automatic or manual.

### Rebalance
The process of redistributing partitions among consumers in a group when consumers join or leave.

### Lag
The difference between the latest offset in a partition and the consumer's current committed offset. High lag indicates slow consumers.

```
Consumer Lag Visualization
┌─────────────────────────────────────────────────┐
│  Partition 0:                                   │
│  [0][1][2][3][4][5][6][7][8][9]                 │
│              ▲              ▲                   │
│              │              │                   │
│        Consumer Offset   Latest Offset          │
│              (5)            (9)                 │
│                                                 │
│        Lag = 9 - 5 = 4 messages                 │
└─────────────────────────────────────────────────┘
```

### Heartbeat
Periodic signal from consumer to coordinator indicating it's alive. Missed heartbeats trigger rebalancing.

### Session Timeout
Maximum time a consumer can be unresponsive before being removed from the group.

### Auto Offset Reset
What to do when no committed offset exists:
- `earliest`: Start from the beginning
- `latest`: Start from the end (new messages only)
- `none`: Throw an error

[↑ Back to Table of Contents](#table-of-contents)

---

## Kafka Connect terms

### Connector
A pluggable component that moves data between Kafka and external systems. Two types:
- **Source Connector**: Imports data into Kafka
- **Sink Connector**: Exports data from Kafka

### Task
The unit of parallelism in Kafka Connect. Connectors are divided into tasks for parallel execution.

### Worker
A JVM process that executes connectors and tasks. Can run in standalone or distributed mode.

### Converter
Transforms data between Kafka Connect's internal format and the wire format (JSON, Avro, etc.).

### Transform (SMT)
Single Message Transform - lightweight modification of records as they flow through Connect.

### Dead Letter Queue (DLQ)
A topic where failed records are sent instead of causing the connector to fail.

[↑ Back to Table of Contents](#table-of-contents)

---

## Kafka Streams terms

### KStream
An abstraction representing an unbounded stream of records. Each record is independent.

### KTable
An abstraction representing a changelog stream where each record is an update. Only the latest value for each key is kept.

### GlobalKTable
A KTable that is fully replicated on each application instance, useful for lookups.

### State Store
Local storage used by Kafka Streams for stateful operations like aggregations and joins.

### Windowing
Grouping records by time windows for aggregation:
- **Tumbling**: Fixed-size, non-overlapping windows
- **Hopping**: Fixed-size, overlapping windows
- **Sliding**: Continuous windows
- **Session**: Dynamic windows based on activity

```
Window Types
┌────────────────────────────────────────────────────────────┐
│  Tumbling (5 min):                                         │
│  [──────][──────][──────][──────]                          │
│                                                            │
│  Hopping (5 min, advance 2 min):                           │
│  [──────]                                                  │
│     [──────]                                               │
│        [──────]                                            │
│                                                            │
│  Session (5 min inactivity gap):                           │
│  [────][───────────][──]                                   │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Topology
The processing logic of a Kafka Streams application, consisting of source, processor, and sink nodes.

[↑ Back to Table of Contents](#table-of-contents)

---

## Security terms

### SSL/TLS
Encryption for data in transit. Uses certificates for both encryption and authentication.

### SASL
Simple Authentication and Security Layer. Supports various mechanisms:
- **PLAIN**: Username/password (use with TLS)
- **SCRAM**: Salted Challenge Response (more secure)
- **GSSAPI**: Kerberos authentication
- **OAUTHBEARER**: OAuth 2.0 tokens

### ACL (Access Control List)
Rules defining what operations principals can perform on resources (topics, consumer groups, etc.).

```
ACL Example
┌─────────────────────────────────────────────────────────────┐
│  Principal: User:alice                                      │
│  Resource: Topic:orders                                     │
│  Operation: Read, Write                                     │
│  Permission: Allow                                          │
└─────────────────────────────────────────────────────────────┘
```

### Principal
An identity (user, service account) that can be authenticated and authorized.

### Delegation Token
A lightweight, renewable token for authentication that avoids repeated SASL handshakes.

[↑ Back to Table of Contents](#table-of-contents)

---

## Operations terms

### Reassignment
Moving partition replicas between brokers for load balancing or maintenance.

### Preferred Leader Election
Restoring leadership to the "preferred" replica (usually the first in the replica list).

### Under-Replicated Partition
A partition where one or more followers have fallen behind the leader.

### Offline Partition
A partition with no available leader, causing unavailability.

### Throughput
The rate of data flow, measured in messages/second or bytes/second.

### Latency
The time delay between producing and consuming a message.

### Consumer Lag
The delay between when messages are produced and when they are consumed, measured in number of messages.

### Compaction
Log compaction retains only the latest value for each key, useful for changelogs.

```
Log Compaction
Before: [K1:A][K2:B][K1:C][K3:D][K2:E][K1:F]
After:  [K3:D][K2:E][K1:F]
```

[↑ Back to Table of Contents](#table-of-contents)

---

**Next:** [Quick Reference →](./quick_reference.md)
