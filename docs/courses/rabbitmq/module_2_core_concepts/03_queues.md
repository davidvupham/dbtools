# Queues

In this lesson, you learn about queues - how they store messages, their properties, and the different queue types available in RabbitMQ.

## What is a queue?

A **queue** is a sequential data structure that stores messages until they are consumed. Messages are delivered in FIFO (First In, First Out) order.

```
   Publish                                              Consume
      │                                                    │
      ▼                                                    ▼
┌─────────────────────────────────────────────────────────────┐
│  Queue: order_processing                                     │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                   │
│  │msg 1│ │msg 2│ │msg 3│ │msg 4│ │msg 5│  →  Consumer      │
│  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘                   │
│    ▲                                                        │
│    │                                                        │
│   HEAD (oldest)                              TAIL (newest)  │
└─────────────────────────────────────────────────────────────┘
```

## Queue properties

When declaring a queue, you can specify several properties:

### Basic declaration

```python
channel.queue_declare(queue='my_queue')
```

### Full declaration with all options

```python
result = channel.queue_declare(
    queue='my_queue',        # Queue name (empty for auto-generated)
    durable=True,            # Survive broker restart
    exclusive=False,         # Only this connection can use it
    auto_delete=False,       # Delete when last consumer disconnects
    arguments={              # Additional arguments
        'x-message-ttl': 300000,
        'x-max-length': 10000
    }
)

queue_name = result.method.queue  # Actual queue name
message_count = result.method.message_count
consumer_count = result.method.consumer_count
```

## Durability

**Durable queues** survive broker restarts. Non-durable queues are deleted.

```python
# Durable queue - survives restart
channel.queue_declare(queue='important_tasks', durable=True)

# Non-durable (transient) - lost on restart
channel.queue_declare(queue='temp_work', durable=False)
```

> [!IMPORTANT]
> Queue durability only saves the queue definition. For messages to survive, they must also be published with `delivery_mode=2` (persistent).

### Complete durability setup

```python
# 1. Durable queue
channel.queue_declare(queue='orders', durable=True)

# 2. Persistent message
channel.basic_publish(
    exchange='',
    routing_key='orders',
    body='order data',
    properties=pika.BasicProperties(
        delivery_mode=pika.DeliveryMode.Persistent
    )
)
```

## Exclusive queues

**Exclusive queues** can only be used by the connection that declared them and are deleted when that connection closes.

```python
# Create exclusive queue with auto-generated name
result = channel.queue_declare(queue='', exclusive=True)
private_queue = result.method.queue
# e.g., 'amq.gen-JzTY20BRgKO-HjmUJj0wLg'
```

Use cases:
- Reply queues for RPC patterns
- Temporary private queues
- Queues that shouldn't outlive the connection

## Auto-delete queues

**Auto-delete queues** are deleted when the last consumer unsubscribes.

```python
channel.queue_declare(queue='temp_queue', auto_delete=True)
```

> [!NOTE]
> Auto-delete triggers when the last consumer leaves, not when the queue becomes empty.

## Queue arguments

Queue arguments (x-arguments) configure advanced behaviors:

### Message TTL

Messages expire after a specified time:

```python
channel.queue_declare(
    queue='expiring_tasks',
    durable=True,
    arguments={
        'x-message-ttl': 60000  # 60 seconds in milliseconds
    }
)
```

### Queue max length

Limit the number of messages:

```python
channel.queue_declare(
    queue='bounded_queue',
    durable=True,
    arguments={
        'x-max-length': 1000,  # Max 1000 messages
        'x-overflow': 'reject-publish'  # Or 'drop-head' (default)
    }
)
```

Overflow behaviors:
- `drop-head` - Remove oldest messages (default)
- `reject-publish` - Reject new messages
- `reject-publish-dlx` - Reject and dead-letter

### Dead letter exchange

Route rejected/expired messages to another exchange:

```python
channel.queue_declare(
    queue='tasks',
    durable=True,
    arguments={
        'x-dead-letter-exchange': 'dlx',
        'x-dead-letter-routing-key': 'failed'
    }
)
```

### Priority queues

Enable message priorities (0-255):

```python
channel.queue_declare(
    queue='priority_tasks',
    durable=True,
    arguments={
        'x-max-priority': 10  # Enable priorities 0-10
    }
)

# Publish with priority
channel.basic_publish(
    exchange='',
    routing_key='priority_tasks',
    body='urgent task',
    properties=pika.BasicProperties(priority=10)
)
```

### Queue expiry (lazy queues)

Queue is deleted if unused for a period:

```python
channel.queue_declare(
    queue='temp_queue',
    arguments={
        'x-expires': 1800000  # Delete after 30 minutes of no use
    }
)
```

## Queue types

RabbitMQ 3.8+ introduced different queue types:

### Classic queues (default)

Traditional queues, single leader, optional mirroring.

```python
channel.queue_declare(
    queue='classic_queue',
    arguments={
        'x-queue-type': 'classic'
    }
)
```

### Quorum queues

Replicated queues using Raft consensus. Recommended for data safety.

```python
channel.queue_declare(
    queue='important_queue',
    durable=True,  # Required for quorum queues
    arguments={
        'x-queue-type': 'quorum'
    }
)
```

Benefits:
- Data safety across node failures
- Automatic leader election
- Better consistency guarantees

Limitations:
- Must be durable
- No exclusive or auto-delete
- Higher resource usage

### Stream queues

Append-only logs, multiple consumers can read same messages.

```python
channel.queue_declare(
    queue='event_stream',
    durable=True,
    arguments={
        'x-queue-type': 'stream',
        'x-max-length-bytes': 1000000000  # 1GB
    }
)
```

Benefits:
- Replay from any point
- Multiple consumers read same data
- High throughput
- Time-based retention

## Queue operations

### Get queue information

```python
# Passive declare returns info without modifying
result = channel.queue_declare(queue='my_queue', passive=True)
print(f"Messages: {result.method.message_count}")
print(f"Consumers: {result.method.consumer_count}")
```

### Purge queue

Delete all messages without deleting the queue:

```python
channel.queue_purge(queue='my_queue')
```

### Delete queue

```python
# Delete only if empty and has no consumers
channel.queue_delete(queue='my_queue', if_empty=True, if_unused=True)

# Force delete
channel.queue_delete(queue='my_queue')
```

## Consumer prefetch

Control how many messages are delivered before acknowledgment:

```python
# Per-consumer limit
channel.basic_qos(prefetch_count=10)

# Global limit (all consumers on channel)
channel.basic_qos(prefetch_count=100, global_qos=True)
```

### Why prefetch matters

Without prefetch, RabbitMQ pushes messages as fast as possible:

```
No prefetch (bad for slow consumers):
Consumer A: [processing] [msg2] [msg3] [msg4] [msg5] ...
Consumer B: [idle]

With prefetch_count=1 (fair dispatch):
Consumer A: [processing]
Consumer B: [processing]
Consumer A: [processing]
...
```

## Queue patterns

### Work queue pattern

Multiple consumers share a queue for load balancing:

```python
# Same setup for all workers
channel.queue_declare(queue='tasks', durable=True)
channel.basic_qos(prefetch_count=1)  # Fair dispatch
channel.basic_consume(queue='tasks', on_message_callback=callback)
```

### Competing consumers

```
Producer → [task1, task2, task3, task4] → Consumer A processes task1
                                       → Consumer B processes task2
                                       → Consumer A processes task3
                                       ...
```

### Temporary reply queue

For RPC patterns:

```python
# Create exclusive reply queue
result = channel.queue_declare(queue='', exclusive=True)
reply_queue = result.method.queue

# Include in message for responses
channel.basic_publish(
    exchange='',
    routing_key='rpc_queue',
    body=request,
    properties=pika.BasicProperties(
        reply_to=reply_queue,
        correlation_id=str(uuid.uuid4())
    )
)
```

## Monitoring queues

### Via Management UI

1. Navigate to **Queues** tab
2. Click on queue name for details
3. View: message counts, rates, consumer info, bindings

### Via rabbitmqctl

```bash
# List all queues with message counts
docker exec rabbitmq rabbitmqctl list_queues name messages

# Detailed queue info
docker exec rabbitmq rabbitmqctl list_queues name durable auto_delete arguments
```

### Via Pika

```python
result = channel.queue_declare(queue='my_queue', passive=True)
print(f"Ready messages: {result.method.message_count}")
print(f"Consumer count: {result.method.consumer_count}")
```

## Key takeaways

1. **Queues store messages** - They're the buffers between producers and consumers
2. **Durability saves the definition** - But messages need persistence too
3. **Exclusive queues are private** - Deleted when connection closes
4. **Arguments control behavior** - TTL, max length, dead lettering
5. **Quorum queues for safety** - Use for important data
6. **Prefetch enables fair dispatch** - Essential for work queues

## What's next?

In the next lesson, you'll learn about bindings - the rules that connect exchanges to queues.

---

[← Previous: Exchanges](./02_exchanges.md) | [Back to Module 2](./README.md) | [Next: Bindings →](./04_bindings.md)
