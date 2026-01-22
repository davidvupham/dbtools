# Module 1: Foundations

**[← Back to Course Index](../README.md)**

*Focus: Understanding messaging concepts, setting up RabbitMQ, and writing your first producer/consumer.*

## Lessons

| # | Lesson | Topics |
|:---|:---|:---|
| 1 | [Introduction to Message Brokers](./01_introduction.md) | What is a message broker, why RabbitMQ, AMQP overview |
| 2 | [Messaging Concepts](./02_messaging_concepts.md) | Producers, consumers, messages, connections, channels, ACKs |
| 3 | [Installing RabbitMQ](./03_installation.md) | Docker setup, Management UI, Python Pika |
| 4 | [Hello World](./04_hello_world.md) | First producer and consumer, interactive testing |
| 5 | [Python Pika Deep Dive](./05_python_pika.md) | Connection options, properties, error handling, patterns |

## Exercises

Practice what you've learned:

- **[Exercise 1: Connection Basics](./exercises/ex_01_connections.md)** - Connection parameters and channels
- **[Exercise 2: Message Properties](./exercises/ex_02_properties.md)** - Working with message metadata
- **[Exercise 3: Producer Patterns](./exercises/ex_03_producer.md)** - Different publishing approaches
- **[Exercise 4: Consumer Patterns](./exercises/ex_04_consumer.md)** - Acknowledgments and error handling

## Assessment

- **[Quiz: Module 1](./quiz_module_1.md)** - Test your understanding (15 questions)

## Project

- **[Project 1: Simple Chat System](./project_1_simple_chat.md)** - Build a basic chat application with multiple participants

## Learning objectives

By completing this module, you will be able to:

1. **Explain** what message brokers are and why they're used
2. **Describe** the roles of producers, consumers, exchanges, and queues
3. **Set up** RabbitMQ using Docker
4. **Write** basic producers and consumers in Python
5. **Use** the Pika library for connection management and message handling
6. **Navigate** the RabbitMQ Management UI

## Prerequisites

- Python 3.8+
- Docker or Podman
- Basic command-line skills
- Text editor or IDE

## Quick start

```bash
# 1. Start RabbitMQ
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:management

# 2. Install Pika
pip install pika

# 3. Open Management UI
# http://localhost:15672 (guest/guest)

# 4. Run Hello World
python examples/send.py
python examples/receive.py
```

## Key concepts summary

| Concept | Definition |
|:---|:---|
| **Producer** | Application that sends messages |
| **Consumer** | Application that receives messages |
| **Queue** | Buffer that stores messages |
| **Channel** | Virtual connection within a TCP connection |
| **ACK** | Acknowledgment that message was processed |

---

[← Back to Course Index](../README.md) | [Start Module 1 →](./01_introduction.md)
