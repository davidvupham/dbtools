# Routing

In this lesson, you learn to implement the Routing pattern - selectively delivering messages to specific queues based on criteria.

## The pattern

**Routing** uses direct exchanges to deliver messages to specific queues based on exact routing key matches. Unlike fanout (all queues) or work queues (one queue), routing sends to selected queues.

```
                              ┌─────────────────────────────┐
routing_key='error' ─────────▶│ binding='error' → Queue A  │
                              ├─────────────────────────────┤
routing_key='info'  ─────────▶│ binding='info'  → Queue B  │
                              ├─────────────────────────────┤
routing_key='error' ─────────▶│ binding='error' → Queue C  │
                              └─────────────────────────────┘
                              (Direct Exchange)
```

**Key characteristics:**
- Direct exchange with explicit bindings
- Messages go to queues with matching binding keys
- Multiple queues can bind to the same key
- One queue can bind to multiple keys

## When to use routing

- **Log levels** - Route errors to one queue, info to another
- **Priority handling** - High priority to fast queue, low to slow queue
- **Geographic routing** - Route by region (us-west, eu-central)
- **Service routing** - Different handlers for different message types

## Basic implementation

### Publisher: emit_log_direct.py

```python
#!/usr/bin/env python
"""
emit_log_direct.py - Publishes logs with severity levels.

Usage: python emit_log_direct.py [severity] [message]
       python emit_log_direct.py error "Database connection failed"
       python emit_log_direct.py info "User logged in"
"""
import sys
import pika


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost')
    )
    channel = connection.channel()

    # Declare a direct exchange
    channel.exchange_declare(
        exchange='direct_logs',
        exchange_type='direct'
    )

    severity = sys.argv[1] if len(sys.argv) > 1 else 'info'
    message = ' '.join(sys.argv[2:]) or 'Hello World!'

    # Routing key determines which queues receive the message
    channel.basic_publish(
        exchange='direct_logs',
        routing_key=severity,
        body=message
    )

    print(f" [x] Sent {severity}:'{message}'")
    connection.close()


if __name__ == '__main__':
    main()
```

### Subscriber: receive_logs_direct.py

```python
#!/usr/bin/env python
"""
receive_logs_direct.py - Receives logs for specific severities.

Usage: python receive_logs_direct.py [severities...]
       python receive_logs_direct.py error warning
       python receive_logs_direct.py info
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
        exchange='direct_logs',
        exchange_type='direct'
    )

    # Create exclusive queue
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    # Get severities from command line
    severities = sys.argv[1:]
    if not severities:
        sys.stderr.write("Usage: %s [severity]...\n" % sys.argv[0])
        sys.exit(1)

    # Bind to each requested severity
    for severity in severities:
        channel.queue_bind(
            exchange='direct_logs',
            queue=queue_name,
            routing_key=severity
        )
        print(f" [*] Bound to severity: {severity}")

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

### Terminal 1: Subscribe to errors only

```bash
python receive_logs_direct.py error
# [*] Bound to severity: error
# [*] Waiting for logs...
```

### Terminal 2: Subscribe to errors and warnings

```bash
python receive_logs_direct.py error warning
# [*] Bound to severity: error
# [*] Bound to severity: warning
# [*] Waiting for logs...
```

### Terminal 3: Publish different severities

```bash
python emit_log_direct.py error "Database connection failed"
python emit_log_direct.py warning "High memory usage"
python emit_log_direct.py info "User logged in"
```

### Observe selective delivery

```
# Terminal 1 (errors only)
[x] error:Database connection failed

# Terminal 2 (errors and warnings)
[x] error:Database connection failed
[x] warning:High memory usage

# Note: Neither receives the "info" message
```

## Multiple bindings

### Same queue, multiple keys

One queue can receive multiple routing keys:

```python
# This queue receives both 'error' and 'critical'
channel.queue_bind(exchange='logs', queue='alerts', routing_key='error')
channel.queue_bind(exchange='logs', queue='alerts', routing_key='critical')
```

### Multiple queues, same key

Multiple queues can bind to the same key (like fanout for that key):

```python
# Both queues receive 'error' messages
channel.queue_bind(exchange='logs', queue='disk_storage', routing_key='error')
channel.queue_bind(exchange='logs', queue='email_alerts', routing_key='error')
```

## Real-world example: Order processing

### Publisher: Order service

```python
#!/usr/bin/env python
"""Route orders based on type."""
import json
import pika


class OrderRouter:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost')
        )
        self.channel = self.connection.channel()
        self.channel.exchange_declare(
            exchange='orders',
            exchange_type='direct',
            durable=True
        )

    def route_order(self, order: dict):
        order_type = order.get('type', 'standard')

        self.channel.basic_publish(
            exchange='orders',
            routing_key=order_type,
            body=json.dumps(order),
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type='application/json'
            )
        )
        print(f"Routed {order_type} order: {order['id']}")

    def close(self):
        self.connection.close()


# Usage
router = OrderRouter()
router.route_order({'id': 1, 'type': 'express', 'total': 150.00})
router.route_order({'id': 2, 'type': 'standard', 'total': 25.00})
router.route_order({'id': 3, 'type': 'international', 'total': 500.00})
router.close()
```

### Subscriber: Express orders processor

```python
#!/usr/bin/env python
"""Process only express orders."""
import json
import pika


def process_express(order: dict):
    print(f"[EXPRESS] Processing order {order['id']} - Total: ${order['total']}")
    print("[EXPRESS] Prioritizing for same-day shipping")


def callback(ch, method, properties, body):
    order = json.loads(body)
    process_express(order)
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost')
    )
    channel = connection.channel()

    channel.exchange_declare(exchange='orders', exchange_type='direct', durable=True)
    channel.queue_declare(queue='express_orders', durable=True)
    channel.queue_bind(exchange='orders', queue='express_orders', routing_key='express')

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue='express_orders',
        on_message_callback=callback,
        auto_ack=False
    )

    print('[Express Handler] Ready')
    channel.start_consuming()


if __name__ == '__main__':
    main()
```

### Subscriber: International orders processor

```python
#!/usr/bin/env python
"""Process international orders with customs handling."""
import json
import pika


def process_international(order: dict):
    print(f"[INTL] Processing order {order['id']} - Total: ${order['total']}")
    print("[INTL] Generating customs documentation")


def callback(ch, method, properties, body):
    order = json.loads(body)
    process_international(order)
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost')
    )
    channel = connection.channel()

    channel.exchange_declare(exchange='orders', exchange_type='direct', durable=True)
    channel.queue_declare(queue='international_orders', durable=True)
    channel.queue_bind(
        exchange='orders',
        queue='international_orders',
        routing_key='international'
    )

    channel.basic_consume(
        queue='international_orders',
        on_message_callback=callback,
        auto_ack=False
    )

    print('[International Handler] Ready')
    channel.start_consuming()


if __name__ == '__main__':
    main()
```

## Routing vs other patterns

| Aspect | Routing (Direct) | Work Queues | Pub/Sub (Fanout) |
|:---|:---|:---|:---|
| Exchange | Direct | Default (direct) | Fanout |
| Queues | Multiple, selected | One shared | Multiple, all |
| Delivery | To matching queues | To one consumer | To all queues |
| Routing key | Exact match | Queue name | Ignored |

## Common routing patterns

### Priority routing

```python
# High priority queue (fast workers)
channel.queue_bind(exchange='tasks', queue='high_priority', routing_key='high')

# Low priority queue (batch workers)
channel.queue_bind(exchange='tasks', queue='low_priority', routing_key='low')

# Publish based on priority
priority = 'high' if order['value'] > 1000 else 'low'
channel.basic_publish(exchange='tasks', routing_key=priority, body=msg)
```

### Geographic routing

```python
# Regional queues
channel.queue_bind(exchange='requests', queue='us_west', routing_key='us-west')
channel.queue_bind(exchange='requests', queue='eu_central', routing_key='eu-central')
channel.queue_bind(exchange='requests', queue='ap_south', routing_key='ap-south')

# Route based on user region
channel.basic_publish(exchange='requests', routing_key=user['region'], body=msg)
```

### Service routing

```python
# Different services handle different message types
channel.queue_bind(exchange='messages', queue='email_queue', routing_key='email')
channel.queue_bind(exchange='messages', queue='sms_queue', routing_key='sms')
channel.queue_bind(exchange='messages', queue='push_queue', routing_key='push')

# Route based on notification type
channel.basic_publish(exchange='messages', routing_key='email', body=msg)
```

## When routing isn't enough

Direct routing requires exact matches. When you need:

- **Pattern matching** → Use Topic exchanges (next lesson)
- **Header-based routing** → Use Headers exchanges
- **Content-based routing** → Use application logic or plugins

## Key takeaways

1. **Direct exchanges route by exact key match** - No patterns, just exact strings
2. **Multiple bindings enable flexible routing** - One queue, many keys or one key, many queues
3. **Routing key must match binding key exactly** - Case-sensitive string comparison
4. **Use for categorical routing** - Log levels, priorities, regions, types
5. **More flexible than work queues** - But less flexible than topics

## What's next?

In the next lesson, you'll learn the Topics pattern for flexible pattern-based routing.

---

[← Previous: Publish/Subscribe](./02_publish_subscribe.md) | [Back to Module 3](./README.md) | [Next: Topics →](./04_topics.md)
