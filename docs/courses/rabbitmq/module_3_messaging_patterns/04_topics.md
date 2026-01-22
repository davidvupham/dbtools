# Topics

In this lesson, you learn to implement the Topics pattern - flexible routing using pattern matching on routing keys.

## The pattern

**Topic exchanges** route messages using pattern matching on dot-separated routing keys. This combines the selectivity of direct routing with the flexibility of wildcards.

```
routing_key='order.created.us' ──▶ binding='order.*.us' → Queue A ✓
routing_key='order.created.eu' ──▶ binding='order.*.us' → Queue A ✗
routing_key='order.cancelled.us' ▶ binding='order.#'    → Queue B ✓
routing_key='user.created'     ──▶ binding='*.created'  → Queue C ✓
```

**Wildcards:**
- `*` (star) - matches exactly **one** word
- `#` (hash) - matches **zero or more** words

## When to use topics

- **Log routing** - Filter by source, level, and component
- **Event streams** - Subscribe to specific event types
- **Multi-tenant systems** - Route by tenant and action
- **Geographic + service routing** - Combine multiple criteria

## Routing key structure

Topic routing keys must be **dot-separated words**:

```
<word>.<word>.<word>...

Examples:
- order.created.us
- user.profile.updated
- log.api.auth.error
- stock.nyse.goog.price
```

## Pattern matching rules

| Pattern | Matches | Doesn't Match |
|:---|:---|:---|
| `order.*` | `order.created`, `order.shipped` | `order.item.added` |
| `order.#` | `order`, `order.created`, `order.item.added` | `user.created` |
| `*.created` | `order.created`, `user.created` | `order.item.created` |
| `#.error` | `error`, `api.error`, `api.auth.error` | `error.log` |
| `*.*.error` | `api.auth.error`, `app.db.error` | `error`, `api.error` |

## Basic implementation

### Publisher: emit_log_topic.py

```python
#!/usr/bin/env python
"""
emit_log_topic.py - Publishes logs with structured routing keys.

Usage: python emit_log_topic.py <routing_key> <message>
       python emit_log_topic.py api.auth.error "Invalid token"
       python emit_log_topic.py db.query.warning "Slow query detected"
"""
import sys
import pika


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost')
    )
    channel = connection.channel()

    channel.exchange_declare(
        exchange='topic_logs',
        exchange_type='topic'
    )

    routing_key = sys.argv[1] if len(sys.argv) > 1 else 'anonymous.info'
    message = ' '.join(sys.argv[2:]) or 'Hello World!'

    channel.basic_publish(
        exchange='topic_logs',
        routing_key=routing_key,
        body=message
    )

    print(f" [x] Sent {routing_key}:'{message}'")
    connection.close()


if __name__ == '__main__':
    main()
```

### Subscriber: receive_logs_topic.py

```python
#!/usr/bin/env python
"""
receive_logs_topic.py - Receives logs matching topic patterns.

Usage: python receive_logs_topic.py <pattern> [pattern...]
       python receive_logs_topic.py "#"           (all logs)
       python receive_logs_topic.py "*.error"     (all errors)
       python receive_logs_topic.py "api.#"       (all API logs)
       python receive_logs_topic.py "api.auth.*"  (API auth logs)
"""
import sys
import pika


def callback(ch, method, properties, body):
    print(f" [x] {method.routing_key}:{body.decode()}")


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost')
    )
    channel = connection.channel()

    channel.exchange_declare(
        exchange='topic_logs',
        exchange_type='topic'
    )

    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    patterns = sys.argv[1:]
    if not patterns:
        sys.stderr.write("Usage: %s <pattern> [pattern]...\n" % sys.argv[0])
        sys.exit(1)

    for pattern in patterns:
        channel.queue_bind(
            exchange='topic_logs',
            queue=queue_name,
            routing_key=pattern
        )
        print(f" [*] Bound to pattern: {pattern}")

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

### Terminal 1: All errors

```bash
python receive_logs_topic.py "*.*.error" "#.error"
# Receives: api.auth.error, db.query.error, error
```

### Terminal 2: All API logs

```bash
python receive_logs_topic.py "api.#"
# Receives: api.auth.error, api.request.info, api.response.warning
```

### Terminal 3: Everything (catch-all)

```bash
python receive_logs_topic.py "#"
# Receives: all messages
```

### Terminal 4: Publish various logs

```bash
python emit_log_topic.py api.auth.error "Invalid token"
python emit_log_topic.py api.request.info "GET /users"
python emit_log_topic.py db.query.warning "Slow query"
python emit_log_topic.py app.startup.info "Server started"
```

## Real-world example: Event-driven architecture

### Event publisher

```python
#!/usr/bin/env python
"""Publish domain events with structured routing keys."""
import json
import pika
from datetime import datetime
from typing import Any


class EventPublisher:
    """
    Publishes events with routing key format:
    <domain>.<entity>.<action>

    Examples:
    - order.order.created
    - user.profile.updated
    - inventory.item.low_stock
    """

    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost')
        )
        self.channel = self.connection.channel()
        self.channel.exchange_declare(
            exchange='domain_events',
            exchange_type='topic',
            durable=True
        )

    def publish(self, domain: str, entity: str, action: str, data: dict):
        routing_key = f"{domain}.{entity}.{action}"

        event = {
            'routing_key': routing_key,
            'timestamp': datetime.utcnow().isoformat(),
            'data': data
        }

        self.channel.basic_publish(
            exchange='domain_events',
            routing_key=routing_key,
            body=json.dumps(event),
            properties=pika.BasicProperties(
                content_type='application/json',
                delivery_mode=2
            )
        )
        print(f"Published: {routing_key}")

    def close(self):
        self.connection.close()


# Usage
pub = EventPublisher()
pub.publish('order', 'order', 'created', {'order_id': 1, 'total': 99.99})
pub.publish('order', 'order', 'shipped', {'order_id': 1, 'tracking': 'ABC123'})
pub.publish('user', 'profile', 'updated', {'user_id': 42, 'field': 'email'})
pub.publish('inventory', 'item', 'low_stock', {'sku': 'WIDGET-01', 'quantity': 5})
pub.close()
```

### Order service subscriber

```python
#!/usr/bin/env python
"""Order service subscribes to order-related events."""
import json
import pika


def handle_event(routing_key: str, data: dict):
    print(f"[Order Service] {routing_key}: {data}")


def callback(ch, method, properties, body):
    event = json.loads(body)
    handle_event(method.routing_key, event['data'])
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost')
    )
    channel = connection.channel()

    channel.exchange_declare(
        exchange='domain_events',
        exchange_type='topic',
        durable=True
    )

    channel.queue_declare(queue='order_service', durable=True)

    # Subscribe to all order events
    channel.queue_bind(
        exchange='domain_events',
        queue='order_service',
        routing_key='order.#'  # order.order.created, order.order.shipped, etc.
    )

    channel.basic_consume(
        queue='order_service',
        on_message_callback=callback,
        auto_ack=False
    )

    print('[Order Service] Listening for order.# events')
    channel.start_consuming()


if __name__ == '__main__':
    main()
```

### Notification service subscriber

```python
#!/usr/bin/env python
"""Notification service listens to events that need user notification."""
import json
import pika


def send_notification(event_type: str, data: dict):
    print(f"[Notification] Sending alert for: {event_type}")


def callback(ch, method, properties, body):
    event = json.loads(body)
    send_notification(method.routing_key, event['data'])
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost')
    )
    channel = connection.channel()

    channel.exchange_declare(
        exchange='domain_events',
        exchange_type='topic',
        durable=True
    )

    channel.queue_declare(queue='notification_service', durable=True)

    # Subscribe to specific events that need notifications
    patterns = [
        'order.order.created',    # New order notification
        'order.order.shipped',    # Shipping notification
        '*.*.low_stock',          # Low stock alerts
        'user.*.created',         # Welcome notifications
    ]

    for pattern in patterns:
        channel.queue_bind(
            exchange='domain_events',
            queue='notification_service',
            routing_key=pattern
        )
        print(f"[Notification] Bound to: {pattern}")

    channel.basic_consume(
        queue='notification_service',
        on_message_callback=callback,
        auto_ack=False
    )

    print('[Notification Service] Ready')
    channel.start_consuming()


if __name__ == '__main__':
    main()
```

## Pattern design guidelines

### Good routing key structures

```
# Three-level hierarchy
<domain>.<entity>.<action>
order.order.created
user.profile.updated
payment.transaction.completed

# With environment
<env>.<domain>.<entity>.<action>
prod.order.order.created
staging.user.profile.updated

# With region
<region>.<domain>.<action>
us-west.order.created
eu-central.payment.processed
```

### Avoid these patterns

```
# Too flat - no filtering possible
order_created
user_updated

# Too deep - hard to match
app.module.submodule.component.action.status.code

# Inconsistent structure
order.created      # 2 levels
user.profile.updated  # 3 levels
```

## Topic vs direct exchange

| Aspect | Topic | Direct |
|:---|:---|:---|
| Routing | Pattern matching | Exact match |
| Flexibility | High | Low |
| Performance | Slightly slower | Fastest |
| Use case | Complex filtering | Simple routing |
| Routing key | Dot-separated words | Any string |

## Special cases

### Emulating fanout

```python
# '#' matches everything
channel.queue_bind(exchange='events', queue='all_events', routing_key='#')
```

### Emulating direct

```python
# No wildcards = exact match
channel.queue_bind(exchange='events', queue='orders', routing_key='order.created')
```

## Key takeaways

1. **Topic exchanges enable pattern matching** - Use `*` and `#` wildcards
2. **Routing keys should be dot-separated** - Design a consistent structure
3. **`*` matches exactly one word** - `order.*` matches `order.created`, not `order`
4. **`#` matches zero or more words** - `order.#` matches `order`, `order.created`, `order.a.b.c`
5. **Combine patterns for flexible subscriptions** - Bind multiple patterns to one queue
6. **`#` as catch-all** - Use sparingly for debugging or audit logs

## What's next?

In the next lesson, you'll learn the RPC (Remote Procedure Call) pattern for request/response communication.

---

[← Previous: Routing](./03_routing.md) | [Back to Module 3](./README.md) | [Next: RPC →](./05_rpc.md)
