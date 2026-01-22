# RabbitMQ Glossary

**[← Back to Course Index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-RabbitMQ-orange)

> [!IMPORTANT]
> **Related Docs:** [Quick Reference](./quick_reference.md) | [Course Overview](./course_overview.md)

## Core concepts

| Term | Definition |
|:---|:---|
| **AMQP** | Advanced Message Queuing Protocol. The wire-level protocol RabbitMQ implements (version 0-9-1). |
| **Message Broker** | Software that translates messages between formal messaging protocols, enabling applications to communicate asynchronously. |
| **Producer** | An application that sends (publishes) messages to RabbitMQ. |
| **Consumer** | An application that receives messages from RabbitMQ queues. |
| **Message** | A unit of data sent through RabbitMQ, consisting of a body (payload) and properties (metadata). |

## Exchanges

| Term | Definition |
|:---|:---|
| **Exchange** | A routing agent that receives messages from producers and routes them to queues based on rules (bindings). |
| **Direct Exchange** | Routes messages to queues where the binding key exactly matches the routing key. |
| **Topic Exchange** | Routes messages using pattern matching with `*` (one word) and `#` (zero or more words). |
| **Fanout Exchange** | Routes messages to all bound queues, ignoring routing keys (broadcast). |
| **Headers Exchange** | Routes messages based on header attributes rather than routing keys. |
| **Default Exchange** | A pre-declared direct exchange with no name. Every queue is automatically bound to it using the queue name as routing key. |

## Queues

| Term | Definition |
|:---|:---|
| **Queue** | A buffer that stores messages waiting to be consumed. Messages are delivered in FIFO order. |
| **Durable Queue** | A queue that survives broker restarts. Declaration persists but messages need `delivery_mode=2`. |
| **Transient Queue** | A queue that is deleted when the broker restarts. |
| **Exclusive Queue** | A queue that can only be used by one connection and is deleted when that connection closes. |
| **Auto-delete Queue** | A queue that is deleted when its last consumer unsubscribes. |
| **Quorum Queue** | A replicated queue type (RabbitMQ 3.8+) designed for data safety across cluster nodes. |
| **Classic Queue** | The original queue implementation, suitable for most use cases. |

## Bindings

| Term | Definition |
|:---|:---|
| **Binding** | A link between an exchange and a queue that defines how messages should be routed. |
| **Routing Key** | A message attribute that the exchange uses to determine how to route the message to queues. |
| **Binding Key** | The routing key pattern specified when creating a binding (what the exchange matches against). |

## Message delivery

| Term | Definition |
|:---|:---|
| **Acknowledgment (ACK)** | A signal from a consumer to RabbitMQ indicating successful message processing. |
| **Negative Acknowledgment (NACK)** | A signal indicating the consumer could not process the message. Can trigger requeue or dead-lettering. |
| **Reject** | Similar to NACK but for a single message. Used to decline a message. |
| **Prefetch Count** | The maximum number of unacknowledged messages a consumer can have at once. Controls flow. |
| **Auto-ACK** | Automatic acknowledgment mode where messages are acknowledged immediately upon delivery (risky). |
| **Manual ACK** | Mode where the application explicitly acknowledges messages after processing (recommended). |

## Message properties

| Term | Definition |
|:---|:---|
| **Delivery Mode** | 1 = transient (non-persistent), 2 = persistent (survives broker restart). |
| **Persistent Message** | A message with `delivery_mode=2` stored to disk for durability. |
| **TTL (Time-To-Live)** | Expiration time for messages. Can be set per-message or per-queue. |
| **Priority** | Message priority level (0-255). Requires priority queue configuration. |
| **Correlation ID** | Application-provided identifier to correlate responses with requests (used in RPC). |
| **Reply-To** | Queue name where responses should be sent (used in RPC pattern). |

## Error handling

| Term | Definition |
|:---|:---|
| **Dead Letter Exchange (DLX)** | An exchange where messages are sent when they cannot be delivered or are rejected. |
| **Dead Letter Queue (DLQ)** | A queue bound to a DLX that collects failed messages for later inspection or retry. |
| **Requeue** | Returning a rejected message back to its original queue for retry. |
| **Message Expiration** | When a message's TTL expires, it may be dead-lettered or discarded. |

## Connections and channels

| Term | Definition |
|:---|:---|
| **Connection** | A TCP connection between a client and RabbitMQ broker. Resource-intensive to create. |
| **Channel** | A virtual connection inside a TCP connection. Lightweight and thread-safe. Multiple channels share one connection. |
| **Virtual Host (vhost)** | A logical grouping of exchanges, queues, and permissions. Provides multi-tenant isolation. |

## Clustering and high availability

| Term | Definition |
|:---|:---|
| **Cluster** | Multiple RabbitMQ nodes working together, sharing users, vhosts, queues, exchanges, and bindings. |
| **Node** | A single RabbitMQ server instance within a cluster. |
| **Mirrored Queue** | (Deprecated) A queue replicated across multiple nodes. Use quorum queues instead. |
| **Partition** | Network split that separates cluster nodes. Requires partition handling strategy. |
| **Pause Minority** | Partition handling strategy where minority nodes pause until connectivity is restored. |

## Messaging patterns

| Term | Definition |
|:---|:---|
| **Work Queue** | Pattern where multiple consumers share a queue to distribute tasks. |
| **Publish/Subscribe** | Pattern where messages are broadcast to multiple consumers via a fanout exchange. |
| **Routing** | Pattern where messages are selectively delivered based on routing keys. |
| **Topics** | Pattern using pattern matching for flexible message routing. |
| **RPC** | Remote Procedure Call pattern using reply-to queues and correlation IDs. |

## Management and monitoring

| Term | Definition |
|:---|:---|
| **Management Plugin** | Web-based UI and HTTP API for managing and monitoring RabbitMQ. |
| **rabbitmqctl** | Command-line tool for managing RabbitMQ nodes and clusters. |
| **Shovel** | Plugin that moves messages between brokers (even across data centers). |
| **Federation** | Plugin that links exchanges and queues across brokers for geographic distribution. |

## Performance terms

| Term | Definition |
|:---|:---|
| **Throughput** | Number of messages processed per unit of time. |
| **Latency** | Time between message publish and consumer receipt. |
| **Flow Control** | Mechanism that slows down fast producers when consumers can't keep up. |
| **Memory Alarm** | Alert triggered when memory usage exceeds threshold, causing publishers to be blocked. |
| **Disk Alarm** | Alert triggered when disk space falls below threshold, causing publishers to be blocked. |

---

[← Back to Course Index](./README.md)
