# RabbitMQ Course Overview

**[← Back to Course Index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-RabbitMQ-orange)

> [!IMPORTANT]
> **Related Docs:** [Quick Reference](./quick_reference.md) | [Glossary](./glossary.md)

## Course description

This comprehensive course teaches message-driven architecture using RabbitMQ. You learn to design, implement, and operate reliable messaging systems that power modern distributed applications.

## Learning objectives

By completing this course, you will be able to:

1. **Explain messaging fundamentals** including producers, consumers, queues, and exchanges
2. **Set up RabbitMQ** using Docker for development and clusters for production
3. **Implement AMQP concepts** including exchanges (direct, topic, fanout, headers), queues, and bindings
4. **Build messaging patterns** such as work queues, publish/subscribe, routing, and RPC
5. **Handle failures gracefully** using acknowledgments, dead letter exchanges, and retry strategies
6. **Configure production systems** with clustering, high availability, monitoring, and security
7. **Design distributed systems** that are scalable, reliable, and maintainable

## Target audience

- **Application developers** building microservices or distributed systems
- **DevOps engineers** deploying and managing message infrastructure
- **Architects** designing event-driven architectures
- **Database administrators** expanding into messaging technologies
- **Anyone** wanting to understand modern async communication patterns

## Prerequisites

- **Basic Python knowledge** - Variables, functions, classes
- **Command-line familiarity** - Navigating directories, running commands
- **Docker basics** - Running containers (covered in Module 1 if needed)
- **Networking concepts** - Understanding ports, hosts, TCP connections (helpful)

**No prior RabbitMQ or messaging experience required!**

## Course structure

| Module | Title | Duration | Topics |
|:---|:---|:---|:---|
| **1** | [Foundations](./module_1_foundations/01_introduction.md) | 4-6 hours | Messaging concepts, installation, Hello World, Python Pika |
| **2** | [Core Concepts](./module_2_core_concepts/01_amqp_model.md) | 4-6 hours | AMQP model, exchanges, queues, bindings, message properties |
| **3** | [Messaging Patterns](./module_3_messaging_patterns/01_work_queues.md) | 6-8 hours | Work queues, pub/sub, routing, topics, RPC |
| **4** | [Production](./module_4_production/01_reliability.md) | 4-6 hours | Reliability, DLX, clustering, monitoring, security |
| **5** | [Capstone](./module_5_project/capstone_order_system.md) | 8-12 hours | Complete order processing system |

**Total estimated time:** 26-38 hours (self-paced)

## Module details

### Module 1: Foundations

*What you learn:*
- What message brokers are and why they matter
- The role of RabbitMQ in modern architectures
- Setting up RabbitMQ with Docker
- Writing your first producer and consumer
- Using the Python Pika library

*Project:* Build a simple chat system with multiple participants

---

### Module 2: Core concepts

*What you learn:*
- The AMQP 0-9-1 protocol model
- Exchange types: direct, topic, fanout, headers
- Queue properties and behaviors
- Bindings and routing keys
- Message properties and headers

*Project:* Build a log aggregation system with filtering

---

### Module 3: Messaging patterns

*What you learn:*
- Work queues for task distribution
- Publish/Subscribe for broadcasting
- Routing for selective delivery
- Topic exchanges for flexible routing
- RPC for request/response patterns

*Project:* Build a distributed task processor

---

### Module 4: Production

*What you learn:*
- Message acknowledgments and persistence
- Dead letter exchanges for error handling
- Clustering and high availability
- Monitoring with the management UI and Prometheus
- Security: authentication, authorization, TLS

*Project:* Build a resilient system with automatic recovery

---

### Module 5: Capstone project

*What you build:*
A complete order processing system featuring:
- Order submission and validation
- Inventory checking with retry logic
- Payment processing with timeout handling
- Notification services (email, SMS, push)
- Dead letter handling for failed orders
- Monitoring dashboard

## Technology stack

- **Message Broker:** RabbitMQ 4.x
- **Protocol:** AMQP 0-9-1
- **Client Library:** Python Pika 1.3+
- **Containers:** Docker / Podman
- **Monitoring:** RabbitMQ Management Plugin, Prometheus (optional)
- **Development OS:** Linux, macOS, or Windows with WSL2

## Assessment structure

Each module includes:

| Component | Description |
|:---|:---|
| **Exercises** | Hands-on coding tasks after each lesson |
| **Quiz** | 15 questions testing conceptual understanding |
| **Project** | Practical application building a working system |

**Passing criteria:**
- Quiz: 80% (12/15 correct)
- Project: Working implementation that meets requirements

## Quick start

```bash
# 1. Clone the repository (if applicable)
cd docs/courses/rabbitmq

# 2. Start RabbitMQ with Docker
docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:management

# 3. Access Management UI
# Open http://localhost:15672
# Login: guest / guest

# 4. Install Python client
pip install pika

# 5. Run Hello World example
python module_1_foundations/examples/hello_world_send.py
python module_1_foundations/examples/hello_world_receive.py
```

## Support resources

- **Troubleshooting:** Each module has a troubleshooting section
- **Examples:** Working code in each module's `examples/` directory
- **Community:**
  - [RabbitMQ Mailing List](https://groups.google.com/g/rabbitmq-users)
  - [Stack Overflow - rabbitmq tag](https://stackoverflow.com/questions/tagged/rabbitmq)

---

[↑ Back to Top](#rabbitmq-course-overview)
