# Message Properties

In this lesson, you learn about message properties - the metadata attached to messages that controls their behavior and provides information to consumers.

## Message structure

A RabbitMQ message consists of two parts:

```
┌─────────────────────────────────────────────────────────────┐
│                        MESSAGE                               │
├─────────────────────────────────────────────────────────────┤
│  PROPERTIES (metadata)                                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ content_type    │ application/json                     │  │
│  │ delivery_mode   │ 2 (persistent)                       │  │
│  │ priority        │ 5                                    │  │
│  │ correlation_id  │ abc-123                              │  │
│  │ headers         │ {custom: "data"}                     │  │
│  └───────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  BODY (payload)                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ {"order_id": 123, "customer": "Alice"}                 │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Standard properties

AMQP defines a set of standard message properties:

| Property | Type | Description |
|:---|:---|:---|
| `content_type` | string | MIME type (e.g., `application/json`) |
| `content_encoding` | string | Encoding (e.g., `utf-8`, `gzip`) |
| `delivery_mode` | int | 1=transient, 2=persistent |
| `priority` | int | Priority 0-255 |
| `correlation_id` | string | For correlating requests/responses |
| `reply_to` | string | Queue name for responses |
| `expiration` | string | TTL in milliseconds |
| `message_id` | string | Application message identifier |
| `timestamp` | int | Unix timestamp |
| `type` | string | Application message type |
| `user_id` | string | User who published |
| `app_id` | string | Application identifier |
| `headers` | dict | Custom key-value headers |

## Setting properties in Python

```python
import pika
import json
import uuid
import time

properties = pika.BasicProperties(
    content_type='application/json',
    content_encoding='utf-8',
    delivery_mode=pika.DeliveryMode.Persistent,
    priority=5,
    correlation_id=str(uuid.uuid4()),
    reply_to='response_queue',
    expiration='60000',  # 60 seconds
    message_id=str(uuid.uuid4()),
    timestamp=int(time.time()),
    type='order.created',
    app_id='order-service',
    headers={
        'x-retry-count': 0,
        'x-source': 'web'
    }
)

channel.basic_publish(
    exchange='',
    routing_key='orders',
    body=json.dumps({'order_id': 123}),
    properties=properties
)
```

## Reading properties in consumer

```python
def callback(ch, method, properties, body):
    print(f"Content-Type: {properties.content_type}")
    print(f"Message ID: {properties.message_id}")
    print(f"Timestamp: {properties.timestamp}")
    print(f"Priority: {properties.priority}")
    print(f"Headers: {properties.headers}")
    print(f"Body: {body.decode()}")

    ch.basic_ack(delivery_tag=method.delivery_tag)
```

## Key properties explained

### Delivery mode (persistence)

Controls whether messages survive broker restarts:

```python
# Transient - lost on restart
properties = pika.BasicProperties(delivery_mode=1)

# Persistent - written to disk
properties = pika.BasicProperties(delivery_mode=2)
# Or use the enum:
properties = pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent)
```

> [!IMPORTANT]
> Persistence requires BOTH:
> 1. `delivery_mode=2` on the message
> 2. `durable=True` on the queue

### Content type and encoding

Help consumers understand the payload:

```python
# JSON message
properties = pika.BasicProperties(
    content_type='application/json',
    content_encoding='utf-8'
)
body = json.dumps({'data': 'value'})

# Binary/compressed
properties = pika.BasicProperties(
    content_type='application/octet-stream',
    content_encoding='gzip'
)
body = gzip.compress(data)

# Plain text
properties = pika.BasicProperties(
    content_type='text/plain',
    content_encoding='utf-8'
)
body = 'Hello World'
```

### Expiration (TTL)

Messages are discarded or dead-lettered after expiration:

```python
# Message expires in 30 seconds
properties = pika.BasicProperties(
    expiration='30000'  # milliseconds as STRING
)
```

> [!NOTE]
> `expiration` is a STRING, not an integer. This is an AMQP quirk.

What happens when messages expire:
1. If queue has DLX configured → message is dead-lettered
2. Otherwise → message is discarded

### Priority

Higher priority messages are delivered first (requires priority queue):

```python
# Declare priority queue
channel.queue_declare(
    queue='priority_tasks',
    durable=True,
    arguments={'x-max-priority': 10}
)

# Publish with priority
channel.basic_publish(
    exchange='',
    routing_key='priority_tasks',
    body='urgent',
    properties=pika.BasicProperties(priority=10)
)

channel.basic_publish(
    exchange='',
    routing_key='priority_tasks',
    body='normal',
    properties=pika.BasicProperties(priority=1)
)
# 'urgent' will be delivered before 'normal'
```

### Correlation ID and Reply-to

Used for RPC (request/response) patterns:

```python
# Client sends request
correlation_id = str(uuid.uuid4())
result = channel.queue_declare(queue='', exclusive=True)
reply_queue = result.method.queue

channel.basic_publish(
    exchange='',
    routing_key='rpc_queue',
    body='request data',
    properties=pika.BasicProperties(
        correlation_id=correlation_id,
        reply_to=reply_queue
    )
)

# Server processes and responds
def on_request(ch, method, props, body):
    response = process(body)
    ch.basic_publish(
        exchange='',
        routing_key=props.reply_to,  # Response goes here
        body=response,
        properties=pika.BasicProperties(
            correlation_id=props.correlation_id  # Same ID
        )
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)
```

### Timestamp

Unix timestamp when message was created:

```python
import time

properties = pika.BasicProperties(
    timestamp=int(time.time())
)

# In consumer
from datetime import datetime
created_at = datetime.fromtimestamp(properties.timestamp)
```

### Type

Application-defined message type:

```python
# Useful for routing different message types to different handlers
properties = pika.BasicProperties(type='order.created')

# Consumer can dispatch based on type
def callback(ch, method, properties, body):
    if properties.type == 'order.created':
        handle_order_created(body)
    elif properties.type == 'order.cancelled':
        handle_order_cancelled(body)
```

## Custom headers

The `headers` property allows arbitrary key-value metadata:

```python
properties = pika.BasicProperties(
    headers={
        'x-retry-count': 0,
        'x-source': 'mobile-app',
        'x-user-id': '12345',
        'x-trace-id': 'abc-123-def'
    }
)
```

### Common header patterns

```python
# Retry tracking
headers = {
    'x-retry-count': 3,
    'x-original-queue': 'tasks',
    'x-first-failure': '2024-01-15T10:30:00Z'
}

# Tracing/observability
headers = {
    'x-trace-id': 'abc123',
    'x-span-id': 'def456',
    'x-parent-id': 'ghi789'
}

# Routing hints
headers = {
    'x-tenant-id': 'acme-corp',
    'x-region': 'us-west-2',
    'x-priority-class': 'premium'
}
```

### Reading headers

```python
def callback(ch, method, properties, body):
    headers = properties.headers or {}

    retry_count = headers.get('x-retry-count', 0)
    trace_id = headers.get('x-trace-id')

    if retry_count > 3:
        # Too many retries, send to DLQ
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    else:
        process(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
```

## Message property patterns

### Self-describing messages

```python
def publish_event(channel, event_type: str, data: dict):
    """Publish a self-describing event message."""
    properties = pika.BasicProperties(
        content_type='application/json',
        content_encoding='utf-8',
        delivery_mode=pika.DeliveryMode.Persistent,
        message_id=str(uuid.uuid4()),
        timestamp=int(time.time()),
        type=event_type,
        app_id='my-service',
        headers={
            'x-schema-version': '1.0',
            'x-event-type': event_type
        }
    )

    channel.basic_publish(
        exchange='events',
        routing_key=event_type,
        body=json.dumps(data),
        properties=properties
    )

# Usage
publish_event(channel, 'order.created', {'order_id': 123})
```

### Dead letter information

When a message is dead-lettered, RabbitMQ adds headers:

```python
def handle_dead_letter(ch, method, properties, body):
    headers = properties.headers or {}

    # RabbitMQ adds these when dead-lettering
    death_info = headers.get('x-death', [])
    if death_info:
        first_death = death_info[0]
        print(f"Original queue: {first_death['queue']}")
        print(f"Reason: {first_death['reason']}")
        print(f"Time: {first_death['time']}")
```

### Versioned messages

```python
properties = pika.BasicProperties(
    type='order.created',
    headers={
        'x-schema-version': '2.0',
        'x-backwards-compatible': True
    }
)
```

## Property comparison table

| Property | When to Use | Example Value |
|:---|:---|:---|
| `content_type` | Always for structured data | `application/json` |
| `delivery_mode` | Important messages | `2` (persistent) |
| `expiration` | Time-sensitive messages | `'30000'` (30 sec) |
| `priority` | Prioritized processing | `1-10` |
| `correlation_id` | RPC patterns | UUID |
| `reply_to` | RPC patterns | Queue name |
| `message_id` | Deduplication, tracing | UUID |
| `timestamp` | Audit, ordering | Unix timestamp |
| `type` | Multi-type queues | `'order.created'` |
| `headers` | Custom metadata | `{'x-tenant': 'a'}` |

## Key takeaways

1. **Properties are metadata** - They describe the message, not the payload
2. **Persistence requires both** - `delivery_mode=2` AND durable queue
3. **expiration is a string** - Milliseconds as string, not integer
4. **Priority needs queue support** - Declare with `x-max-priority`
5. **Headers are flexible** - Use for custom routing, tracing, retry tracking
6. **correlation_id + reply_to** - Essential for RPC patterns

## What's next?

You've completed the Core Concepts module! Test your knowledge with the quiz, then move on to Module 3: Messaging Patterns.

---

[← Previous: Bindings](./04_bindings.md) | [Back to Module 2](./README.md) | [Quiz →](./quiz_module_2.md)
