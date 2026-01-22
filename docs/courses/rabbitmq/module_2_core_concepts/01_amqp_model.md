# The AMQP Model

In this lesson, you learn the AMQP 0-9-1 protocol model that RabbitMQ implements. Understanding this model is essential for designing effective messaging architectures.

## What is AMQP?

**AMQP** (Advanced Message Queuing Protocol) is an open standard for message-oriented middleware. Version 0-9-1 is what RabbitMQ implements.

Key characteristics:
- **Wire-level protocol** - Defines exact byte format on the network
- **Programmable** - Applications define routing behavior
- **Interoperable** - Different languages/platforms can communicate
- **Broker-centric** - The broker does the routing work

## The AMQP model overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              AMQP Broker                                     │
│                                                                              │
│   ┌───────────┐         ┌─────────────┐         ┌───────────────────────┐   │
│   │           │ Publish │             │ Route   │                       │   │
│   │ Producer  │────────▶│  Exchange   │────────▶│  Queue                │   │
│   │           │         │             │         │  (message buffer)     │   │
│   └───────────┘         └─────────────┘         └───────────┬───────────┘   │
│                               │                             │               │
│                               │ Binding                     │ Consume       │
│                               │ (routing rule)              │               │
│                               ▼                             ▼               │
│                         ┌─────────────┐           ┌───────────────────┐     │
│                         │   Binding   │           │     Consumer      │     │
│                         │   Table     │           │   (application)   │     │
│                         └─────────────┘           └───────────────────┘     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Core entities

AMQP defines several entities that work together:

### 1. Connection

A **Connection** is a long-lived TCP connection between a client and the broker.

```python
# A connection represents a TCP socket
connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
```

Properties:
- Authenticated (username/password or certificate)
- Multiplexed (contains multiple channels)
- Resource-intensive (create few, reuse often)

### 2. Channel

A **Channel** is a virtual connection within a TCP connection.

```python
# Channels are lightweight, create as needed
channel = connection.channel()
```

Properties:
- Lightweight (thousands possible per connection)
- Isolated (errors don't affect other channels)
- Thread-affinity (use one channel per thread)

### 3. Exchange

An **Exchange** receives messages and routes them to queues based on bindings.

```python
# Declare an exchange
channel.exchange_declare(
    exchange='orders',
    exchange_type='direct',
    durable=True
)
```

Types:
- **Direct** - Routes by exact routing key match
- **Topic** - Routes by pattern matching
- **Fanout** - Routes to all bound queues
- **Headers** - Routes by message headers

### 4. Queue

A **Queue** is a named buffer that stores messages.

```python
# Declare a queue
channel.queue_declare(
    queue='order_processing',
    durable=True
)
```

Properties:
- Named (unique identifier within a vhost)
- Ordered (FIFO - first in, first out)
- Optionally durable (survives restart)

### 5. Binding

A **Binding** is a rule that tells an exchange how to route messages to queues.

```python
# Create a binding
channel.queue_bind(
    exchange='orders',
    queue='order_processing',
    routing_key='new_order'
)
```

Components:
- Source exchange
- Destination queue
- Binding key (pattern to match)

## Message flow

Let's trace a message through the system:

```
Step 1: Publish
┌──────────┐                     ┌────────────┐
│ Producer │─────publish()──────▶│  Exchange  │
│          │  routing_key='x'    │            │
└──────────┘                     └─────┬──────┘
                                       │
Step 2: Route                          │
                                       ▼
                              ┌────────────────┐
                              │ Binding Table  │
                              │ x → Queue A    │
                              │ y → Queue B    │
                              └───────┬────────┘
                                      │
Step 3: Queue                         │
                                      ▼
                              ┌────────────────┐
                              │    Queue A     │
                              │ [msg] [msg]    │
                              └───────┬────────┘
                                      │
Step 4: Deliver                       │
                                      ▼
                              ┌────────────────┐
                              │   Consumer     │
                              │ callback(msg)  │
                              └────────────────┘
                                      │
Step 5: Acknowledge                   │
                                      ▼
                              ┌────────────────┐
                              │    Queue A     │
                              │ [msg]          │ (message removed)
                              └────────────────┘
```

### Detailed flow

1. **Publish**: Producer sends message to exchange with a routing key
2. **Route**: Exchange examines bindings and routing key
3. **Queue**: Message is copied to matching queue(s)
4. **Deliver**: Broker pushes message to subscribed consumer
5. **Acknowledge**: Consumer confirms processing, message removed

## The default exchange

RabbitMQ provides a pre-declared **default exchange** (nameless direct exchange).

```python
# Publishing to default exchange
channel.basic_publish(
    exchange='',           # Empty string = default exchange
    routing_key='my_queue',  # Routes directly to queue named 'my_queue'
    body='Hello'
)
```

Special behavior:
- Every queue is automatically bound to it
- Binding key equals the queue name
- Makes it easy to send directly to a queue

This is what we used in Module 1's Hello World example.

## Virtual hosts

**Virtual hosts** (vhosts) provide logical grouping and separation:

```
┌─────────────────────────────────────────────────────────┐
│                    RabbitMQ Server                       │
│  ┌──────────────────┐    ┌──────────────────┐          │
│  │   vhost: /       │    │  vhost: /prod    │          │
│  │  ┌────────────┐  │    │  ┌────────────┐  │          │
│  │  │ Exchanges  │  │    │  │ Exchanges  │  │          │
│  │  │ Queues     │  │    │  │ Queues     │  │          │
│  │  │ Bindings   │  │    │  │ Bindings   │  │          │
│  │  │ Users      │  │    │  │ Users      │  │          │
│  │  └────────────┘  │    │  └────────────┘  │          │
│  └──────────────────┘    └──────────────────┘          │
└─────────────────────────────────────────────────────────┘
```

Uses:
- Multi-tenant isolation
- Environment separation (dev, staging, prod)
- Access control boundaries

```python
# Connect to a specific vhost
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host='localhost',
        virtual_host='/production'
    )
)
```

## AMQP methods

The protocol defines operations as methods organized by class:

| Class | Methods | Purpose |
|:---|:---|:---|
| **Connection** | start, tune, open, close | Connection lifecycle |
| **Channel** | open, flow, close | Channel management |
| **Exchange** | declare, delete, bind | Exchange operations |
| **Queue** | declare, delete, bind, purge | Queue operations |
| **Basic** | publish, consume, ack, nack, get | Message operations |
| **Tx** | select, commit, rollback | Transactions |
| **Confirm** | select | Publisher confirms |

In Pika, these map to channel methods:

```python
channel.exchange_declare(...)   # Exchange.Declare
channel.queue_declare(...)      # Queue.Declare
channel.queue_bind(...)         # Queue.Bind
channel.basic_publish(...)      # Basic.Publish
channel.basic_consume(...)      # Basic.Consume
channel.basic_ack(...)          # Basic.Ack
```

## Message acknowledgments

AMQP supports different acknowledgment modes:

### Automatic (auto-ack)

```python
channel.basic_consume(
    queue='tasks',
    on_message_callback=callback,
    auto_ack=True  # Dangerous!
)
```

- Message acknowledged on delivery
- No guarantee of processing
- Risk of message loss

### Manual acknowledgment

```python
def callback(ch, method, properties, body):
    process(body)
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(
    queue='tasks',
    on_message_callback=callback,
    auto_ack=False
)
```

- Application controls acknowledgment
- Message persists until ACK received
- Enables retry on failure

### Negative acknowledgment

```python
# Reject and requeue
ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

# Reject and discard (or dead-letter)
ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
```

## Durability and persistence

For messages to survive broker restarts:

### 1. Durable exchange

```python
channel.exchange_declare(
    exchange='orders',
    exchange_type='direct',
    durable=True  # Exchange survives restart
)
```

### 2. Durable queue

```python
channel.queue_declare(
    queue='order_processing',
    durable=True  # Queue survives restart
)
```

### 3. Persistent message

```python
channel.basic_publish(
    exchange='orders',
    routing_key='new',
    body=message,
    properties=pika.BasicProperties(
        delivery_mode=2  # Persistent
    )
)
```

All three are required for complete durability!

## Key takeaways

1. **AMQP is programmable** - Applications define exchanges, queues, and bindings
2. **Exchanges route, queues store** - Clear separation of concerns
3. **Bindings are rules** - They connect exchanges to queues with patterns
4. **Default exchange is convenient** - Routes directly to queues by name
5. **Virtual hosts isolate** - Separate environments within one broker
6. **Durability requires three parts** - Exchange + queue + message persistence

## What's next?

In the next lesson, you'll learn about exchange types in detail - when to use direct, topic, fanout, and headers exchanges.

---

[← Back to Module 2](./README.md) | [Next: Exchanges →](./02_exchanges.md)
