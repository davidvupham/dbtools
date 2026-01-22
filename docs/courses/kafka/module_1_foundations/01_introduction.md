# Introduction to Apache Kafka

**[← Back to Module 1](./README.md)** | **[Next: Architecture →](./02_architecture.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Module](https://img.shields.io/badge/Module-1_Foundations-blue)

## Table of contents

- [Learning objectives](#learning-objectives)
- [What is Apache Kafka?](#what-is-apache-kafka)
- [Why use Kafka?](#why-use-kafka)
- [Kafka vs traditional messaging](#kafka-vs-traditional-messaging)
- [Real-world use cases](#real-world-use-cases)
- [The Kafka ecosystem](#the-kafka-ecosystem)
- [Key takeaways](#key-takeaways)
- [Knowledge check](#knowledge-check)

---

## Learning objectives

By the end of this lesson, you will be able to:

1. Define what Apache Kafka is and its primary purpose
2. Explain why organizations choose Kafka over traditional messaging systems
3. Identify common use cases for Kafka
4. Describe the components of the Kafka ecosystem

---

## What is Apache Kafka?

Apache Kafka is a **distributed event streaming platform** capable of handling trillions of events per day. Originally developed at LinkedIn in 2011 and later open-sourced, Kafka has become the de facto standard for building real-time data pipelines and streaming applications.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         WHAT KAFKA DOES                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Data Sources                  KAFKA                    Data Destinations  │
│  ┌───────────┐            ┌─────────────────┐           ┌───────────┐      │
│  │ Databases │───────────►│                 │──────────►│ Analytics │      │
│  └───────────┘            │   Publish &     │           └───────────┘      │
│  ┌───────────┐            │   Subscribe     │           ┌───────────┐      │
│  │   Apps    │───────────►│   to Streams    │──────────►│ Databases │      │
│  └───────────┘            │   of Events     │           └───────────┘      │
│  ┌───────────┐            │                 │           ┌───────────┐      │
│  │   IoT     │───────────►│                 │──────────►│   Apps    │      │
│  └───────────┘            └─────────────────┘           └───────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Three core capabilities

1. **Publish and Subscribe**: Read and write streams of events (similar to a messaging system)
2. **Store**: Store streams of events durably and reliably for as long as you want
3. **Process**: Process streams of events as they occur or retrospectively

### The event streaming paradigm

Think of Kafka as the **central nervous system** for your data. Instead of applications directly communicating with each other, they communicate through Kafka:

```
Traditional Architecture          Event Streaming Architecture

   ┌───┐    ┌───┐                    ┌───┐
   │ A │────│ B │                    │ A │───┐
   └───┘    └───┘                    └───┘   │     ┌─────────┐
     │        │                              ├────►│  KAFKA  │
   ┌───┐    ┌───┐                    ┌───┐   │     └────┬────┘
   │ C │────│ D │                    │ B │───┘          │
   └───┘    └───┘                    └───┘              │
                                                       │
   Point-to-point                    ┌───┐             │
   connections grow                  │ C │◄────────────┤
   exponentially                     └───┘             │
   (n*(n-1)/2)                       ┌───┐             │
                                     │ D │◄────────────┘
                                     └───┘

                                     Linear connections
                                     (2n)
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Why use Kafka?

### Scale

Kafka handles **millions of messages per second** with sub-second latency. Companies like LinkedIn process over 7 trillion messages per day, and Netflix processes trillions of events daily.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        KAFKA AT SCALE                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  LinkedIn:    7+ trillion messages/day                                      │
│  Netflix:     Trillions of events/day                                       │
│  Uber:        Petabytes of data/day                                         │
│  Spotify:     500+ billion events/day                                       │
│                                                                             │
│  Why so much?                                                               │
│  ─────────────                                                              │
│  • User clicks, views, searches                                             │
│  • Application logs and metrics                                             │
│  • IoT sensor data                                                          │
│  • Database change events                                                   │
│  • Payment transactions                                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Durability

Unlike traditional message queues that delete messages after consumption, Kafka **persists messages to disk** and replicates them across multiple servers. You can replay messages at any time.

### Fault tolerance

Kafka is designed to handle failures gracefully:
- Data is replicated across multiple brokers
- If a broker fails, another takes over automatically
- No single point of failure

### Real-time processing

Process data as it arrives with millisecond latency, enabling:
- Real-time fraud detection
- Live dashboards
- Instant notifications
- Dynamic pricing

### Decoupling

Producers and consumers are completely decoupled:
- Producers don't know who consumes their data
- Consumers don't know who produces the data
- Add new consumers without changing producers

[↑ Back to Table of Contents](#table-of-contents)

---

## Kafka vs traditional messaging

### Traditional message queues (RabbitMQ, ActiveMQ)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TRADITIONAL MESSAGE QUEUE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Producer ──► [Queue] ──► Consumer                                          │
│                                                                             │
│  • Message deleted after consumption                                        │
│  • One message → one consumer (usually)                                     │
│  • Push-based delivery                                                      │
│  • Best for: Task distribution, request/reply                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Kafka (distributed log)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         KAFKA LOG                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Producer ──► [──Log──] ◄── Consumer A (offset 5)                           │
│               [0][1][2][3][4][5][6][7][8]                                    │
│                              ◄── Consumer B (offset 3)                      │
│                                                                             │
│  • Messages retained (configurable)                                         │
│  • One message → many consumers                                             │
│  • Pull-based delivery                                                      │
│  • Best for: Event streaming, data pipelines                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Comparison table

| Feature | Traditional MQ | Kafka |
|---------|----------------|-------|
| **Data retention** | Until consumed | Configurable (forever) |
| **Consumer model** | Push | Pull |
| **Replay** | No | Yes |
| **Throughput** | Thousands/sec | Millions/sec |
| **Ordering** | Per queue | Per partition |
| **Consumer count** | Limited | Unlimited |
| **Use case** | Task queues | Event streaming |

### When to use which?

**Use traditional MQ when:**
- You need request/reply patterns
- Message order across the entire queue matters
- You want automatic message acknowledgment
- Simple task distribution

**Use Kafka when:**
- You need event replay capability
- Multiple consumers need the same data
- You need high throughput
- You're building data pipelines
- You need long-term message storage

[↑ Back to Table of Contents](#table-of-contents)

---

## Real-world use cases

### 1. Real-time analytics

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     REAL-TIME ANALYTICS PIPELINE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [Web App] ──► [Kafka] ──► [Stream Processing] ──► [Dashboard]              │
│                   │                                                         │
│                   └──────► [Data Lake] ──► [Batch Analytics]                │
│                                                                             │
│  Example: Spotify                                                           │
│  • Track play events in real-time                                           │
│  • Update listening statistics instantly                                    │
│  • Power "Wrapped" year-end summaries                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2. Microservices communication

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    EVENT-DRIVEN MICROSERVICES                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [Order Service] ──► "order.created" ──► [Inventory Service]                │
│                              │                                              │
│                              ├──────────► [Payment Service]                 │
│                              │                                              │
│                              └──────────► [Notification Service]            │
│                                                                             │
│  Example: Uber                                                              │
│  • Ride request events                                                      │
│  • Driver location updates                                                  │
│  • Payment processing                                                       │
│  • 300+ microservices communicate via Kafka                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3. Log aggregation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        LOG AGGREGATION                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [Server 1] ──┐                                                             │
│  [Server 2] ──┼──► [Kafka] ──► [Elasticsearch] ──► [Kibana]                 │
│  [Server 3] ──┘                                                             │
│                                                                             │
│  Example: Netflix                                                           │
│  • Collect logs from thousands of servers                                   │
│  • Real-time error detection                                                │
│  • Centralized log analysis                                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4. Change data capture (CDC)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     CHANGE DATA CAPTURE                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [PostgreSQL] ──► [Debezium] ──► [Kafka] ──► [Elasticsearch]                │
│                                     │                                       │
│                                     └────► [Data Warehouse]                 │
│                                                                             │
│  Example: Database Replication                                              │
│  • Capture every INSERT, UPDATE, DELETE                                     │
│  • Stream changes to search indexes                                         │
│  • Keep data warehouses in sync                                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5. Fraud detection

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      FRAUD DETECTION                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [Transaction] ──► [Kafka] ──► [ML Model] ──► [Alert/Block]                 │
│                                    │                                        │
│                                    ▼                                        │
│                              [Pattern DB]                                   │
│                                                                             │
│  Example: Financial Services                                                │
│  • Analyze transactions in milliseconds                                     │
│  • Detect unusual patterns                                                  │
│  • Block fraudulent transactions in real-time                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

[↑ Back to Table of Contents](#table-of-contents)

---

## The Kafka ecosystem

Kafka is more than just a message broker. It's a complete ecosystem for event streaming:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         KAFKA ECOSYSTEM                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                          ┌─────────────────┐                                │
│                          │  KAFKA CORE     │                                │
│                          │  (Brokers)      │                                │
│                          └────────┬────────┘                                │
│                                   │                                         │
│         ┌───────────┬─────────────┼─────────────┬───────────┐              │
│         │           │             │             │           │              │
│         ▼           ▼             ▼             ▼           ▼              │
│   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│   │  Kafka   │ │  Schema  │ │  Kafka   │ │  ksqlDB  │ │  Kafka   │        │
│   │ Connect  │ │ Registry │ │ Streams  │ │          │ │  REST    │        │
│   └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘        │
│   Data         Schema       Stream       SQL-based    HTTP                 │
│   Integration  Evolution    Processing   Processing   Interface            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Component overview

| Component | Purpose | Covered In |
|-----------|---------|------------|
| **Kafka Core** | Distributed event store and streaming | Module 1-2 |
| **Kafka Connect** | Data integration (import/export) | Module 3 |
| **Schema Registry** | Schema management and evolution | Module 3 |
| **Kafka Streams** | Java library for stream processing | Module 4 |
| **ksqlDB** | SQL interface for stream processing | Module 4 |
| **Kafka REST Proxy** | HTTP interface to Kafka | Reference |

### Key terms to know

| Term | Definition |
|------|------------|
| **Event** | A record of something that happened |
| **Topic** | A named channel for organizing events |
| **Partition** | A subset of a topic for parallelism |
| **Broker** | A Kafka server |
| **Producer** | An application that sends events |
| **Consumer** | An application that reads events |
| **Offset** | The position of an event in a partition |

> [!NOTE]
> Don't worry about memorizing all these terms now. We cover each in detail throughout the course. See the [Glossary](../glossary.md) for complete definitions.

[↑ Back to Table of Contents](#table-of-contents)

---

## Key takeaways

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        KEY TAKEAWAYS                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. Kafka is a distributed event streaming platform, not just a message    │
│     queue. It stores events durably and allows replay.                      │
│                                                                             │
│  2. Kafka excels at high-throughput, real-time data pipelines with         │
│     built-in fault tolerance and horizontal scalability.                    │
│                                                                             │
│  3. Unlike traditional message queues, Kafka retains messages and          │
│     supports multiple independent consumers.                                │
│                                                                             │
│  4. Common use cases include analytics, microservices communication,        │
│     log aggregation, CDC, and fraud detection.                              │
│                                                                             │
│  5. The Kafka ecosystem includes Connect, Schema Registry, Streams,         │
│     and ksqlDB for complete data streaming solutions.                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Knowledge check

Test your understanding before moving on:

1. What are the three core capabilities of Kafka?
2. Why might you choose Kafka over a traditional message queue like RabbitMQ?
3. Name three real-world use cases for Kafka.
4. What is the difference between push-based and pull-based message delivery?
5. What component would you use to import data from a database into Kafka?

<details>
<summary>Click to reveal answers</summary>

1. **Three core capabilities:** Publish and subscribe, store, and process streams of events.

2. **Kafka advantages over RabbitMQ:**
   - Message replay capability
   - Higher throughput (millions/sec vs thousands/sec)
   - Long-term message retention
   - Multiple consumers can read the same data independently

3. **Three use cases (any of these):**
   - Real-time analytics
   - Microservices communication
   - Log aggregation
   - Change data capture (CDC)
   - Fraud detection
   - IoT data collection

4. **Push vs pull:**
   - Push: The broker sends messages to consumers immediately
   - Pull: Consumers request messages from the broker when ready (Kafka uses this)

5. **Kafka Connect** is used to import/export data between Kafka and external systems.

</details>

---

**Next:** [Kafka Architecture Deep Dive →](./02_architecture.md)
