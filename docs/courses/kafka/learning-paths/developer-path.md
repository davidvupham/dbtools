# Developer Learning Path

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Path](https://img.shields.io/badge/Path-Developer-blue)

## Overview

This learning path is designed for **software developers** who need to build applications that produce and consume Kafka messages. You learn to write reliable, high-performance Kafka applications with proper error handling and exactly-once semantics.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       DEVELOPER LEARNING PATH                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Week 1              Week 2              Week 3              Week 4         │
│  ┌─────────┐        ┌─────────┐        ┌─────────┐        ┌─────────┐     │
│  │ Module  │        │ Module  │        │ Module  │        │ Module  │     │
│  │ 1 & 2   │───────►│   3     │───────►│ 4       │───────►│   5     │     │
│  │         │        │         │        │ (13-14) │        │Capstone │     │
│  │Foundati-│        │ Connect │        │ Streams │        │         │     │
│  │ons &    │        │ Schema  │        │ ksqlDB  │        │         │     │
│  │ Core    │        │ Registry│        │         │        │         │     │
│  └─────────┘        └─────────┘        └─────────┘        └─────────┘     │
│                                                                             │
│  Focus: Architecture   Focus: Data       Focus: Stream      Focus: Apply   │
│         Producer       Contracts         Processing         Everything     │
│         Consumer       Serialization     Real-time          End-to-End     │
│         Error Handling                   Analytics                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Target audience

- Backend developers building microservices
- Data engineers creating pipelines
- Full-stack developers integrating Kafka
- Application developers new to event streaming

## Prerequisites

- Programming experience (Python, Java, or similar)
- Basic understanding of distributed systems
- Docker installed and running
- Command line familiarity

## Learning objectives

By completing this path, you will be able to:

1. **Design** event-driven applications with Kafka
2. **Build** reliable producers with proper acknowledgment settings
3. **Implement** consumers with correct offset management
4. **Handle** errors with dead letter queues and retry patterns
5. **Use** Schema Registry for data contracts
6. **Process** streams in real-time with Kafka Streams or ksqlDB

---

## Week 1: Foundations and core concepts

### Lessons

| Day | Topic | Module | Duration |
|-----|-------|--------|----------|
| 1 | Introduction to Kafka | [01_introduction.md](../module_1_foundations/01_introduction.md) | 1 hour |
| 1 | Architecture overview | [02_architecture.md](../module_1_foundations/02_architecture.md) | 1.5 hours |
| 2 | Environment setup | [03_setup_environment.md](../module_1_foundations/03_setup_environment.md) | 1 hour |
| 2 | First cluster hands-on | [04_first_cluster.md](../module_1_foundations/04_first_cluster.md) | 2 hours |
| 3 | Topics and partitions | [05_topics_partitions.md](../module_2_core_concepts/05_topics_partitions.md) | 1.5 hours |
| 4 | Producers deep dive | [06_producers.md](../module_2_core_concepts/06_producers.md) | 2 hours |
| 5 | Consumers deep dive | [07_consumers.md](../module_2_core_concepts/07_consumers.md) | 2 hours |
| 5 | Consumer groups | [08_consumer_groups.md](../module_2_core_concepts/08_consumer_groups.md) | 1.5 hours |

### Key developer concepts

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PRODUCER CONFIGURATION DECISIONS                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  USE CASE              ACKS      IDEMPOTENCE   BATCHING      COMPRESSION   │
│  ────────────────────────────────────────────────────────────────────────   │
│                                                                             │
│  Financial/Critical    all       true          Small         lz4           │
│  (No data loss)        ───       ────          linger=5ms    ───           │
│                                                                             │
│  High Throughput       1         true          Large         lz4/zstd      │
│  (Metrics, Logs)       ─         ────          linger=50ms   ────────      │
│                                                                             │
│  Fire & Forget         0         false         Large         snappy        │
│  (Non-critical)        ─         ─────         linger=100ms  ──────        │
│                                                                             │
│  Low Latency           1         true          Small         none          │
│  (Real-time)           ─         ────          linger=0ms    ────          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Exercises (Week 1)

1. **Create a multi-partition topic** and produce 1000 messages with keys
2. **Implement a producer** with delivery callbacks and error handling
3. **Build a consumer** that processes messages and commits offsets manually
4. **Set up a consumer group** with 3 consumers and observe partition assignment
5. **Simulate consumer failure** and observe rebalancing

### Quiz checkpoint

Complete [Module 1 Quiz](../module_1_foundations/quiz_module_1.md) and [Module 2 Quiz](../module_2_core_concepts/quiz_module_2.md) before proceeding.

---

## Week 2: Data integration and schema management

### Lessons

| Day | Topic | Module | Duration |
|-----|-------|--------|----------|
| 1 | Kafka Connect basics | [09_kafka_connect.md](../module_3_intermediate/09_kafka_connect.md) | 2 hours |
| 2 | Schema Registry | [10_schema_registry.md](../module_3_intermediate/10_schema_registry.md) | 2 hours |
| 3 | Serialization formats | [11_serialization.md](../module_3_intermediate/11_serialization.md) | 1.5 hours |
| 4 | Exactly-once semantics | [12_exactly_once.md](../module_3_intermediate/12_exactly_once.md) | 2 hours |
| 5 | Project work | [project_3_pipeline.md](../module_3_intermediate/project_3_pipeline.md) | 3 hours |

### Key developer concepts

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SCHEMA COMPATIBILITY MODES                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  MODE              DESCRIPTION                  USE CASE                    │
│  ────────────────────────────────────────────────────────────────────────   │
│                                                                             │
│  BACKWARD          New schema can read old      Safe consumer upgrades      │
│                    data (add optional fields)  (upgrade consumers first)   │
│                                                                             │
│  FORWARD           Old schema can read new      Safe producer upgrades      │
│                    data (delete fields OK)     (upgrade producers first)   │
│                                                                             │
│  FULL              Both backward & forward      Maximum flexibility         │
│                    compatible                  (recommended default)       │
│                                                                             │
│  NONE              No compatibility check       Development only            │
│                    (breaking changes allowed)  (not for production)        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Exercises (Week 2)

1. **Register an Avro schema** and produce/consume with Schema Registry
2. **Evolve a schema** by adding an optional field (backward compatible)
3. **Implement exactly-once** producer with transactions
4. **Build a CDC pipeline** with Debezium connector
5. **Handle schema incompatibility** errors gracefully

---

## Week 3: Stream processing

### Lessons

| Day | Topic | Module | Duration |
|-----|-------|--------|----------|
| 1-2 | Kafka Streams basics | [13_kafka_streams.md](../module_4_advanced/13_kafka_streams.md) | 4 hours |
| 3-4 | ksqlDB | [14_ksqldb.md](../module_4_advanced/14_ksqldb.md) | 4 hours |
| 5 | Choose your tool | Comparison exercise | 2 hours |

### Key developer concepts

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    WHEN TO USE KAFKA STREAMS VS KSQLDB                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  KAFKA STREAMS (Java Library)            KSQLDB (SQL Engine)                │
│  ─────────────────────────────           ─────────────────────              │
│                                                                             │
│  ✓ Complex business logic                ✓ Familiar SQL syntax              │
│  ✓ Custom serialization                  ✓ Quick prototyping                │
│  ✓ Embedded in microservices             ✓ Ad-hoc queries                   │
│  ✓ Full control over processing          ✓ No JVM required                  │
│  ✓ Unit testable with TopologyTestDriver ✓ Managed infrastructure           │
│                                                                             │
│  Use for:                                Use for:                           │
│  • Complex event processing              • Real-time dashboards             │
│  • Custom aggregations                   • Simple transformations           │
│  • When Java/Kotlin is your stack        • When SQL skills available        │
│  • Microservice integration              • Rapid development                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Exercises (Week 3)

1. **Build a Kafka Streams app** that filters and transforms messages
2. **Implement a windowed aggregation** (count events per minute)
3. **Create a ksqlDB stream** from a Kafka topic
4. **Write a ksqlDB query** with joins between stream and table
5. **Compare latency and throughput** between Streams and ksqlDB

---

## Week 4: Capstone project

### Project: Event-driven order processing system

Build a complete e-commerce backend with:

1. **Order Service** - Produces order events with Avro schemas
2. **Validation Service** - Validates orders using Kafka Streams
3. **Inventory Service** - Updates stock with exactly-once semantics
4. **Analytics** - Real-time dashboard with ksqlDB

See [Project 5: Capstone](../module_5_project/project_5_capstone.md) for full requirements.

---

## Developer best practices checklist

### Producer best practices

- [ ] Enable idempotence (`enable.idempotence=true`) for critical data
- [ ] Use `acks=all` for durability, `acks=1` for performance
- [ ] Set appropriate `retries` (default is now MAX_INT)
- [ ] Configure `delivery.timeout.ms` for total retry time
- [ ] Use message keys for ordering guarantees
- [ ] Implement delivery callbacks for error handling
- [ ] Call `flush()` before application shutdown
- [ ] Use compression (`lz4` recommended) for throughput

### Consumer best practices

- [ ] Choose `auto.offset.reset` carefully (`earliest` vs `latest`)
- [ ] Use manual offset commits for exactly-once processing
- [ ] Handle rebalancing with `ConsumerRebalanceListener`
- [ ] Set `max.poll.interval.ms` based on processing time
- [ ] Implement graceful shutdown with `wakeup()`
- [ ] Use dead letter queues for unprocessable messages
- [ ] Monitor consumer lag

### Error handling patterns

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ERROR HANDLING PATTERNS                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. RETRY WITH BACKOFF                                                      │
│     ─────────────────────                                                   │
│     message ──► process ──► fail ──► wait ──► retry (up to N times)         │
│                                                                             │
│  2. DEAD LETTER QUEUE                                                       │
│     ──────────────────────                                                  │
│     message ──► process ──► fail ──► retry ──► DLQ topic                    │
│                                      (after N failures)                     │
│                                                                             │
│  3. RETRY TOPICS (Exponential Backoff)                                      │
│     ────────────────────────────────────                                    │
│     main ──► retry-1 (1s) ──► retry-2 (10s) ──► retry-3 (60s) ──► DLQ      │
│                                                                             │
│  4. CIRCUIT BREAKER                                                         │
│     ────────────────────                                                    │
│     If errors > threshold: pause consumption, alert, wait for recovery      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Assessment

| Assessment | Passing Score | Description |
|------------|---------------|-------------|
| Module 1 Quiz | 80% (12/15) | Foundations concepts |
| Module 2 Quiz | 80% (12/15) | Core concepts |
| Module 3 Quiz | 80% (12/15) | Integration patterns |
| Module 4 Quiz | 80% (12/15) | Stream processing |
| Capstone Project | Complete all features | End-to-end system |

---

## Resources

### Documentation
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Confluent Developer Portal](https://developer.confluent.io/)
- [Kafka Streams Documentation](https://kafka.apache.org/documentation/streams/)

### Books
- "Kafka: The Definitive Guide" (O'Reilly)
- "Designing Event-Driven Systems" (Confluent)
- "Kafka Streams in Action" (Manning)

### Community
- [Confluent Community Slack](https://launchpass.com/confluentcommunity)
- [Apache Kafka Mailing Lists](https://kafka.apache.org/contact)
- [Stack Overflow - kafka tag](https://stackoverflow.com/questions/tagged/apache-kafka)

---

**Next:** [Administrator Learning Path →](./administrator-path.md)
