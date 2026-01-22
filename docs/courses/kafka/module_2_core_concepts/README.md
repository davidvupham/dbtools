# Module 2: Core Concepts

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Module](https://img.shields.io/badge/Module-2_Core_Concepts-blue)

## Module overview

This module dives deep into Kafka's fundamental building blocks. You master topics, partitions, producers, consumers, and consumer groups - the core abstractions that power all Kafka applications.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        MODULE 2: CORE CONCEPTS                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐ │
│  │ 05           │   │ 06           │   │ 07           │   │ 08           │ │
│  │ Topics &     │──►│ Producers    │──►│ Consumers    │──►│ Consumer     │ │
│  │ Partitions   │   │              │   │              │   │ Groups       │ │
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

1. Design topics with appropriate partition strategies
2. Configure producers for reliability, throughput, and latency
3. Build consumers with proper offset management
4. Implement consumer groups for parallel processing
5. Handle rebalancing and failure scenarios
6. Tune configurations for your use case

## Lessons

| # | Lesson | Description |
|---|--------|-------------|
| 05 | [Topics and Partitions](./05_topics_partitions.md) | Design patterns, retention, compaction |
| 06 | [Producers](./06_producers.md) | Acknowledgments, batching, idempotence |
| 07 | [Consumers](./07_consumers.md) | Polling, offset commits, rebalancing |
| 08 | [Consumer Groups](./08_consumer_groups.md) | Coordination, assignment strategies |

## Assessment

| Resource | Description |
|----------|-------------|
| [Exercises](./exercises/) | 12 hands-on exercises |
| [Quiz](./quiz_module_2.md) | 15-question assessment (80% to pass) |
| [Project 2](./project_2_messaging.md) | Build a real-time messaging system |

## Prerequisites

- Completed Module 1: Foundations
- Kafka development environment running
- Basic programming knowledge (Python or Java)

## Time estimate

| Activity | Duration |
|----------|----------|
| Lessons | 3-4 hours |
| Exercises | 2-3 hours |
| Quiz | 20 minutes |
| Project | 3-4 hours |
| **Total** | **8-12 hours** |

## Key concepts covered

### Topics and partitions
- Partition design strategies
- Retention policies (time vs size)
- Log compaction
- Partition rebalancing

### Producers
- Acknowledgment levels (acks)
- Batching and compression
- Idempotent producers
- Error handling and retries

### Consumers
- Poll loop architecture
- Offset management
- Auto vs manual commit
- Rebalancing listeners

### Consumer groups
- Group coordinator
- Assignment strategies
- Static membership
- Consumer lag monitoring

## Architecture preview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PRODUCER → KAFKA → CONSUMER                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PRODUCER                      BROKER                      CONSUMER         │
│  ─────────                     ──────                      ────────         │
│                                                                             │
│  ┌─────────┐                 ┌─────────────┐              ┌─────────┐      │
│  │ Batch   │                 │   TOPIC     │              │  Poll   │      │
│  │ Records │                 │             │              │  Loop   │      │
│  └────┬────┘                 │ ┌─────────┐ │              └────┬────┘      │
│       │                      │ │   P0    │ │                   │           │
│       │    ┌──────────┐      │ ├─────────┤ │     ┌─────────┐   │           │
│       └───►│ Serialize│─────►│ │   P1    │ │────►│Deserial.│───┘           │
│            │ Partition│      │ ├─────────┤ │     │ Process │               │
│            └──────────┘      │ │   P2    │ │     └─────────┘               │
│                              │ └─────────┘ │                               │
│  acks=all  ◄─────────────────│             │──────────────► commit         │
│                              └─────────────┘                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Next module

After completing Module 2, proceed to:

**[Module 3: Intermediate →](../module_3_intermediate/README.md)**

---

[↑ Back to Course Index](../README.md)
