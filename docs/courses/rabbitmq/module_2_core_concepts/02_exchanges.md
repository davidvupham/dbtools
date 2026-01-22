# Exchanges

In this lesson, you learn about the four types of exchanges in RabbitMQ and when to use each one.

## What is an exchange?

An **exchange** is a routing agent that receives messages from producers and routes them to queues based on rules called bindings.

```
Producer → Exchange → [Routing Logic] → Queue(s)
```

Key principle: **Producers never send directly to queues.** They send to exchanges, which decide where messages go.

## Exchange types

RabbitMQ supports four exchange types:

| Type | Routing Logic | Use Case |
|:---|:---|:---|
| **Direct** | Exact match on routing key | Task queues, point-to-point |
| **Topic** | Pattern match on routing key | Log routing, event filtering |
| **Fanout** | Broadcast to all bound queues | Notifications, pub/sub |
| **Headers** | Match on message headers | Complex routing rules |

## Direct exchange

A **direct exchange** routes messages to queues with binding keys that exactly match the routing key.

```
                         ┌─────────────────┐
routing_key='error' ────▶│ binding='error' │────▶ Queue: errors
                         ├─────────────────┤
routing_key='info'  ────▶│ binding='info'  │────▶ Queue: info_logs
                         ├─────────────────┤
routing_key='error' ────▶│ binding='error' │────▶ Queue: all_logs
                         └─────────────────┘
```

### Example: Log levels

```python
import pika

connection = pika.BlockingConnection()
channel = connection.channel()

# Declare a direct exchange
channel.exchange_declare(
    exchange='logs_direct',
    exchange_type='direct',
    durable=True
)

# Declare queues
channel.queue_declare(queue='errors', durable=True)
channel.queue_declare(queue='warnings', durable=True)
channel.queue_declare(queue='all_logs', durable=True)

# Bind queues with routing keys
channel.queue_bind(exchange='logs_direct', queue='errors', routing_key='error')
channel.queue_bind(exchange='logs_direct', queue='warnings', routing_key='warning')
channel.queue_bind(exchange='logs_direct', queue='all_logs', routing_key='error')
channel.queue_bind(exchange='logs_direct', queue='all_logs', routing_key='warning')
channel.queue_bind(exchange='logs_direct', queue='all_logs', routing_key='info')

# Publish messages
channel.basic_publish(
    exchange='logs_direct',
    routing_key='error',
    body='Database connection failed'
)
# Goes to: errors, all_logs

channel.basic_publish(
    exchange='logs_direct',
    routing_key='info',
    body='User logged in'
)
# Goes to: all_logs only

connection.close()
```

### When to use direct exchange

- Task distribution to specific workers
- Routing by severity or category
- Simple one-to-one or one-to-few routing
- When routing key is known at publish time

## Topic exchange

A **topic exchange** routes messages using pattern matching on the routing key. Routing keys must be dot-separated words.

Pattern wildcards:
- `*` (star) - matches exactly one word
- `#` (hash) - matches zero or more words

```
                              ┌────────────────────────┐
routing_key='order.created' ─▶│ binding='order.*'     │─▶ Queue: order_events
                              ├────────────────────────┤
routing_key='order.shipped' ─▶│ binding='order.*'     │─▶ Queue: order_events
                              ├────────────────────────┤
routing_key='user.created'  ─▶│ binding='*.created'   │─▶ Queue: created_events
                              ├────────────────────────┤
routing_key='order.created' ─▶│ binding='*.created'   │─▶ Queue: created_events
                              ├────────────────────────┤
routing_key='audit.user.login'│ binding='audit.#'     │─▶ Queue: audit_log
                              └────────────────────────┘
```

### Example: Event routing

```python
import pika

connection = pika.BlockingConnection()
channel = connection.channel()

# Declare a topic exchange
channel.exchange_declare(
    exchange='events',
    exchange_type='topic',
    durable=True
)

# Declare queues
channel.queue_declare(queue='order_service', durable=True)
channel.queue_declare(queue='notification_service', durable=True)
channel.queue_declare(queue='audit_service', durable=True)

# Bind with patterns
channel.queue_bind(
    exchange='events',
    queue='order_service',
    routing_key='order.*'  # order.created, order.updated, order.cancelled
)

channel.queue_bind(
    exchange='events',
    queue='notification_service',
    routing_key='*.created'  # order.created, user.created
)

channel.queue_bind(
    exchange='events',
    queue='audit_service',
    routing_key='#'  # Everything (catch-all)
)

# Publish events
channel.basic_publish(
    exchange='events',
    routing_key='order.created',
    body='{"order_id": 123}'
)
# Goes to: order_service, notification_service, audit_service

channel.basic_publish(
    exchange='events',
    routing_key='user.login',
    body='{"user_id": 456}'
)
# Goes to: audit_service only

connection.close()
```

### Topic pattern examples

| Pattern | Matches | Doesn't Match |
|:---|:---|:---|
| `order.*` | `order.created`, `order.shipped` | `order.item.added` |
| `order.#` | `order.created`, `order.item.added` | `user.created` |
| `*.*.critical` | `app.db.critical`, `api.auth.critical` | `critical`, `app.critical` |
| `#.error` | `error`, `app.error`, `app.db.error` | `error.log` |

### When to use topic exchange

- Event-driven architectures
- Log aggregation with filtering
- Pub/sub with selective subscriptions
- When subscribers need flexible filtering

## Fanout exchange

A **fanout exchange** broadcasts messages to all bound queues, ignoring the routing key.

```
                        ┌─────────────────┐
                   ┌───▶│ Queue: service1 │
                   │    └─────────────────┘
┌─────────┐        │    ┌─────────────────┐
│ Fanout  │────────┼───▶│ Queue: service2 │
│Exchange │        │    └─────────────────┘
└─────────┘        │    ┌─────────────────┐
                   └───▶│ Queue: service3 │
                        └─────────────────┘
```

### Example: Notifications

```python
import pika

connection = pika.BlockingConnection()
channel = connection.channel()

# Declare a fanout exchange
channel.exchange_declare(
    exchange='notifications',
    exchange_type='fanout',
    durable=True
)

# Each service has its own queue
for service in ['email', 'sms', 'push', 'slack']:
    queue_name = f'{service}_notifications'
    channel.queue_declare(queue=queue_name, durable=True)
    channel.queue_bind(
        exchange='notifications',
        queue=queue_name
        # No routing_key needed for fanout
    )

# Publish a notification (goes to ALL queues)
channel.basic_publish(
    exchange='notifications',
    routing_key='',  # Ignored for fanout
    body='{"event": "system_alert", "message": "Server is down!"}'
)

connection.close()
```

### When to use fanout exchange

- Broadcasting to all subscribers
- Cache invalidation across services
- Real-time updates (sports scores, stock prices)
- When all consumers need every message

## Headers exchange

A **headers exchange** routes based on message header attributes rather than routing key.

```python
import pika

connection = pika.BlockingConnection()
channel = connection.channel()

# Declare a headers exchange
channel.exchange_declare(
    exchange='reports',
    exchange_type='headers',
    durable=True
)

# Bind with header matching
channel.queue_declare(queue='pdf_reports', durable=True)
channel.queue_bind(
    exchange='reports',
    queue='pdf_reports',
    arguments={
        'x-match': 'all',  # 'all' = AND, 'any' = OR
        'format': 'pdf',
        'department': 'finance'
    }
)

channel.queue_declare(queue='all_finance', durable=True)
channel.queue_bind(
    exchange='reports',
    queue='all_finance',
    arguments={
        'x-match': 'any',
        'department': 'finance'
    }
)

# Publish with headers
channel.basic_publish(
    exchange='reports',
    routing_key='',  # Ignored
    body='report data',
    properties=pika.BasicProperties(
        headers={
            'format': 'pdf',
            'department': 'finance'
        }
    )
)
# Goes to: pdf_reports (all match), all_finance (any match)

connection.close()
```

### When to use headers exchange

- Complex routing rules not expressible in routing keys
- Multi-attribute filtering
- When routing key structure is limiting
- Metadata-based routing

## Exchange comparison

| Feature | Direct | Topic | Fanout | Headers |
|:---|:---|:---|:---|:---|
| Routing logic | Exact match | Pattern match | Broadcast | Header match |
| Routing key | Required | Required (dotted) | Ignored | Ignored |
| Flexibility | Low | High | None | Highest |
| Performance | Fastest | Fast | Fast | Slowest |
| Use case | Tasks | Events | Notifications | Complex rules |

## Declaring exchanges

### Basic declaration

```python
channel.exchange_declare(
    exchange='my_exchange',
    exchange_type='direct'
)
```

### With durability

```python
channel.exchange_declare(
    exchange='my_exchange',
    exchange_type='direct',
    durable=True  # Survives broker restart
)
```

### Passive declaration (check exists)

```python
try:
    channel.exchange_declare(
        exchange='my_exchange',
        passive=True  # Just check, don't create
    )
    print("Exchange exists")
except pika.exceptions.ChannelClosedByBroker:
    print("Exchange does not exist")
```

### Auto-delete exchange

```python
channel.exchange_declare(
    exchange='temp_exchange',
    exchange_type='fanout',
    auto_delete=True  # Deleted when last binding removed
)
```

## Pre-declared exchanges

RabbitMQ provides several pre-declared exchanges:

| Exchange | Type | Purpose |
|:---|:---|:---|
| `(AMQP default)` | direct | Route by queue name (empty string) |
| `amq.direct` | direct | General direct routing |
| `amq.fanout` | fanout | General broadcasting |
| `amq.topic` | topic | General topic routing |
| `amq.headers` | headers | General header routing |
| `amq.match` | headers | Alias for amq.headers |

These are automatically available; you don't need to declare them.

## Key takeaways

1. **Direct** - Use for exact routing key matching
2. **Topic** - Use for flexible pattern-based routing
3. **Fanout** - Use for broadcasting to all queues
4. **Headers** - Use for complex multi-attribute routing
5. **Exchanges don't store messages** - They only route
6. **Durable exchanges survive restarts** - But messages need persistent mode too

## What's next?

In the next lesson, you'll learn about queues - their properties, types, and configuration options.

---

[← Previous: AMQP Model](./01_amqp_model.md) | [Back to Module 2](./README.md) | [Next: Queues →](./03_queues.md)
