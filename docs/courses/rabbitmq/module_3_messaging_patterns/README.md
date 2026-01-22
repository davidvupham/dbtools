# Module 3: Messaging Patterns

**[← Back to Course Index](../README.md)**

*Focus: Implementing common messaging patterns - work queues, pub/sub, routing, topics, and RPC.*

## Lessons

| # | Lesson | Topics |
|:---|:---|:---|
| 1 | [Work Queues](./01_work_queues.md) | Task distribution, fair dispatch, acknowledgments |
| 2 | [Publish/Subscribe](./02_publish_subscribe.md) | Broadcasting, fanout exchanges, temporary queues |
| 3 | [Routing](./03_routing.md) | Direct exchanges, selective delivery |
| 4 | [Topics](./04_topics.md) | Pattern matching, flexible routing |
| 5 | [RPC](./05_rpc.md) | Request/response, correlation, timeouts |

## Exercises

Practice what you've learned:

- **[Exercise 1: Work Queue Implementation](./exercises/ex_01_work_queues.md)** - Build a task processor
- **[Exercise 2: Event Broadcasting](./exercises/ex_02_pubsub.md)** - Implement pub/sub system
- **[Exercise 3: Log Router](./exercises/ex_03_routing.md)** - Route logs by severity

## Assessment

- **[Quiz: Module 3](./quiz_module_3.md)** - Test your understanding (15 questions)

## Project

- **[Project 3: Distributed Task Processor](./project_3_task_processor.md)** - Build a system that distributes image processing tasks

## Learning objectives

By completing this module, you will be able to:

1. **Implement work queues** for distributing tasks among workers
2. **Build pub/sub systems** for broadcasting events
3. **Use direct routing** for selective message delivery
4. **Apply topic patterns** for flexible filtering
5. **Create RPC systems** with proper correlation and timeouts

## Prerequisites

- Completed Module 2: Core Concepts
- Understanding of exchanges, queues, and bindings
- Familiarity with Python Pika

## Pattern comparison

| Pattern | Exchange Type | Use Case | Message Flow |
|:---|:---|:---|:---|
| **Work Queues** | Direct (default) | Task distribution | 1 producer → 1 of N consumers |
| **Pub/Sub** | Fanout | Broadcasting | 1 producer → all consumers |
| **Routing** | Direct | Selective delivery | 1 producer → selected consumers |
| **Topics** | Topic | Flexible filtering | 1 producer → pattern-matched consumers |
| **RPC** | Direct | Request/response | 1 producer ↔ 1 consumer |

## Pattern decision tree

```
Need to distribute work among workers?
├── Yes → Work Queues (01_work_queues.md)
│
Need all subscribers to receive every message?
├── Yes → Pub/Sub (02_publish_subscribe.md)
│
Need to route to specific queues by exact category?
├── Yes → Routing (03_routing.md)
│
Need flexible pattern-based routing?
├── Yes → Topics (04_topics.md)
│
Need request/response semantics?
├── Yes → RPC (05_rpc.md)
```

---

[← Back to Course Index](../README.md) | [Start Module 3 →](./01_work_queues.md)
