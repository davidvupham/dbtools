# Module 3: Intermediate Kafka

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Module](https://img.shields.io/badge/Module-3_Intermediate-blue)

## Module overview

This module covers Kafka's data integration and schema management capabilities. You learn to build robust data pipelines with Kafka Connect and ensure data quality with Schema Registry.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        MODULE 3: INTERMEDIATE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐ │
│  │ 09           │   │ 10           │   │ 11           │   │ 12           │ │
│  │ Kafka        │──►│ Schema       │──►│ Serializ-    │──►│ Exactly-     │ │
│  │ Connect      │   │ Registry     │   │ ation        │   │ Once         │ │
│  └──────────────┘   └──────────────┘   └──────────────┘   └──────────────┘ │
│                                                                             │
│                              │                                              │
│                              ▼                                              │
│                    ┌────────────────────┐                                   │
│                    │  Exercises + Quiz  │                                   │
│                    │     + Project      │                                   │
│                    └────────────────────┘                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Learning objectives

By completing this module, you will be able to:

1. Build data pipelines using Kafka Connect
2. Configure and use source and sink connectors
3. Implement schema management with Schema Registry
4. Handle schema evolution gracefully
5. Choose appropriate serialization formats (Avro, Protobuf, JSON Schema)
6. Understand and configure exactly-once semantics

## Lessons

| # | Lesson | Description |
|---|--------|-------------|
| 09 | [Kafka Connect](./09_kafka_connect.md) | Connectors, workers, transformations |
| 10 | [Schema Registry](./10_schema_registry.md) | Schema management, evolution, compatibility |
| 11 | [Serialization](./11_serialization.md) | Avro, Protobuf, JSON Schema |
| 12 | [Exactly-Once Semantics](./12_exactly_once.md) | Transactions, idempotence, EOS |

## Assessment

| Resource | Description |
|----------|-------------|
| [Exercises](./exercises/) | 10 hands-on exercises |
| [Quiz](./quiz_module_3.md) | 15-question assessment (80% to pass) |
| [Project 3](./project_3_pipeline.md) | Build a CDC data pipeline |

## Prerequisites

- Completed Module 2: Core Concepts
- Docker environment running with full stack
- Basic SQL knowledge (for Connect exercises)

## Time estimate

| Activity | Duration |
|----------|----------|
| Lessons | 3-4 hours |
| Exercises | 2-3 hours |
| Quiz | 20 minutes |
| Project | 3-4 hours |
| **Total** | **8-12 hours** |

## Key concepts covered

### Kafka Connect
- Source and sink connectors
- Standalone vs distributed mode
- Single Message Transforms (SMTs)
- Dead letter queues
- Connector monitoring

### Schema Registry
- Schema storage and retrieval
- Compatibility modes (backward, forward, full)
- Schema evolution strategies
- Subject naming strategies

### Serialization formats
- Apache Avro
- Protocol Buffers
- JSON Schema
- Schema-on-read vs schema-on-write

### Exactly-once semantics
- Idempotent producers
- Transactional producers
- Consumer read isolation

## Architecture preview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DATA PIPELINE ARCHITECTURE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────┐   │
│  │PostgreSQL│────►│ Source       │────►│   KAFKA     │────►│  Sink    │   │
│  │          │     │ Connector    │     │   TOPIC     │     │ Connector│   │
│  └──────────┘     └──────────────┘     └──────┬──────┘     └────┬─────┘   │
│                          │                    │                  │         │
│                          │              ┌─────▼─────┐            │         │
│                          └─────────────►│  Schema   │◄───────────┘         │
│                                         │ Registry  │                      │
│                                         └───────────┘                      │
│                                                                             │
│  Debezium captures CDC events, validates against schema, writes to Kafka   │
│  Sink connector reads, deserializes, and writes to destination             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Project preview: CDC Pipeline

In this module's project, you build a complete Change Data Capture (CDC) pipeline:

1. **Source**: PostgreSQL database with sample data
2. **Connector**: Debezium PostgreSQL connector
3. **Schema**: Avro schemas with Schema Registry
4. **Sink**: Elasticsearch for search, or another database
5. **Monitoring**: Track connector health and lag

## Next module

After completing Module 3, proceed to:

**[Module 4: Advanced →](../module_4_advanced/README.md)**

---

[↑ Back to Course Index](../README.md)
