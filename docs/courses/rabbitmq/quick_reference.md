# RabbitMQ Quick Reference

**[← Back to Course Index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-RabbitMQ-orange)

> [!IMPORTANT]
> **Related Docs:** [Glossary](./glossary.md) | [Course Overview](./course_overview.md)

## Table of contents

- [Docker commands](#docker-commands)
- [RabbitMQ CLI (rabbitmqctl)](#rabbitmq-cli-rabbitmqctl)
- [Management UI](#management-ui)
- [Python Pika patterns](#python-pika-patterns)
- [Exchange types](#exchange-types)
- [Message properties](#message-properties)
- [Production checklist](#production-checklist)

## Docker commands

### Start RabbitMQ

```bash
# Simple single container with management UI
docker run -d --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  rabbitmq:management

# With custom credentials
docker run -d --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  -e RABBITMQ_DEFAULT_USER=myuser \
  -e RABBITMQ_DEFAULT_PASS=mypassword \
  rabbitmq:management

# With data persistence
docker run -d --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  -v rabbitmq_data:/var/lib/rabbitmq \
  rabbitmq:management
```

### Container management

```bash
docker start rabbitmq       # Start stopped container
docker stop rabbitmq        # Stop container
docker restart rabbitmq     # Restart container
docker logs rabbitmq        # View logs
docker logs -f rabbitmq     # Follow logs
docker exec -it rabbitmq bash  # Shell access
```

[↑ Back to Table of Contents](#table-of-contents)

## RabbitMQ CLI (rabbitmqctl)

### Status and information

```bash
# Inside container: docker exec -it rabbitmq bash

rabbitmqctl status              # Node status
rabbitmqctl cluster_status      # Cluster status
rabbitmqctl environment         # Environment variables
rabbitmqctl report              # Full diagnostic report
```

### Queue management

```bash
rabbitmqctl list_queues                    # List all queues
rabbitmqctl list_queues name messages      # Queue names and message counts
rabbitmqctl list_queues name consumers     # Queue names and consumer counts
rabbitmqctl purge_queue <queue_name>       # Delete all messages from queue
rabbitmqctl delete_queue <queue_name>      # Delete queue
```

### Exchange management

```bash
rabbitmqctl list_exchanges                 # List all exchanges
rabbitmqctl list_exchanges name type       # Exchange names and types
rabbitmqctl list_bindings                  # List all bindings
```

### Connection and channel management

```bash
rabbitmqctl list_connections               # List connections
rabbitmqctl list_channels                  # List channels
rabbitmqctl list_consumers                 # List consumers
```

### User management

```bash
rabbitmqctl list_users                                    # List users
rabbitmqctl add_user <user> <password>                   # Add user
rabbitmqctl delete_user <user>                           # Delete user
rabbitmqctl change_password <user> <newpass>             # Change password
rabbitmqctl set_permissions -p / <user> ".*" ".*" ".*"   # Full permissions
rabbitmqctl set_user_tags <user> administrator           # Make admin
```

### Virtual host management

```bash
rabbitmqctl list_vhosts                    # List virtual hosts
rabbitmqctl add_vhost <vhost>              # Add virtual host
rabbitmqctl delete_vhost <vhost>           # Delete virtual host
```

[↑ Back to Table of Contents](#table-of-contents)

## Management UI

**URL:** `http://localhost:15672`
**Default credentials:** `guest` / `guest`

### Key tabs

| Tab | Purpose |
|:---|:---|
| Overview | Node stats, message rates, global counts |
| Connections | Active client connections |
| Channels | Communication channels within connections |
| Exchanges | All exchanges with message rates |
| Queues | All queues with message counts |
| Admin | Users, virtual hosts, policies |

### Useful metrics to monitor

- **Ready messages** - Messages waiting to be consumed
- **Unacked messages** - Messages delivered but not acknowledged
- **Publish rate** - Messages/second being published
- **Deliver rate** - Messages/second being delivered to consumers
- **Memory** - Broker memory usage
- **Disk** - Disk space for persistence

[↑ Back to Table of Contents](#table-of-contents)

## Python Pika patterns

### Basic producer

```python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='hello')

channel.basic_publish(
    exchange='',
    routing_key='hello',
    body='Hello World!'
)

connection.close()
```

### Basic consumer

```python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='hello')

def callback(ch, method, properties, body):
    print(f"Received: {body.decode()}")

channel.basic_consume(
    queue='hello',
    on_message_callback=callback,
    auto_ack=True
)

channel.start_consuming()
```

### Consumer with manual acknowledgment

```python
def callback(ch, method, properties, body):
    try:
        process_message(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

channel.basic_consume(
    queue='task_queue',
    on_message_callback=callback,
    auto_ack=False  # Manual ack
)
```

### Durable queue with persistent messages

```python
# Producer
channel.queue_declare(queue='task_queue', durable=True)

channel.basic_publish(
    exchange='',
    routing_key='task_queue',
    body=message,
    properties=pika.BasicProperties(
        delivery_mode=pika.DeliveryMode.Persistent
    )
)

# Consumer
channel.basic_qos(prefetch_count=1)
channel.queue_declare(queue='task_queue', durable=True)
```

### Topic exchange

```python
# Producer
channel.exchange_declare(exchange='logs', exchange_type='topic')

channel.basic_publish(
    exchange='logs',
    routing_key='app.error.critical',
    body='Critical error occurred!'
)

# Consumer
channel.exchange_declare(exchange='logs', exchange_type='topic')
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

channel.queue_bind(
    exchange='logs',
    queue=queue_name,
    routing_key='app.error.*'
)
```

### Dead letter exchange setup

```python
# Declare dead letter exchange
channel.exchange_declare(exchange='dlx', exchange_type='direct')
channel.queue_declare(queue='dead_letters')
channel.queue_bind(exchange='dlx', queue='dead_letters', routing_key='failed')

# Declare main queue with DLX
channel.queue_declare(
    queue='task_queue',
    durable=True,
    arguments={
        'x-dead-letter-exchange': 'dlx',
        'x-dead-letter-routing-key': 'failed'
    }
)
```

[↑ Back to Table of Contents](#table-of-contents)

## Exchange types

| Type | Routing Logic | Use Case |
|:---|:---|:---|
| **Direct** | Exact routing key match | Task queues, point-to-point |
| **Topic** | Pattern matching (`*`, `#`) | Log routing, event filtering |
| **Fanout** | Broadcast to all bound queues | Notifications, pub/sub |
| **Headers** | Message header matching | Complex routing rules |

### Routing key patterns (Topic exchange)

| Pattern | Matches |
|:---|:---|
| `stock.usd.nyse` | Exact match only |
| `stock.*.*` | `stock.usd.nyse`, `stock.eur.lse` |
| `stock.#` | `stock.usd`, `stock.usd.nyse.tech` |
| `#.critical` | `app.error.critical`, `critical` |
| `*.*.critical` | `app.error.critical` (exactly 3 words) |

[↑ Back to Table of Contents](#table-of-contents)

## Message properties

| Property | Description | Example |
|:---|:---|:---|
| `delivery_mode` | 1 = transient, 2 = persistent | `delivery_mode=2` |
| `content_type` | MIME type | `application/json` |
| `content_encoding` | Encoding | `utf-8` |
| `priority` | Priority 0-255 | `priority=5` |
| `correlation_id` | Request/response correlation | UUID |
| `reply_to` | Response queue name | `reply_queue` |
| `expiration` | TTL in milliseconds | `60000` |
| `message_id` | Application message ID | UUID |
| `timestamp` | Unix timestamp | `1706000000` |
| `type` | Application message type | `order.created` |
| `app_id` | Application identifier | `order-service` |

[↑ Back to Table of Contents](#table-of-contents)

## Production checklist

### Before deployment

- [ ] **Use durable queues** for important data
- [ ] **Use persistent messages** with `delivery_mode=2`
- [ ] **Enable manual acknowledgments** - never use `auto_ack=True` in production
- [ ] **Set appropriate prefetch** - `basic_qos(prefetch_count=N)`
- [ ] **Configure dead letter exchanges** for failed messages
- [ ] **Use quorum queues** for critical data (RabbitMQ 3.8+)

### Clustering

- [ ] **Use odd number of nodes** (3, 5, 7) for quorum decisions
- [ ] **Configure partition handling** - prefer `pause_minority`
- [ ] **Enable disk alarms** to prevent data loss
- [ ] **Set memory limits** appropriately

### Security

- [ ] **Change default credentials** - never use `guest/guest`
- [ ] **Enable TLS** for encrypted connections
- [ ] **Configure virtual hosts** for tenant isolation
- [ ] **Set minimal permissions** for each user
- [ ] **Disable management UI** in production or restrict access

### Monitoring

- [ ] **Monitor queue depth** - growing queues indicate problems
- [ ] **Monitor unacked messages** - may indicate stuck consumers
- [ ] **Monitor memory usage** - set alarms at 80%
- [ ] **Monitor disk usage** - set alarms at 80%
- [ ] **Set up alerts** for connection drops and queue buildups

### Performance

- [ ] **Keep queues short** - consumers should keep up with producers
- [ ] **Use multiple queues** - single queue is a bottleneck
- [ ] **Batch operations** where possible
- [ ] **Disable plugins** you don't use
- [ ] **Use direct exchange** when possible (fastest)

[↑ Back to Table of Contents](#table-of-contents)

---

[← Back to Course Index](./README.md)
