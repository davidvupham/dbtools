# Messaging Concepts

In this lesson, you learn the fundamental concepts of message-based communication: producers, consumers, messages, and how they interact.

## The message lifecycle

Every message in RabbitMQ follows this journey:

```
┌──────────┐     ┌─────────┐     ┌───────┐     ┌──────────┐     ┌──────┐
│ Producer │────▶│ Channel │────▶│ Exch. │────▶│  Queue   │────▶│ Cons.│
│  creates │     │ publish │     │ route │     │  store   │     │ ACK  │
└──────────┘     └─────────┘     └───────┘     └──────────┘     └──────┘
     │                │                │              │              │
     ▼                ▼                ▼              ▼              ▼
  Message         Sent to          Routing        Waiting        Processed
  created         broker           decision       delivery       & removed
```

Let's examine each component.

## Producers

A **producer** is any application that sends messages to RabbitMQ.

### Producer responsibilities

1. **Connect** to RabbitMQ and open a channel
2. **Declare** (or verify) the exchange exists
3. **Publish** messages with routing information
4. **Optionally wait** for confirmations

### Producer code pattern

```python
import pika

# 1. Establish connection
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost')
)

# 2. Create a channel
channel = connection.channel()

# 3. Declare exchange (optional - can use default)
channel.exchange_declare(exchange='orders', exchange_type='direct')

# 4. Publish message
channel.basic_publish(
    exchange='orders',
    routing_key='new_order',
    body='{"order_id": 123, "item": "widget"}'
)

# 5. Clean up
connection.close()
```

### Producer best practices

| Practice | Reason |
|:---|:---|
| Reuse connections | Creating connections is expensive |
| Use channels for concurrency | Channels are lightweight |
| Set `delivery_mode=2` for important messages | Persists messages to disk |
| Enable publisher confirms | Know when messages reach broker |

## Consumers

A **consumer** is any application that receives messages from a queue.

### Consumer responsibilities

1. **Connect** to RabbitMQ and open a channel
2. **Declare** (or verify) the queue exists
3. **Subscribe** to the queue with a callback
4. **Process** messages
5. **Acknowledge** successful processing

### Consumer code pattern

```python
import pika

# 1. Establish connection
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost')
)

# 2. Create a channel
channel = connection.channel()

# 3. Declare queue (idempotent - safe to repeat)
channel.queue_declare(queue='orders')

# 4. Define callback function
def process_order(channel, method, properties, body):
    print(f"Processing: {body}")
    # Do work here...

    # 5. Acknowledge message
    channel.basic_ack(delivery_tag=method.delivery_tag)

# 6. Subscribe to queue
channel.basic_consume(
    queue='orders',
    on_message_callback=process_order,
    auto_ack=False  # Manual acknowledgment
)

# 7. Start consuming (blocks)
channel.start_consuming()
```

### Consumer best practices

| Practice | Reason |
|:---|:---|
| Use manual ACK | Prevents message loss if consumer crashes |
| Set prefetch count | Controls how many messages to buffer |
| Handle exceptions | NACK or requeue failed messages |
| Idempotent processing | Messages may be delivered more than once |

## Messages

A **message** consists of a body (payload) and properties (metadata).

### Message structure

```
┌─────────────────────────────────────────────────────────────┐
│                        MESSAGE                               │
├─────────────────────────────────────────────────────────────┤
│  Properties (Headers)                                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ delivery_mode: 2 (persistent)                          │  │
│  │ content_type: application/json                         │  │
│  │ correlation_id: abc-123                                │  │
│  │ reply_to: response_queue                               │  │
│  │ expiration: 60000                                      │  │
│  │ priority: 5                                            │  │
│  │ headers: {custom: "metadata"}                          │  │
│  └───────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  Body (Payload)                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ {"order_id": 123, "customer": "Alice", "items": [...]} │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Important message properties

| Property | Type | Description |
|:---|:---|:---|
| `delivery_mode` | int | 1 = transient, 2 = persistent (survives restart) |
| `content_type` | str | MIME type (e.g., `application/json`) |
| `correlation_id` | str | For correlating requests with responses |
| `reply_to` | str | Queue name for responses (RPC pattern) |
| `expiration` | str | Message TTL in milliseconds |
| `priority` | int | Message priority (0-255) |
| `timestamp` | int | Unix timestamp when message was created |
| `message_id` | str | Application-provided unique identifier |
| `headers` | dict | Custom key-value metadata |

### Setting message properties in Python

```python
import pika
import json
import uuid
import time

properties = pika.BasicProperties(
    delivery_mode=pika.DeliveryMode.Persistent,  # Survive restarts
    content_type='application/json',
    correlation_id=str(uuid.uuid4()),
    timestamp=int(time.time()),
    headers={'source': 'order-service', 'version': '1.0'}
)

message = json.dumps({'order_id': 123})

channel.basic_publish(
    exchange='orders',
    routing_key='new_order',
    body=message,
    properties=properties
)
```

## Connections and channels

Understanding connections and channels is crucial for performance.

### Connections

A **connection** is a TCP connection between your application and RabbitMQ.

```
┌────────────────┐                    ┌────────────────┐
│  Application   │◀───TCP Socket───▶│   RabbitMQ     │
│                │    (port 5672)     │   Broker       │
└────────────────┘                    └────────────────┘
```

- **Resource intensive** - Each connection uses ~100KB RAM
- **Should be reused** - Don't create connection per message
- **Long-lived** - Keep open for the application lifetime
- **One per application** is typically sufficient

### Channels

A **channel** is a virtual connection inside a TCP connection.

```
┌────────────────────────────────────────────────────────────┐
│                    TCP Connection                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Channel 1 │  │Channel 2 │  │Channel 3 │  │Channel 4 │   │
│  │(Thread A)│  │(Thread B)│  │(Thread C)│  │(Thread D)│   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└────────────────────────────────────────────────────────────┘
```

- **Lightweight** - Multiplexed over single connection
- **Thread-safe** - Use one channel per thread
- **Isolate operations** - Errors on one channel don't affect others
- **Create as needed** - For concurrent operations

### Connection/channel pattern

```python
# One connection for the application
connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)

# Multiple channels for different operations
publishing_channel = connection.channel()
consuming_channel = connection.channel()

# Or in threaded applications
def worker_thread():
    # Each thread gets its own channel
    channel = connection.channel()
    # ... do work ...
```

## Acknowledgments

**Acknowledgments** tell RabbitMQ whether a message was successfully processed.

### Types of acknowledgments

| Type | Method | Effect |
|:---|:---|:---|
| **ACK** | `basic_ack()` | Message successfully processed, remove from queue |
| **NACK** | `basic_nack()` | Processing failed, optionally requeue |
| **Reject** | `basic_reject()` | Reject single message, optionally requeue |

### Auto-ACK vs Manual-ACK

```python
# Auto-ACK (DANGEROUS in production)
channel.basic_consume(
    queue='tasks',
    on_message_callback=callback,
    auto_ack=True  # Message removed immediately on delivery
)

# Manual-ACK (RECOMMENDED)
def callback(ch, method, properties, body):
    try:
        process(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception:
        # Requeue for retry
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

channel.basic_consume(
    queue='tasks',
    on_message_callback=callback,
    auto_ack=False  # Must acknowledge manually
)
```

### What happens without ACK?

If a consumer crashes without acknowledging:

1. RabbitMQ waits for the connection to close
2. Message is **requeued** and delivered to another consumer
3. **No data loss** (assuming durable queue + persistent message)

This is why manual ACK is critical for reliability.

## Message flow diagram

Complete message flow with acknowledgments:

```
Producer                        RabbitMQ                        Consumer
   │                               │                               │
   │  1. Publish message           │                               │
   │──────────────────────────────▶│                               │
   │                               │                               │
   │  2. (Optional) Publisher      │                               │
   │     confirm                   │                               │
   │◀──────────────────────────────│                               │
   │                               │                               │
   │                               │  3. Deliver message           │
   │                               │──────────────────────────────▶│
   │                               │                               │
   │                               │                               │  4. Process
   │                               │                               │     message
   │                               │                               │
   │                               │  5. Acknowledge (ACK)         │
   │                               │◀──────────────────────────────│
   │                               │                               │
   │                               │  6. Remove from queue         │
   │                               │                               │
```

## Key takeaways

1. **Producers publish messages** - They send to exchanges, not directly to queues
2. **Consumers subscribe to queues** - They receive and acknowledge messages
3. **Messages have body and properties** - Properties control behavior (persistence, TTL, etc.)
4. **Connections are expensive, channels are cheap** - One connection, many channels
5. **Always use manual acknowledgments** - Auto-ACK risks message loss
6. **Message lifecycle matters** - Understand publish → route → queue → deliver → ACK

## What's next?

In the next lesson, you'll install RabbitMQ using Docker and explore the management interface.

---

[← Previous: Introduction](./01_introduction.md) | [Back to Module 1](./README.md) | [Next: Installation →](./03_installation.md)
