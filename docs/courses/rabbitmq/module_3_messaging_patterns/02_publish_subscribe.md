# Publish/Subscribe

In this lesson, you learn to implement the Publish/Subscribe (Pub/Sub) pattern - broadcasting messages to multiple consumers simultaneously.

## The pattern

**Publish/Subscribe** delivers each message to ALL subscribed consumers. This differs from work queues where each message goes to one consumer.

```
                           ┌──────────────────────┐
                      ┌───▶│ Queue A → Consumer 1 │
                      │    └──────────────────────┘
┌──────────┐    ┌─────┴────┐
│ Producer │───▶│  Fanout  │ All consumers get every message
└──────────┘    │ Exchange │
                └─────┬────┘
                      │    ┌──────────────────────┐
                      └───▶│ Queue B → Consumer 2 │
                           └──────────────────────┘
```

**Key characteristics:**
- One message is delivered to ALL bound queues
- Each consumer has its own queue
- Routing key is ignored (fanout exchange)
- New subscribers immediately start receiving messages

## When to use pub/sub

- **Notifications** - Alert multiple systems about events
- **Cache invalidation** - Clear caches across all servers
- **Real-time updates** - Push updates to multiple clients
- **Event broadcasting** - Announce events to interested services
- **Logging** - Send logs to multiple destinations

## Basic implementation

### Publisher: emit_log.py

```python
#!/usr/bin/env python
"""
emit_log.py - Publishes logs to all subscribers.

Usage: python emit_log.py "Log message here"
"""
import sys
import pika


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost')
    )
    channel = connection.channel()

    # Declare a fanout exchange
    channel.exchange_declare(
        exchange='logs',
        exchange_type='fanout'
    )

    message = ' '.join(sys.argv[1:]) or 'Hello World!'

    # Publish to the exchange (routing_key ignored for fanout)
    channel.basic_publish(
        exchange='logs',
        routing_key='',  # Ignored for fanout
        body=message
    )

    print(f" [x] Sent '{message}'")
    connection.close()


if __name__ == '__main__':
    main()
```

### Subscriber: receive_logs.py

```python
#!/usr/bin/env python
"""
receive_logs.py - Receives logs from the fanout exchange.

Each subscriber gets its own temporary queue.
"""
import pika


def callback(ch, method, properties, body):
    print(f" [x] {body.decode()}")


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost')
    )
    channel = connection.channel()

    # Declare the same fanout exchange
    channel.exchange_declare(
        exchange='logs',
        exchange_type='fanout'
    )

    # Create a temporary, exclusive queue
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    # Bind the queue to the exchange
    channel.queue_bind(
        exchange='logs',
        queue=queue_name
    )

    print(' [*] Waiting for logs. To exit press CTRL+C')

    channel.basic_consume(
        queue=queue_name,
        on_message_callback=callback,
        auto_ack=True
    )

    channel.start_consuming()


if __name__ == '__main__':
    main()
```

## Testing the pattern

### Terminal 1 & 2: Start subscribers

```bash
# Terminal 1
python receive_logs.py
# [*] Waiting for logs...

# Terminal 2
python receive_logs.py
# [*] Waiting for logs...
```

### Terminal 3: Publish messages

```bash
python emit_log.py "Server started"
python emit_log.py "User logged in"
python emit_log.py "Error occurred"
```

### Observe: Both terminals receive ALL messages

```
# Terminal 1
[x] Server started
[x] User logged in
[x] Error occurred

# Terminal 2
[x] Server started
[x] User logged in
[x] Error occurred
```

## Temporary vs durable queues

### Temporary queues (typical for pub/sub)

```python
# Auto-generated name, exclusive, auto-delete
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue
# e.g., 'amq.gen-JzTY20BRgKO-HjmUJj0wLg'
```

- Deleted when connection closes
- No messages persist
- Perfect for live subscribers

### Durable queues (persistent subscribers)

```python
# Named, durable, will accumulate messages when offline
channel.queue_declare(queue='email_service_logs', durable=True)
channel.queue_bind(exchange='logs', queue='email_service_logs')
```

- Survives reconnections
- Messages queue up when subscriber offline
- Use for critical subscribers that must not miss messages

## Exchange durability

```python
# Durable exchange - survives broker restart
channel.exchange_declare(
    exchange='logs',
    exchange_type='fanout',
    durable=True
)

# Transient exchange - lost on restart
channel.exchange_declare(
    exchange='temp_logs',
    exchange_type='fanout',
    durable=False
)
```

## Real-world example: Multi-service notification

### Publisher: Event service

```python
#!/usr/bin/env python
"""Publish events to multiple services."""
import json
import pika
import uuid
from datetime import datetime


class EventPublisher:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost')
        )
        self.channel = self.connection.channel()
        self.channel.exchange_declare(
            exchange='events',
            exchange_type='fanout',
            durable=True
        )

    def publish(self, event_type: str, data: dict):
        event = {
            'id': str(uuid.uuid4()),
            'type': event_type,
            'timestamp': datetime.utcnow().isoformat(),
            'data': data
        }

        self.channel.basic_publish(
            exchange='events',
            routing_key='',
            body=json.dumps(event),
            properties=pika.BasicProperties(
                content_type='application/json',
                delivery_mode=2
            )
        )
        print(f"Published: {event_type}")

    def close(self):
        self.connection.close()


# Usage
publisher = EventPublisher()
publisher.publish('user.created', {'user_id': 123, 'email': 'alice@example.com'})
publisher.publish('order.placed', {'order_id': 456, 'total': 99.99})
publisher.close()
```

### Subscriber: Email service

```python
#!/usr/bin/env python
"""Email service subscribes to all events."""
import json
import pika


def handle_event(event: dict):
    event_type = event['type']

    if event_type == 'user.created':
        print(f"Sending welcome email to {event['data']['email']}")
    elif event_type == 'order.placed':
        print(f"Sending order confirmation for order {event['data']['order_id']}")


def callback(ch, method, properties, body):
    event = json.loads(body)
    print(f"[Email Service] Received: {event['type']}")
    handle_event(event)
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost')
    )
    channel = connection.channel()

    channel.exchange_declare(exchange='events', exchange_type='fanout', durable=True)

    # Durable queue - don't miss messages if service restarts
    channel.queue_declare(queue='email_service', durable=True)
    channel.queue_bind(exchange='events', queue='email_service')

    channel.basic_qos(prefetch_count=10)
    channel.basic_consume(
        queue='email_service',
        on_message_callback=callback,
        auto_ack=False
    )

    print('[Email Service] Ready')
    channel.start_consuming()


if __name__ == '__main__':
    main()
```

### Subscriber: Analytics service

```python
#!/usr/bin/env python
"""Analytics service subscribes to all events."""
import json
import pika


def callback(ch, method, properties, body):
    event = json.loads(body)
    print(f"[Analytics] Recording: {event['type']} at {event['timestamp']}")
    # Store in analytics database
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost')
    )
    channel = connection.channel()

    channel.exchange_declare(exchange='events', exchange_type='fanout', durable=True)

    channel.queue_declare(queue='analytics_service', durable=True)
    channel.queue_bind(exchange='events', queue='analytics_service')

    channel.basic_consume(
        queue='analytics_service',
        on_message_callback=callback,
        auto_ack=False
    )

    print('[Analytics Service] Ready')
    channel.start_consuming()


if __name__ == '__main__':
    main()
```

## Pub/sub with filtering

Sometimes you want pub/sub but with filtering. Use topic exchange instead:

```python
# Publisher
channel.exchange_declare(exchange='events', exchange_type='topic')
channel.basic_publish(exchange='events', routing_key='user.created', body=msg)
channel.basic_publish(exchange='events', routing_key='order.placed', body=msg)

# Subscriber 1: Only user events
channel.queue_bind(exchange='events', queue='user_service', routing_key='user.*')

# Subscriber 2: All events (like fanout)
channel.queue_bind(exchange='events', queue='audit_service', routing_key='#')
```

## Handling late subscribers

Messages published before a subscriber connects are lost (for temporary queues).

### Solution 1: Durable queues

```python
# Subscriber uses a durable, named queue
channel.queue_declare(queue='my_service_events', durable=True)
```

### Solution 2: Message replay service

Store recent messages and replay on request:

```python
class ReplayService:
    def __init__(self, max_messages=1000):
        self.messages = []
        self.max_messages = max_messages

    def store(self, message):
        self.messages.append(message)
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)

    def replay_since(self, timestamp):
        return [m for m in self.messages if m['timestamp'] > timestamp]
```

## Scaling considerations

### Too many subscribers

Each message is copied to each queue. With many subscribers:

```
1 message × 1000 subscribers = 1000 message copies
```

**Solutions:**
- Use topic exchange with specific bindings
- Implement fan-out at application level
- Consider streaming solutions for high-scale

### Slow subscribers

One slow subscriber doesn't affect others (they have separate queues).

```
Fast subscriber: [msg1] [msg2] [msg3] [done]
Slow subscriber: [msg1...] queue builds up: [msg2] [msg3] [msg4]...
```

**Solutions:**
- Set `x-max-length` on queues
- Monitor queue depth
- Scale slow consumers

## Key takeaways

1. **Fanout exchanges broadcast** - All bound queues receive every message
2. **Each subscriber needs its own queue** - Don't share queues in pub/sub
3. **Temporary queues for live subscribers** - Auto-deleted on disconnect
4. **Durable queues for persistent subscribers** - Don't miss messages
5. **Routing key is ignored** - Fanout doesn't look at it
6. **Use topic exchange for filtered pub/sub** - When you need selective delivery

## What's next?

In the next lesson, you'll learn the Routing pattern for selectively delivering messages based on criteria.

---

[← Previous: Work Queues](./01_work_queues.md) | [Back to Module 3](./README.md) | [Next: Routing →](./03_routing.md)
