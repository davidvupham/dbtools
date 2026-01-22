# RabbitMQ Message Broker Course

**[← Back to Courses Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-RabbitMQ-orange)

> [!IMPORTANT]
> **Related Docs:** [Course Overview](./course_overview.md) | [Quick Reference](./quick_reference.md) | [Glossary](./glossary.md)

## Introduction

This is a **comprehensive course** on message-driven architecture using RabbitMQ. It takes you from understanding basic messaging concepts to building production-ready distributed systems.

### Core Philosophy: Understand First, Then Build

We believe you cannot effectively build distributed systems without understanding the underlying messaging patterns. Therefore, this course is structured progressively:

1. **Phase 1: Foundations (Module 1)**
   - Understand what message brokers are and why they exist
   - Set up a local RabbitMQ environment with Docker
   - Write your first producer and consumer

2. **Phase 2: Core Concepts (Module 2)**
   - Master the AMQP protocol model
   - Learn exchanges, queues, and bindings
   - Understand message routing in depth

3. **Phase 3: Messaging Patterns (Module 3)**
   - Implement work queues, pub/sub, routing, and RPC
   - Handle message acknowledgments and persistence
   - Build reliable message processing systems

4. **Phase 4: Production (Module 4)**
   - Configure clustering and high availability
   - Implement dead letter exchanges and error handling
   - Monitor and tune RabbitMQ performance

5. **Phase 5: Capstone Project (Module 5)**
   - Build a complete order processing system
   - Apply all concepts in a real-world scenario

## Directory structure

```text
docs/courses/rabbitmq/
├── README.md                    <-- You are here (Navigation Hub)
├── course_overview.md           <-- Learning objectives, prerequisites
├── quick_reference.md           <-- Common commands cheat sheet
├── glossary.md                  <-- Terminology definitions
├── module_1_foundations/        <-- Getting Started
│   ├── 01_introduction.md
│   ├── 02_messaging_concepts.md
│   ├── 03_installation.md
│   ├── 04_hello_world.md
│   ├── 05_python_pika.md
│   ├── exercises/
│   ├── quiz_module_1.md
│   └── project_1_simple_chat.md
├── module_2_core_concepts/      <-- AMQP Model Deep Dive
│   ├── 01_amqp_model.md
│   ├── 02_exchanges.md
│   ├── 03_queues.md
│   ├── 04_bindings.md
│   ├── 05_message_properties.md
│   ├── exercises/
│   ├── quiz_module_2.md
│   └── project_2_log_aggregator.md
├── module_3_messaging_patterns/ <-- Implementation Patterns
│   ├── 01_work_queues.md
│   ├── 02_publish_subscribe.md
│   ├── 03_routing.md
│   ├── 04_topics.md
│   ├── 05_rpc.md
│   ├── exercises/
│   ├── quiz_module_3.md
│   └── project_3_task_processor.md
├── module_4_production/         <-- Production Readiness
│   ├── 01_reliability.md
│   ├── 02_dead_letter_exchanges.md
│   ├── 03_clustering.md
│   ├── 04_monitoring.md
│   ├── 05_security.md
│   ├── exercises/
│   ├── quiz_module_4.md
│   └── project_4_resilient_system.md
├── module_5_project/            <-- Capstone
│   └── capstone_order_system.md
├── docker/                      <-- Docker Compose files
│   └── docker-compose.yml
├── scripts/                     <-- Helper scripts
│   └── setup_rabbitmq.sh
└── assets/                      <-- Diagrams and images
    └── diagrams/
```

## Quick resources

- **[Course Overview](./course_overview.md)** - Learning objectives, time estimates, prerequisites
- **[Quick Reference](./quick_reference.md)** - Common commands and patterns cheat sheet
- **[Glossary](./glossary.md)** - Terminology definitions

## Learning paths

Choose the path that fits your experience level.

### Recommended path (Beginner to Intermediate)

*Best for: Users new to message brokers or those wanting a solid foundation.*

1. **[Module 1: Foundations](./module_1_foundations/01_introduction.md)**
   - *Goal*: Understand messaging concepts, set up RabbitMQ, write your first producer/consumer.

2. **[Module 2: Core Concepts](./module_2_core_concepts/01_amqp_model.md)**
   - *Goal*: Master the AMQP model with exchanges, queues, and bindings.

3. **[Module 3: Messaging Patterns](./module_3_messaging_patterns/01_work_queues.md)**
   - *Goal*: Implement common messaging patterns (work queues, pub/sub, routing, RPC).

4. **[Module 4: Production](./module_4_production/01_reliability.md)**
   - *Goal*: Learn clustering, monitoring, security, and production best practices.

5. **[Module 5: Capstone Project](./module_5_project/capstone_order_system.md)**
   - *Goal*: Build a complete distributed order processing system.

---

### Fast track (Experienced Users)

*Best for: Developers familiar with messaging who want specific patterns.*

| Topic | Resource |
|:---|:---|
| Exchange types | [Module 2: Exchanges](./module_2_core_concepts/02_exchanges.md) |
| Pub/Sub pattern | [Module 3: Publish/Subscribe](./module_3_messaging_patterns/02_publish_subscribe.md) |
| Dead letter handling | [Module 4: Dead Letter Exchanges](./module_4_production/02_dead_letter_exchanges.md) |
| Production checklist | [Quick Reference](./quick_reference.md#production-checklist) |

---

## Method comparison: Development vs Production

| Feature | Local Docker (Dev) | Production Cluster |
|:---|:---|:---|
| **Setup** | `docker-compose up` | Cluster deployment |
| **Persistence** | Optional | Required (quorum queues) |
| **High Availability** | Single node | 3+ node cluster |
| **Monitoring** | Management UI | Prometheus + Grafana |
| **Security** | Default credentials | TLS + LDAP/OAuth |
| **Best For** | Development, Learning | Production workloads |

## Frequently asked questions

### Q: Do I need prior messaging experience?

**A:** No. This course starts from the fundamentals and progressively builds up to advanced topics. Basic Python and command-line knowledge is helpful.

### Q: Why Python for the examples?

**A:** Python with the Pika library provides clear, readable examples that focus on concepts rather than language complexity. The patterns translate easily to Java, Node.js, Go, or any AMQP client.

### Q: How long does the course take?

**A:** Self-paced. Module 1-2 can be completed in a weekend. The full course with projects typically takes 2-4 weeks of part-time study.

### Q: Why use Docker for RabbitMQ?

**A:** Docker provides a clean, reproducible environment. You can experiment freely without affecting your system, and cleanup is as simple as removing the container.

## Help and troubleshooting

- **Connection Issues**: Check [Module 1: Installation](./module_1_foundations/03_installation.md#troubleshooting)
- **Pattern Selection**: See the [Pattern Selection Guide](./module_3_messaging_patterns/01_work_queues.md#when-to-use)
- **Community Resources**:
  - [RabbitMQ Documentation](https://www.rabbitmq.com/docs)
  - [RabbitMQ GitHub Discussions](https://github.com/rabbitmq/rabbitmq-server/discussions)
  - [CloudAMQP Blog](https://www.cloudamqp.com/blog/)

---

[↑ Back to Table of Contents](#directory-structure)
