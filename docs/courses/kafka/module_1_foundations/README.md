# Module 1: Kafka Foundations

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Module](https://img.shields.io/badge/Module-1_Foundations-blue)

## Module overview

This module introduces you to Apache Kafka - what it is, why it's used, and how it works. You'll set up a local Kafka cluster and gain hands-on experience with core CLI tools.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        MODULE 1: FOUNDATIONS                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐ │
│  │ 01           │   │ 02           │   │ 03           │   │ 04           │ │
│  │ Introduction │──►│ Architecture │──►│ Environment  │──►│ First        │ │
│  │              │   │              │   │ Setup        │   │ Cluster      │ │
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

1. Explain what Apache Kafka is and why organizations use it
2. Describe Kafka's core architecture (brokers, topics, partitions, replication)
3. Set up a local Kafka cluster using Docker
4. Use Kafka CLI tools to create topics, produce messages, and consume messages
5. Understand the basics of consumer groups and partitioning

## Lessons

| # | Lesson | Description |
|---|--------|-------------|
| 01 | [Introduction to Kafka](./01_introduction.md) | What Kafka is, why use it, real-world use cases |
| 02 | [Architecture Deep Dive](./02_architecture.md) | Brokers, topics, partitions, replication, ZooKeeper/KRaft |
| 03 | [Environment Setup](./03_setup_environment.md) | Docker setup, configuration, troubleshooting |
| 04 | [Your First Cluster](./04_first_cluster.md) | Hands-on CLI tools, producing, consuming, consumer groups |

## Assessment

| Resource | Description |
|----------|-------------|
| [Exercises](./exercises/) | 10 hands-on exercises to reinforce concepts |
| [Quiz](./quiz_module_1.md) | 15-question assessment (80% to pass) |
| [Project 1](./project_1_cli_tool.md) | Build a Kafka CLI management tool |

## Prerequisites

- Docker installed and running
- Basic command line knowledge
- 4GB+ available RAM
- 5GB+ available disk space

## Time estimate

| Activity | Duration |
|----------|----------|
| Lessons | 2-3 hours |
| Exercises | 1-2 hours |
| Quiz | 20 minutes |
| Project | 2-3 hours |
| **Total** | **5-8 hours** |

## Quick start

```bash
# 1. Navigate to course directory
cd ~/kafka-tutorial/docker

# 2. Start Kafka
docker compose up -d

# 3. Verify Kafka is running
docker exec -it kafka kafka-topics --bootstrap-server localhost:9092 --list

# 4. Start learning!
```

## Key concepts covered

- Event streaming vs message queuing
- Distributed architecture
- Topics and partitions
- Producers and consumers
- Consumer groups
- Offsets and message ordering
- KRaft mode

## Next module

After completing Module 1, proceed to:

**[Module 2: Core Concepts →](../module_2_core_concepts/README.md)**

---

[↑ Back to Course Index](../README.md)
