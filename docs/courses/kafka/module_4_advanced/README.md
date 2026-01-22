# Module 4: Advanced Kafka

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Module](https://img.shields.io/badge/Module-4_Advanced-blue)

## Module overview

This module covers advanced Kafka topics including stream processing, SQL-based streaming, security, monitoring, and production operations. You learn to build real-time applications and operate Kafka clusters in production.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        MODULE 4: ADVANCED                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐               │
│  │ 13     │  │ 14     │  │ 15     │  │ 16     │  │ 17     │               │
│  │ Kafka  │─►│ ksqlDB │─►│Security│─►│Monitor │─►│Productn│               │
│  │Streams │  │        │  │        │  │        │  │  Ops   │               │
│  └────────┘  └────────┘  └────────┘  └────────┘  └────────┘               │
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

1. Build stream processing applications with Kafka Streams
2. Write SQL queries on streams using ksqlDB
3. Secure Kafka clusters with TLS, SASL, and ACLs
4. Monitor Kafka with metrics, logging, and alerting
5. Operate Kafka in production with proper capacity planning

## Lessons

| # | Lesson | Description |
|---|--------|-------------|
| 13 | [Kafka Streams](./13_kafka_streams.md) | KStream, KTable, joins, aggregations |
| 14 | [ksqlDB](./14_ksqldb.md) | SQL streams, tables, materialized views |
| 15 | [Security](./15_security.md) | TLS, SASL, ACLs, encryption |
| 16 | [Monitoring](./16_monitoring.md) | Metrics, alerting, observability |
| 17 | [Production Operations](./17_production_ops.md) | Capacity planning, upgrades, maintenance |

## Assessment

| Resource | Description |
|----------|-------------|
| [Exercises](./exercises/) | 15 hands-on exercises |
| [Quiz](./quiz_module_4.md) | 15-question assessment (80% to pass) |
| [Project 4](./project_4_production.md) | Build a production-ready Kafka cluster |

## Prerequisites

- Completed Module 3: Intermediate
- Java 17+ installed (for Kafka Streams)
- Understanding of SQL basics

## Time estimate

| Activity | Duration |
|----------|----------|
| Lessons | 5-6 hours |
| Exercises | 3-4 hours |
| Quiz | 20 minutes |
| Project | 4-6 hours |
| **Total** | **12-16 hours** |

## Key concepts covered

### Kafka Streams
- KStream and KTable abstractions
- Stateless transformations (map, filter, flatMap)
- Stateful operations (aggregations, joins)
- Windowed operations
- State stores and interactive queries
- Exactly-once processing

### ksqlDB
- Creating streams and tables
- Push and pull queries
- Joins and aggregations
- Windowed aggregations
- User-defined functions
- Deployment options

### Security
- TLS/SSL encryption
- SASL authentication (PLAIN, SCRAM, GSSAPI)
- Access Control Lists (ACLs)
- Encryption at rest
- Security best practices

### Monitoring
- JMX metrics
- Key metrics to monitor
- Prometheus and Grafana integration
- Alert configuration
- Log aggregation

### Production operations
- Capacity planning
- Hardware recommendations
- Rolling upgrades
- Backup and disaster recovery
- Performance tuning

## Stream processing comparison

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STREAM PROCESSING OPTIONS                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  KAFKA STREAMS                         KSQLDB                               │
│  ─────────────                         ──────                               │
│                                                                             │
│  ┌─────────────────┐                   ┌─────────────────┐                 │
│  │  Java/Scala     │                   │      SQL        │                 │
│  │  Library        │                   │    Interface    │                 │
│  └─────────────────┘                   └─────────────────┘                 │
│                                                                             │
│  • Full programming power              • Familiar SQL syntax                │
│  • Complex business logic              • Quick development                  │
│  • Unit testable                       • Interactive queries                │
│  • Deploy as microservice              • Managed infrastructure             │
│  • Fine-grained control                • Lower learning curve               │
│                                                                             │
│  Use when:                             Use when:                            │
│  • Complex transformations             • SQL expertise available            │
│  • Custom serialization                • Rapid prototyping                  │
│  • Existing Java codebase              • Ad-hoc queries needed              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Project preview: Production cluster

In this module's project, you build a production-ready Kafka environment:

1. **Security**: TLS encryption and SASL authentication
2. **Monitoring**: Prometheus metrics and Grafana dashboards
3. **Alerting**: Configure alerts for key metrics
4. **Testing**: Chaos engineering with broker failures
5. **Documentation**: Runbooks for common operations

## Next module

After completing Module 4, proceed to:

**[Module 5: Capstone Project →](../module_5_project/README.md)**

---

[↑ Back to Course Index](../README.md)
