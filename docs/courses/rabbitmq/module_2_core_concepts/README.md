# Module 2: Core Concepts

**[← Back to Course Index](../README.md)**

*Focus: Deep dive into the AMQP model - exchanges, queues, bindings, and message routing.*

## Lessons

| # | Lesson | Topics |
|:---|:---|:---|
| 1 | [The AMQP Model](./01_amqp_model.md) | Protocol overview, message flow, entities |
| 2 | [Exchanges](./02_exchanges.md) | Exchange types, declaration, default exchange |
| 3 | [Queues](./03_queues.md) | Queue properties, durability, types |
| 4 | [Bindings](./04_bindings.md) | Binding rules, routing keys, patterns |
| 5 | [Message Properties](./05_message_properties.md) | Headers, persistence, TTL, priority |

## Exercises

Practice what you've learned:

- **[Exercise 1: Exchange Types](./exercises/ex_01_exchanges.md)** - Working with different exchange types
- **[Exercise 2: Queue Configuration](./exercises/ex_02_queues.md)** - Queue properties and arguments
- **[Exercise 3: Routing Patterns](./exercises/ex_03_routing.md)** - Binding and routing key patterns

## Assessment

- **[Quiz: Module 2](./quiz_module_2.md)** - Test your understanding (15 questions)

## Project

- **[Project 2: Log Aggregation System](./project_2_log_aggregator.md)** - Build a centralized logging system with filtering

## Learning objectives

By completing this module, you will be able to:

1. **Explain** the AMQP 0-9-1 message flow from producer to consumer
2. **Choose** the appropriate exchange type for different scenarios
3. **Configure** queue properties for durability, TTL, and limits
4. **Design** binding patterns for flexible message routing
5. **Use** message properties for metadata and behavior control

## Prerequisites

- Completed Module 1: Foundations
- RabbitMQ running locally
- Familiarity with Python Pika

## Key concepts summary

| Concept | Purpose | Example |
|:---|:---|:---|
| **Direct Exchange** | Exact routing key match | Task queues |
| **Topic Exchange** | Pattern-based routing | Log filtering |
| **Fanout Exchange** | Broadcast to all | Notifications |
| **Durable Queue** | Survives restarts | Important data |
| **Binding Key** | Route matching rule | `order.created` |

## Architecture diagram

```
                        ┌─────────────────────────────────────────────────────┐
                        │                    RabbitMQ Broker                   │
                        │                                                      │
Producer ──────────────▶│  ┌──────────┐    Bindings    ┌──────────┐          │
(publishes to exchange) │  │ Exchange │ ──────────────▶│  Queue   │──────────│──▶ Consumer
                        │  │          │    (rules)     │          │          │
                        │  └──────────┘                └──────────┘          │
                        │       │                           ▲                 │
                        │       │        ┌─────────────────┘                 │
                        │       │        │                                    │
                        │       ▼        │                                    │
                        │  ┌──────────┐  │                                    │
                        │  │  Queue   │──┘                                    │──▶ Consumer
                        │  └──────────┘                                       │
                        │                                                      │
                        └─────────────────────────────────────────────────────┘
```

---

[← Back to Course Index](../README.md) | [Start Module 2 →](./01_amqp_model.md)
