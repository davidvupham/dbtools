# Dead Letter Exchanges

In this lesson, you learn to handle message failures using Dead Letter Exchanges (DLX) - RabbitMQ's mechanism for routing messages that can't be delivered or processed.

## What is a dead letter exchange?

A **Dead Letter Exchange (DLX)** is a normal exchange where messages are sent when they can't be processed. Messages become "dead letters" when:

1. **Rejected** - Consumer rejects with `requeue=False`
2. **Expired** - Message TTL exceeded
3. **Queue overflow** - Queue `x-max-length` exceeded

```
┌────────────────┐     reject/expire/overflow     ┌─────────────────┐
│  Main Queue    │ ──────────────────────────────▶│  Dead Letter    │
│                │                                 │  Exchange (DLX) │
└────────────────┘                                 └────────┬────────┘
                                                            │
                                                            ▼
                                                   ┌─────────────────┐
                                                   │  Dead Letter    │
                                                   │  Queue (DLQ)    │
                                                   └─────────────────┘
```

## Setting up a basic DLX

### Step 1: Create the dead letter exchange and queue

```python
import pika

connection = pika.BlockingConnection()
channel = connection.channel()

# Create DLX (just a normal exchange)
channel.exchange_declare(
    exchange='dlx',
    exchange_type='direct',
    durable=True
)

# Create dead letter queue
channel.queue_declare(queue='dead_letters', durable=True)

# Bind DLQ to DLX
channel.queue_bind(
    exchange='dlx',
    queue='dead_letters',
    routing_key='failed'
)
```

### Step 2: Create main queue with DLX configuration

```python
# Main queue that routes failed messages to DLX
channel.queue_declare(
    queue='orders',
    durable=True,
    arguments={
        'x-dead-letter-exchange': 'dlx',
        'x-dead-letter-routing-key': 'failed'
    }
)
```

### Step 3: Consumer that rejects messages

```python
def callback(ch, method, properties, body):
    try:
        process_order(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Failed to process: {e}")
        # This sends the message to DLX
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

channel.basic_consume(
    queue='orders',
    on_message_callback=callback,
    auto_ack=False
)
```

## Dead letter message headers

When a message is dead-lettered, RabbitMQ adds the `x-death` header with information about why and when:

```python
def handle_dead_letter(ch, method, properties, body):
    headers = properties.headers or {}
    x_death = headers.get('x-death', [])

    if x_death:
        death_info = x_death[0]
        print(f"Original queue: {death_info['queue']}")
        print(f"Reason: {death_info['reason']}")
        print(f"Death count: {death_info['count']}")
        print(f"Time: {death_info['time']}")
        print(f"Original exchange: {death_info['exchange']}")
        print(f"Original routing key: {death_info['routing-keys']}")
```

## DLX for message expiration

Messages can be dead-lettered when their TTL expires:

```python
# Queue with message TTL
channel.queue_declare(
    queue='time_sensitive_orders',
    durable=True,
    arguments={
        'x-message-ttl': 60000,  # 60 seconds
        'x-dead-letter-exchange': 'dlx',
        'x-dead-letter-routing-key': 'expired'
    }
)

# Or per-message TTL
channel.basic_publish(
    exchange='',
    routing_key='orders',
    body=message,
    properties=pika.BasicProperties(
        expiration='30000'  # 30 seconds
    )
)
```

## DLX for queue overflow

When a queue reaches its maximum length:

```python
channel.queue_declare(
    queue='limited_orders',
    durable=True,
    arguments={
        'x-max-length': 1000,
        'x-overflow': 'reject-publish-dlx',  # Dead-letter overflow
        'x-dead-letter-exchange': 'dlx',
        'x-dead-letter-routing-key': 'overflow'
    }
)
```

Overflow behaviors:
- `drop-head` - Remove oldest messages (default, no DLX)
- `reject-publish` - Reject new messages (nack to publisher)
- `reject-publish-dlx` - Dead-letter new messages that can't fit

## Retry patterns with DLX

### Pattern 1: Simple retry with delay

Use DLX to implement delayed retry:

```python
# Retry queue with delay
channel.queue_declare(
    queue='orders_retry',
    durable=True,
    arguments={
        'x-message-ttl': 30000,  # 30 second delay
        'x-dead-letter-exchange': '',
        'x-dead-letter-routing-key': 'orders'  # Back to main queue
    }
)

# Main queue
channel.queue_declare(
    queue='orders',
    durable=True,
    arguments={
        'x-dead-letter-exchange': '',
        'x-dead-letter-routing-key': 'orders_retry'
    }
)
```

Flow:
```
orders → (reject) → orders_retry → (30s delay) → orders → ...
```

### Pattern 2: Retry with count limit

Track retries in message headers:

```python
def callback(ch, method, properties, body):
    headers = properties.headers or {}
    retry_count = headers.get('x-retry-count', 0)
    max_retries = 3

    try:
        process_order(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except TemporaryError as e:
        if retry_count < max_retries:
            # Republish with incremented retry count
            new_headers = dict(headers)
            new_headers['x-retry-count'] = retry_count + 1

            ch.basic_publish(
                exchange='',
                routing_key='orders_retry',
                body=body,
                properties=pika.BasicProperties(
                    headers=new_headers,
                    delivery_mode=2
                )
            )
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print(f"Retry {retry_count + 1}/{max_retries}")
        else:
            # Max retries exceeded, send to permanent DLQ
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            print(f"Max retries exceeded, dead-lettered")

    except PermanentError as e:
        # Permanent failure, dead-letter immediately
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
```

### Pattern 3: Exponential backoff

Multiple retry queues with increasing delays:

```python
# Setup retry queues with different delays
delays = [5000, 30000, 120000, 600000]  # 5s, 30s, 2m, 10m

for i, delay in enumerate(delays):
    channel.queue_declare(
        queue=f'orders_retry_{i}',
        durable=True,
        arguments={
            'x-message-ttl': delay,
            'x-dead-letter-exchange': '',
            'x-dead-letter-routing-key': 'orders'
        }
    )

# Consumer logic
def callback(ch, method, properties, body):
    headers = properties.headers or {}
    retry_count = headers.get('x-retry-count', 0)

    try:
        process_order(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception:
        if retry_count < len(delays):
            new_headers = dict(headers)
            new_headers['x-retry-count'] = retry_count + 1

            ch.basic_publish(
                exchange='',
                routing_key=f'orders_retry_{retry_count}',
                body=body,
                properties=pika.BasicProperties(
                    headers=new_headers,
                    delivery_mode=2
                )
            )
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
```

## Processing dead letters

### Dead letter consumer

```python
def process_dead_letter(ch, method, properties, body):
    headers = properties.headers or {}
    x_death = headers.get('x-death', [{}])[0]

    print(f"=== Dead Letter ===")
    print(f"Original queue: {x_death.get('queue')}")
    print(f"Reason: {x_death.get('reason')}")
    print(f"Death count: {x_death.get('count')}")
    print(f"Body: {body.decode()}")
    print(f"==================")

    # Options:
    # 1. Log and discard
    # 2. Store for manual review
    # 3. Alert operations team
    # 4. Attempt recovery

    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(
    queue='dead_letters',
    on_message_callback=process_dead_letter,
    auto_ack=False
)
```

### Reprocessing dead letters

```python
def reprocess_dead_letters():
    """Move dead letters back to original queue."""
    connection = pika.BlockingConnection()
    channel = connection.channel()

    while True:
        method, properties, body = channel.basic_get(
            queue='dead_letters',
            auto_ack=False
        )

        if method is None:
            break  # Queue empty

        headers = properties.headers or {}
        x_death = headers.get('x-death', [{}])[0]
        original_queue = x_death.get('queue', 'unknown')

        # Republish to original queue
        channel.basic_publish(
            exchange='',
            routing_key=original_queue,
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=2,
                headers={'x-reprocessed': True}
            )
        )

        channel.basic_ack(delivery_tag=method.delivery_tag)
        print(f"Requeued message to {original_queue}")

    connection.close()
```

## Complete DLX setup example

```python
#!/usr/bin/env python
"""Complete DLX setup with retry logic."""
import pika


def setup_dlx_infrastructure():
    connection = pika.BlockingConnection()
    channel = connection.channel()

    # === Dead Letter Infrastructure ===

    # DLX for permanent failures
    channel.exchange_declare(
        exchange='dlx.permanent',
        exchange_type='direct',
        durable=True
    )

    channel.queue_declare(queue='dead_letters', durable=True)
    channel.queue_bind(
        exchange='dlx.permanent',
        queue='dead_letters',
        routing_key='failed'
    )

    # === Retry Infrastructure ===

    # Retry queues with increasing delays
    retry_delays = [
        ('retry.5s', 5000),
        ('retry.30s', 30000),
        ('retry.2m', 120000),
        ('retry.10m', 600000),
    ]

    for queue_name, delay in retry_delays:
        channel.queue_declare(
            queue=queue_name,
            durable=True,
            arguments={
                'x-message-ttl': delay,
                'x-dead-letter-exchange': '',
                'x-dead-letter-routing-key': 'orders'
            }
        )

    # === Main Queue ===

    channel.queue_declare(
        queue='orders',
        durable=True,
        arguments={
            'x-dead-letter-exchange': 'dlx.permanent',
            'x-dead-letter-routing-key': 'failed'
        }
    )

    print("DLX infrastructure created")
    connection.close()


if __name__ == '__main__':
    setup_dlx_infrastructure()
```

## Key takeaways

1. **DLX is just a regular exchange** - Configure on the source queue
2. **Three causes of dead lettering** - Rejection, expiration, overflow
3. **x-death header contains history** - Original queue, reason, count
4. **Implement retry with TTL queues** - Dead-letter back to main queue after delay
5. **Track retry count in headers** - Prevent infinite retry loops
6. **Process dead letters** - Don't ignore them; log, alert, or reprocess

## What's next?

In the next lesson, you'll learn about clustering RabbitMQ for high availability.

---

[← Previous: Reliability](./01_reliability.md) | [Back to Module 4](./README.md) | [Next: Clustering →](./03_clustering.md)
