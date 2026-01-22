# Bindings

In this lesson, you learn about bindings - the rules that connect exchanges to queues and determine how messages are routed.

## What is a binding?

A **binding** is a relationship between an exchange and a queue that defines routing rules. It's essentially a rule that says "messages matching X should go to queue Y."

```
┌──────────┐     Binding      ┌─────────┐
│ Exchange │ ═══════════════▶ │  Queue  │
└──────────┘  routing_key     └─────────┘
```

## Creating bindings

### Basic binding

```python
# First, ensure exchange and queue exist
channel.exchange_declare(exchange='orders', exchange_type='direct')
channel.queue_declare(queue='order_processing')

# Create the binding
channel.queue_bind(
    exchange='orders',
    queue='order_processing',
    routing_key='new_order'
)
```

### Multiple bindings to one queue

A queue can receive messages from multiple routing keys:

```python
channel.queue_bind(exchange='logs', queue='all_logs', routing_key='error')
channel.queue_bind(exchange='logs', queue='all_logs', routing_key='warning')
channel.queue_bind(exchange='logs', queue='all_logs', routing_key='info')
```

### Multiple queues with same binding

Multiple queues can bind with the same routing key:

```python
channel.queue_bind(exchange='orders', queue='processing', routing_key='new')
channel.queue_bind(exchange='orders', queue='analytics', routing_key='new')
channel.queue_bind(exchange='orders', queue='audit', routing_key='new')
# Message with routing_key='new' goes to ALL three queues
```

## Binding keys vs routing keys

These terms are often confused:

| Term | Where Used | Purpose |
|:---|:---|:---|
| **Routing Key** | Message property | Attached when publishing |
| **Binding Key** | Binding property | Pattern to match against |

```python
# Binding key: 'order.created' (on the binding)
channel.queue_bind(
    exchange='events',
    queue='order_queue',
    routing_key='order.created'  # This is the BINDING key
)

# Routing key: 'order.created' (on the message)
channel.basic_publish(
    exchange='events',
    routing_key='order.created',  # This is the ROUTING key
    body='...'
)
# Match! Message goes to order_queue
```

## Binding with different exchange types

### Direct exchange bindings

Exact match between routing key and binding key:

```python
channel.exchange_declare(exchange='tasks', exchange_type='direct')

# Binding with exact key
channel.queue_bind(
    exchange='tasks',
    queue='high_priority',
    routing_key='urgent'
)

# Only messages with routing_key='urgent' match
channel.basic_publish(exchange='tasks', routing_key='urgent', body='...')  # Matches
channel.basic_publish(exchange='tasks', routing_key='normal', body='...')  # No match
```

### Topic exchange bindings

Pattern matching with wildcards:

```python
channel.exchange_declare(exchange='events', exchange_type='topic')

# Pattern bindings
channel.queue_bind(exchange='events', queue='all_orders', routing_key='order.#')
channel.queue_bind(exchange='events', queue='creations', routing_key='*.created')
channel.queue_bind(exchange='events', queue='everything', routing_key='#')

# Publishing
channel.basic_publish(exchange='events', routing_key='order.created', body='...')
# Matches: all_orders (order.#), creations (*.created), everything (#)

channel.basic_publish(exchange='events', routing_key='user.created', body='...')
# Matches: creations (*.created), everything (#)

channel.basic_publish(exchange='events', routing_key='order.item.added', body='...')
# Matches: all_orders (order.#), everything (#)
```

### Fanout exchange bindings

Routing key is ignored; all bound queues receive messages:

```python
channel.exchange_declare(exchange='broadcast', exchange_type='fanout')

# Routing key in binding is ignored but conventionally left empty
channel.queue_bind(exchange='broadcast', queue='service_a')
channel.queue_bind(exchange='broadcast', queue='service_b')
channel.queue_bind(exchange='broadcast', queue='service_c')

# All queues receive this message regardless of routing key
channel.basic_publish(exchange='broadcast', routing_key='anything', body='...')
```

### Headers exchange bindings

Match based on message headers:

```python
channel.exchange_declare(exchange='headers_ex', exchange_type='headers')

# Binding with header requirements
channel.queue_bind(
    exchange='headers_ex',
    queue='pdf_queue',
    arguments={
        'x-match': 'all',  # All headers must match
        'format': 'pdf',
        'size': 'large'
    }
)

channel.queue_bind(
    exchange='headers_ex',
    queue='any_format',
    arguments={
        'x-match': 'any',  # Any header can match
        'format': 'pdf',
        'format': 'csv'
    }
)
```

## Topic pattern reference

For topic exchanges, routing keys must be dot-separated words:

### Valid routing keys

```
order.created
user.profile.updated
stock.nyse.goog
log.app.api.error
```

### Pattern wildcards

| Pattern | Description | Examples |
|:---|:---|:---|
| `*` | Matches exactly one word | `order.*` matches `order.created`, not `order.item.added` |
| `#` | Matches zero or more words | `order.#` matches `order`, `order.created`, `order.item.added` |

### Pattern examples

```
┌─────────────────┬─────────────────────────────────────────────────┐
│ Pattern         │ Matches                                         │
├─────────────────┼─────────────────────────────────────────────────┤
│ *.orange.*      │ quick.orange.rabbit, lazy.orange.elephant       │
│ lazy.#          │ lazy, lazy.brown.fox, lazy.pink.rabbit          │
│ #.rabbit        │ rabbit, quick.rabbit, slow.white.rabbit         │
│ *.*.*           │ exactly 3 words: a.b.c, quick.brown.fox         │
│ #               │ everything (catch-all)                          │
│ *.*.critical    │ app.db.critical, api.auth.critical              │
└─────────────────┴─────────────────────────────────────────────────┘
```

## Managing bindings

### List bindings

Using rabbitmqctl:

```bash
docker exec rabbitmq rabbitmqctl list_bindings source_name destination_name routing_key
```

### Delete a binding

```python
channel.queue_unbind(
    exchange='orders',
    queue='old_processor',
    routing_key='new_order'
)
```

### Check if binding exists

There's no direct API, but you can:

1. Use the Management API
2. Declare the binding (idempotent - won't error if exists)
3. Use `rabbitmqctl list_bindings`

## Exchange-to-exchange bindings

RabbitMQ extends AMQP to allow binding exchanges to other exchanges:

```python
# Declare exchanges
channel.exchange_declare(exchange='source', exchange_type='topic')
channel.exchange_declare(exchange='destination', exchange_type='fanout')

# Bind exchange to exchange
channel.exchange_bind(
    destination='destination',
    source='source',
    routing_key='important.#'
)
```

Use case: Hierarchical routing

```
                      ┌────────────────┐
                      │ Master Exchange│
                      │    (topic)     │
                      └───────┬────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Orders Exchange │ │ Users Exchange  │ │ Logs Exchange   │
│    (fanout)     │ │    (fanout)     │ │    (topic)      │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
    ┌────┴────┐         ┌────┴────┐         ┌────┴────┐
    ▼         ▼         ▼         ▼         ▼         ▼
 Queue A   Queue B   Queue C   Queue D   Queue E   Queue F
```

## Binding durability

Bindings follow the durability of their source and destination:

| Exchange | Queue | Binding |
|:---|:---|:---|
| Durable | Durable | Survives restart |
| Durable | Transient | Lost on restart |
| Transient | Durable | Lost on restart |
| Transient | Transient | Lost on restart |

Both exchange AND queue must be durable for the binding to survive.

## Best practices

### 1. Use meaningful routing keys

```python
# Good: hierarchical and descriptive
routing_key='order.payment.completed'
routing_key='user.profile.updated'

# Bad: flat and unclear
routing_key='order_done'
routing_key='update123'
```

### 2. Plan your routing topology

Before coding, diagram your exchanges, queues, and bindings:

```
events (topic)
├── order.* → order_service
├── payment.* → payment_service
├── *.created → audit_service
└── # → logging_service
```

### 3. Use catch-all for debugging

Temporarily bind with `#` to see all messages:

```python
channel.queue_bind(
    exchange='events',
    queue='debug_queue',
    routing_key='#'
)
```

### 4. Document your bindings

Keep a record of your messaging topology:

```yaml
# messaging-topology.yaml
exchanges:
  - name: events
    type: topic
    bindings:
      - queue: order_service
        routing_key: order.*
      - queue: notification_service
        routing_key: '*.created'
```

## Common patterns

### Selective subscription

```python
# Subscribe to errors only
channel.queue_bind(exchange='logs', queue='error_alerts', routing_key='*.error')

# Subscribe to critical from any source
channel.queue_bind(exchange='logs', queue='critical_alerts', routing_key='#.critical')
```

### Multi-consumer work distribution

```python
# Both workers bind to same queue (not same binding - same queue!)
# Work is distributed round-robin between them
```

### Audit trail

```python
# Catch-all binding for audit
channel.queue_bind(exchange='events', queue='audit_log', routing_key='#')
```

## Key takeaways

1. **Bindings connect exchanges to queues** - They define routing rules
2. **Routing key is on the message** - Binding key is on the binding
3. **Direct = exact match** - Routing key must equal binding key
4. **Topic = pattern match** - Use `*` and `#` wildcards
5. **Fanout ignores routing** - All bound queues receive everything
6. **Bindings follow durability** - Both exchange and queue must be durable

## What's next?

In the next lesson, you'll learn about message properties - headers, persistence, TTL, and priority.

---

[← Previous: Queues](./03_queues.md) | [Back to Module 2](./README.md) | [Next: Message Properties →](./05_message_properties.md)
