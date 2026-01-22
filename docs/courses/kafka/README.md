# Apache Kafka Engineering Course

**[← Back to Courses Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Apache_Kafka-blue)

> [!IMPORTANT]
> **Related Docs:** [Course Overview](./course_overview.md) | [Quick Reference](./quick_reference.md) | [Glossary](./glossary.md)

## Introduction

This is a **comprehensive course** on Apache Kafka, the leading distributed event streaming platform used by over 80% of Fortune 100 companies including Netflix, Uber, LinkedIn, and Airbnb.

**Goal:** Transform from a Kafka beginner to a production-ready Kafka Engineer.
**Philosophy:** Learn by Doing. You will build **5 Real-World Applications** throughout this course.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         KAFKA LEARNING JOURNEY                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Module 1          Module 2          Module 3          Module 4            │
│   ┌───────┐         ┌───────┐         ┌───────┐         ┌───────┐          │
│   │       │         │       │         │       │         │       │          │
│   │ Found │ ──────► │ Core  │ ──────► │ Inter │ ──────► │  Adv  │          │
│   │ation  │         │Concept│         │mediate│         │anced  │          │
│   │       │         │       │         │       │         │       │          │
│   └───────┘         └───────┘         └───────┘         └───────┘          │
│       │                 │                 │                 │               │
│       ▼                 ▼                 ▼                 ▼               │
│   Project 1         Project 2         Project 3         Project 4          │
│   CLI Tool          Producer/         Stream            Production         │
│                     Consumer          Pipeline          Cluster            │
│                                                                             │
│                              Module 5: Capstone                             │
│                         ┌─────────────────────────┐                         │
│                         │  Event-Driven Order     │                         │
│                         │  Processing System      │                         │
│                         └─────────────────────────┘                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Directory structure

```text
docs/courses/kafka/
├── README.md                  <-- You are here (Navigation Hub)
├── course_overview.md         <-- Learning objectives, prerequisites
├── quick_reference.md         <-- Common commands cheat sheet
├── glossary.md                <-- Terminology definitions
├── module_1_foundations/      <-- Getting started with Kafka
│   ├── 01_introduction.md
│   ├── 02_architecture.md
│   ├── 03_setup_environment.md
│   ├── 04_first_cluster.md
│   ├── exercises/
│   ├── quiz_module_1.md
│   └── project_1_cli_tool.md
├── module_2_core_concepts/    <-- Producers, Consumers, Topics
│   ├── 05_topics_partitions.md
│   ├── 06_producers.md
│   ├── 07_consumers.md
│   ├── 08_consumer_groups.md
│   ├── exercises/
│   ├── quiz_module_2.md
│   └── project_2_messaging.md
├── module_3_intermediate/     <-- Kafka Connect, Schema Registry
│   ├── 09_kafka_connect.md
│   ├── 10_schema_registry.md
│   ├── 11_serialization.md
│   ├── 12_exactly_once.md
│   ├── exercises/
│   ├── quiz_module_3.md
│   └── project_3_pipeline.md
├── module_4_advanced/         <-- Kafka Streams, ksqlDB, Security
│   ├── 13_kafka_streams.md
│   ├── 14_ksqldb.md
│   ├── 15_security.md
│   ├── 16_monitoring.md
│   ├── 17_production_ops.md
│   ├── exercises/
│   ├── quiz_module_4.md
│   └── project_4_production.md
├── module_5_project/          <-- Capstone project
│   └── project_5_capstone.md
├── docker/                    <-- Docker Compose for tutorials
└── scripts/                   <-- Helper scripts
```

## Quick resources

- **[Course Overview](./course_overview.md)** - Learning objectives, prerequisites
- **[Quick Reference](./quick_reference.md)** - Common commands and scripts cheat sheet
- **[Glossary](./glossary.md)** - Terminology definitions
- **[Docker Setup](./docker/README.md)** - Container configurations
- **[Configuration Guide](./reference/configuration-guide.md)** - Configuration decisions by use case
- **[Troubleshooting Guide](./troubleshooting.md)** - Common issues and solutions

---

## Choose your learning path

> [!TIP]
> **We offer two dedicated learning paths based on your role.** Each path is a 4-week structured program with role-specific content, exercises, and projects.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CHOOSE YOUR LEARNING PATH                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────┐     ┌─────────────────────────────┐       │
│  │      DEVELOPER PATH         │     │    ADMINISTRATOR PATH       │       │
│  │         4 WEEKS             │     │         4 WEEKS             │       │
│  ├─────────────────────────────┤     ├─────────────────────────────┤       │
│  │                             │     │                             │       │
│  │  • Producer/Consumer APIs   │     │  • Cluster Architecture     │       │
│  │  • Schema Registry          │     │  • Security (TLS, SASL)     │       │
│  │  • Kafka Streams            │     │  • Monitoring & Metrics     │       │
│  │  • ksqlDB                   │     │  • Production Operations    │       │
│  │  • Error Handling           │     │  • Troubleshooting          │       │
│  │  • Testing Patterns         │     │  • Capacity Planning        │       │
│  │                             │     │                             │       │
│  │  Build streaming apps       │     │  Run production clusters    │       │
│  │                             │     │                             │       │
│  └─────────────────────────────┘     └─────────────────────────────┘       │
│                                                                             │
│    [📘 Developer Path]                 [📗 Administrator Path]              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Developer learning path

**[📘 Start the Developer Path →](./learning-paths/developer-path.md)**

*Best for: Software engineers building applications that produce or consume Kafka messages.*

| Week | Focus | Key Skills |
|------|-------|------------|
| 1 | Foundations | Architecture, Docker setup, CLI basics |
| 2 | Core Development | Producer/Consumer APIs, error handling |
| 3 | Data Integration | Schema Registry, Kafka Connect, serialization |
| 4 | Stream Processing | Kafka Streams, ksqlDB, testing |

**You'll build:**
- Real-time messaging application
- Schema-validated data pipeline
- Stream processing application

---

### Administrator learning path

**[📗 Start the Administrator Path →](./learning-paths/administrator-path.md)**

*Best for: DevOps engineers, platform engineers, and SREs managing Kafka infrastructure.*

| Week | Focus | Key Skills |
|------|-------|------------|
| 1 | Architecture | Cluster design, KRaft mode, sizing |
| 2 | Security | TLS encryption, SASL authentication, ACLs |
| 3 | Monitoring | JMX metrics, Prometheus, alerting |
| 4 | Operations | Upgrades, disaster recovery, troubleshooting |

**You'll build:**
- Secure multi-broker cluster
- Monitoring and alerting stack
- Disaster recovery procedures

---

## Alternative learning paths

### Complete course (beginner to advanced)

*Best for: Users who want comprehensive coverage of all topics.*

```
Week 1-2     Week 3-4       Week 5-6        Week 7-8        Week 9-10
┌───────┐   ┌───────────┐   ┌───────────┐   ┌───────────┐   ┌───────────┐
│Module │   │  Module   │   │  Module   │   │  Module   │   │  Module   │
│   1   │──►│    2      │──►│    3      │──►│    4      │──►│    5      │
│Found. │   │Core Conc. │   │Intermedia.│   │ Advanced  │   │ Capstone  │
└───────┘   └───────────┘   └───────────┘   └───────────┘   └───────────┘
```

### Fast track (experienced developers)

*Best for: Developers familiar with messaging systems who need to learn Kafka quickly.*

| Day | Focus | Modules |
|-----|-------|---------|
| 1 | Architecture & Setup | Module 1 (skim), Project 1 |
| 2 | Core Messaging | Module 2, Project 2 |
| 3 | Data Pipelines | Module 3, Project 3 |
| 4 | Stream Processing | Module 4 (13-14) |
| 5 | Production Readiness | Module 4 (15-17), Project 4 |

## Module 1: Foundations

*Focus: Understanding Kafka architecture and getting hands-on with your first cluster.*

* **[01 Introduction to Kafka](./module_1_foundations/01_introduction.md)**
* **[02 Architecture deep dive](./module_1_foundations/02_architecture.md)**
* **[03 Environment setup](./module_1_foundations/03_setup_environment.md)**
* **[04 Your first Kafka cluster](./module_1_foundations/04_first_cluster.md)**

**[Exercises](./module_1_foundations/exercises/)** | **[Quiz](./module_1_foundations/quiz_module_1.md)**

**[Project 1: Kafka CLI Tool](./module_1_foundations/project_1_cli_tool.md)**

## Module 2: Core concepts

*Focus: Mastering the fundamental building blocks of Kafka.*

* **[05 Topics and partitions](./module_2_core_concepts/05_topics_partitions.md)**
* **[06 Producers](./module_2_core_concepts/06_producers.md)**
* **[07 Consumers](./module_2_core_concepts/07_consumers.md)**
* **[08 Consumer groups](./module_2_core_concepts/08_consumer_groups.md)**

**[Exercises](./module_2_core_concepts/exercises/)** | **[Quiz](./module_2_core_concepts/quiz_module_2.md)**

**[Project 2: Real-time Messaging System](./module_2_core_concepts/project_2_messaging.md)**

## Module 3: Intermediate

*Focus: Building robust data pipelines and ensuring data quality.*

* **[09 Kafka Connect](./module_3_intermediate/09_kafka_connect.md)**
* **[10 Schema Registry](./module_3_intermediate/10_schema_registry.md)**
* **[11 Serialization formats](./module_3_intermediate/11_serialization.md)**
* **[12 Exactly-once semantics](./module_3_intermediate/12_exactly_once.md)**

**[Exercises](./module_3_intermediate/exercises/)** | **[Quiz](./module_3_intermediate/quiz_module_3.md)**

**[Project 3: Database Change Data Capture Pipeline](./module_3_intermediate/project_3_pipeline.md)**

## Module 4: Advanced

*Focus: Stream processing, security, and production operations.*

* **[13 Kafka Streams](./module_4_advanced/13_kafka_streams.md)**
* **[14 ksqlDB](./module_4_advanced/14_ksqldb.md)**
* **[15 Security](./module_4_advanced/15_security.md)**
* **[16 Monitoring and observability](./module_4_advanced/16_monitoring.md)**
* **[17 Production operations](./module_4_advanced/17_production_ops.md)**

**[Exercises](./module_4_advanced/exercises/)** | **[Quiz](./module_4_advanced/quiz_module_4.md)**

**[Project 4: Production-Ready Kafka Cluster](./module_4_advanced/project_4_production.md)**

## Module 5: Capstone project

**[Project 5: Event-Driven Order Processing System](./module_5_project/project_5_capstone.md)**

Build a complete e-commerce order processing system using:
- Kafka for event streaming
- Kafka Connect for database integration
- Kafka Streams for real-time processing
- Schema Registry for data governance
- Full security and monitoring

## Technology stack

| Component | Version | Purpose |
|-----------|---------|---------|
| Apache Kafka | 3.7+ | Event streaming platform |
| Confluent Platform | 7.6+ | Enterprise Kafka distribution |
| Docker/Podman | Latest | Container runtime |
| Python | 3.9+ | Client applications |
| Java | 17+ | Kafka Streams applications |
| ksqlDB | Latest | SQL-based stream processing |

## Prerequisites by module

| Module | Prerequisites |
|--------|--------------|
| 1 | Docker installed, basic command line |
| 2 | Module 1, basic programming knowledge |
| 3 | Module 2, familiarity with databases |
| 4 | Module 3, Java basics (for Streams) |
| 5 | All previous modules |

## Troubleshooting and help

- See the [Troubleshooting Guide](./troubleshooting.md) for common issues
- Check container logs: `docker logs kafka`
- Validate environment: `./scripts/validate_environment.sh`

## External resources

- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Confluent Developer Portal](https://developer.confluent.io/)
- [Kafka Streams 101](https://developer.confluent.io/courses/kafka-streams/get-started/)
- [Confluent Training](https://www.confluent.io/training/)

---

[↑ Back to Top](#apache-kafka-engineering-course)
