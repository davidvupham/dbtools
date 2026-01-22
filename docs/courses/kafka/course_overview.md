# Kafka Course Overview

**[← Back to Course Index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Apache_Kafka-blue)

> [!IMPORTANT]
> **Related Docs:** [Quick Reference](./quick_reference.md) | [Glossary](./glossary.md) | [Troubleshooting](./troubleshooting.md)

## Table of contents

- [Course description](#course-description)
- [Learning objectives](#learning-objectives)
- [Target audience](#target-audience)
- [Prerequisites](#prerequisites)
- [Course structure](#course-structure)
- [Assessment criteria](#assessment-criteria)
- [Quick start](#quick-start)
- [Technology stack](#technology-stack)

## Course description

This comprehensive course teaches distributed event streaming using Apache Kafka. You learn to build scalable, fault-tolerant data pipelines, implement real-time stream processing, and operate Kafka clusters in production environments.

Kafka has become the de facto standard for event streaming, used by companies like Netflix (processing trillions of messages per day), Uber (300+ microservices), LinkedIn (7 trillion messages per day), and over 80% of Fortune 100 companies.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        WHY LEARN KAFKA?                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │   High      │    │   Fault     │    │   Real-     │    │   Event     │  │
│  │ Throughput  │    │  Tolerant   │    │   Time      │    │  Sourcing   │  │
│  │             │    │             │    │             │    │             │  │
│  │ Millions of │    │ Built-in    │    │ Sub-second  │    │ Complete    │  │
│  │ msgs/sec    │    │ replication │    │ latency     │    │ audit trail │  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

[↑ Back to Table of Contents](#table-of-contents)

## Learning objectives

By completing this course, you will be able to:

### Module 1: Foundations
1. **Explain Kafka architecture** and the role of brokers, topics, partitions, and ZooKeeper/KRaft
2. **Set up a local Kafka cluster** using Docker for development and testing
3. **Use Kafka CLI tools** to create topics, produce messages, and consume messages

### Module 2: Core concepts
4. **Design topic schemas** with appropriate partitioning strategies
5. **Build producer applications** with proper error handling and delivery guarantees
6. **Implement consumer applications** with offset management and rebalancing strategies
7. **Configure consumer groups** for parallel processing and fault tolerance

### Module 3: Intermediate
8. **Build data pipelines** using Kafka Connect with source and sink connectors
9. **Implement schema evolution** using Schema Registry and Avro/Protobuf
10. **Configure exactly-once semantics** for reliable message processing

### Module 4: Advanced
11. **Develop stream processing applications** using Kafka Streams
12. **Write real-time queries** using ksqlDB
13. **Secure Kafka clusters** with SSL/TLS, SASL, and ACLs
14. **Monitor Kafka** using metrics, logging, and alerting
15. **Operate Kafka in production** with proper capacity planning and maintenance

### Module 5: Capstone
16. **Design and implement** a complete event-driven system integrating all learned concepts

[↑ Back to Table of Contents](#table-of-contents)

## Target audience

This course is designed for:

| Role | What You Learn |
|------|----------------|
| **Backend Developers** | Building event-driven microservices with Kafka |
| **Data Engineers** | Creating real-time data pipelines and ETL processes |
| **DevOps Engineers** | Deploying, securing, and monitoring Kafka clusters |
| **Solutions Architects** | Designing scalable event streaming architectures |
| **DBAs** | Implementing CDC and database replication with Kafka |

[↑ Back to Table of Contents](#table-of-contents)

## Prerequisites

### Required knowledge

- **Command line basics**: Navigate directories, run commands, edit files
- **Basic programming**: Variables, functions, loops (Python or Java preferred)
- **Docker fundamentals**: Run containers, use docker-compose
- **Networking basics**: Understand ports, hostnames, TCP/IP

### Required software

```bash
# Verify prerequisites
docker --version        # Docker 20.10+
docker-compose --version # Docker Compose 2.0+
python --version        # Python 3.9+ (for exercises)
java --version          # Java 17+ (for Kafka Streams, optional for Modules 1-3)
```

### Optional but helpful

- Experience with messaging systems (RabbitMQ, ActiveMQ)
- Familiarity with microservices architecture
- Basic SQL knowledge (for ksqlDB)

[↑ Back to Table of Contents](#table-of-contents)

## Course structure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           COURSE TIMELINE                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Module 1         Module 2         Module 3         Module 4      Module 5  │
│  ┌───────┐        ┌───────┐        ┌───────┐        ┌───────┐     ┌──────┐ │
│  │ Found │        │ Core  │        │ Inter │        │  Adv  │     │Capst.│ │
│  │ations │        │Concept│        │mediate│        │ anced │     │      │ │
│  └───┬───┘        └───┬───┘        └───┬───┘        └───┬───┘     └──┬───┘ │
│      │                │                │                │            │      │
│  4 lessons        4 lessons        4 lessons        5 lessons    Project   │
│  10 exercises     12 exercises     10 exercises     15 exercises           │
│  1 quiz           1 quiz           1 quiz           1 quiz                 │
│  1 project        1 project        1 project        1 project              │
│                                                                             │
│  Beginner ──────────────────────────────────────────────────────► Advanced │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

| Module | Topics | Lessons | Exercises |
|--------|--------|---------|-----------|
| **1. Foundations** | Architecture, Setup, First Cluster | 4 | 10 |
| **2. Core Concepts** | Topics, Producers, Consumers, Groups | 4 | 12 |
| **3. Intermediate** | Connect, Schema Registry, Exactly-Once | 4 | 10 |
| **4. Advanced** | Streams, ksqlDB, Security, Monitoring | 5 | 15 |
| **5. Capstone** | Complete Event-Driven System | - | 1 Project |

### Time estimates

| Learning Style | Total Duration |
|----------------|----------------|
| **Self-paced (casual)** | 8-10 weeks |
| **Dedicated study** | 4-6 weeks |
| **Fast track** | 1-2 weeks |

[↑ Back to Table of Contents](#table-of-contents)

## Assessment criteria

### Quiz requirements

- **15 questions** per module quiz
- **80% passing score** (12/15 correct)
- Mix of conceptual and practical questions
- Retakes allowed after review

### Project requirements

Each project must demonstrate:

| Criteria | Description |
|----------|-------------|
| **Functionality** | All required features work correctly |
| **Error Handling** | Graceful handling of failures |
| **Code Quality** | Clean, readable, well-documented code |
| **Best Practices** | Following Kafka patterns and conventions |

### Skill levels

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SKILL PROGRESSION                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Awareness      Understanding      Application       Analysis       Expert  │
│      │               │                 │                │             │     │
│  ────┼───────────────┼─────────────────┼────────────────┼─────────────┼──── │
│      │               │                 │                │             │     │
│  Module 1        Module 2          Module 3         Module 4     Capstone  │
│                                                                             │
│  "I know what   "I understand    "I can build     "I can design  "I can    │
│   Kafka is"      how it works"    with Kafka"      solutions"     lead"    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

[↑ Back to Table of Contents](#table-of-contents)

## Quick start

```bash
# 1. Clone the repository and navigate to the course
cd /path/to/dbtools/docs/courses/kafka

# 2. Start the Kafka environment
docker-compose -f docker/docker-compose.yml up -d

# 3. Verify Kafka is running
docker exec -it kafka kafka-topics.sh --bootstrap-server localhost:9092 --list

# 4. Create your first topic
docker exec -it kafka kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create \
  --topic my-first-topic \
  --partitions 3 \
  --replication-factor 1

# 5. Produce a message
echo "Hello, Kafka!" | docker exec -i kafka kafka-console-producer.sh \
  --bootstrap-server localhost:9092 \
  --topic my-first-topic

# 6. Consume the message
docker exec -it kafka kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic my-first-topic \
  --from-beginning
```

[↑ Back to Table of Contents](#table-of-contents)

## Technology stack

| Component | Version | Purpose |
|-----------|---------|---------|
| **Apache Kafka** | 3.7+ | Core event streaming platform |
| **Confluent Platform** | 7.6+ | Enterprise distribution with extras |
| **KRaft** | Included | ZooKeeper-free mode (Kafka 3.3+) |
| **Schema Registry** | 7.6+ | Schema management and evolution |
| **Kafka Connect** | 3.7+ | Data integration framework |
| **ksqlDB** | 0.29+ | SQL-based stream processing |
| **Docker** | 20.10+ | Container runtime |
| **Python** | 3.9+ | Client applications (kafka-python, confluent-kafka) |
| **Java** | 17+ | Kafka Streams applications |

### Architecture overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         KAFKA ECOSYSTEM                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐                                      ┌─────────────┐      │
│  │  Producers  │                                      │  Consumers  │      │
│  │  (Apps/DBs) │                                      │  (Apps/DBs) │      │
│  └──────┬──────┘                                      └──────▲──────┘      │
│         │                                                    │              │
│         │    ┌─────────────────────────────────────────┐    │              │
│         │    │           KAFKA CLUSTER                 │    │              │
│         │    │  ┌─────────┐ ┌─────────┐ ┌─────────┐   │    │              │
│         └───►│  │ Broker  │ │ Broker  │ │ Broker  │   │────┘              │
│              │  │    1    │ │    2    │ │    3    │   │                   │
│              │  └─────────┘ └─────────┘ └─────────┘   │                   │
│              │         Topics & Partitions            │                   │
│              └─────────────────────────────────────────┘                   │
│                              │                                             │
│              ┌───────────────┼───────────────┐                             │
│              │               │               │                             │
│       ┌──────▼─────┐  ┌──────▼─────┐  ┌─────▼──────┐                      │
│       │   Schema   │  │   Kafka    │  │   ksqlDB   │                      │
│       │  Registry  │  │  Connect   │  │            │                      │
│       └────────────┘  └────────────┘  └────────────┘                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

[↑ Back to Table of Contents](#table-of-contents)

---

**Next:** [Module 1: Introduction to Kafka →](./module_1_foundations/01_introduction.md)
