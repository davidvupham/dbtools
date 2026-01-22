# Python Pika Library Deep Dive

In this lesson, you learn the Pika library in depth - connection options, message properties, error handling, and production patterns.

## What is Pika?

**Pika** is the official Python client for RabbitMQ. It implements AMQP 0-9-1 protocol in pure Python.

```bash
pip install pika
```

**Key features:**
- Pure Python (no C extensions required)
- Multiple connection adapters (blocking, async, Tornado, Twisted)
- Full AMQP 0-9-1 support
- Publisher confirms
- Consumer acknowledgments

## Connection parameters

### Basic connection

```python
import pika

# Simplest form - localhost with defaults
connection = pika.BlockingConnection()

# Explicit parameters
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost')
)
```

### Full connection parameters

```python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host='localhost',           # RabbitMQ server hostname
        port=5672,                  # AMQP port
        virtual_host='/',           # Virtual host
        credentials=pika.PlainCredentials(
            username='guest',
            password='guest'
        ),
        heartbeat=600,              # Heartbeat interval (seconds)
        blocked_connection_timeout=300,  # Timeout when blocked
        connection_attempts=3,      # Retry attempts
        retry_delay=5,              # Delay between retries (seconds)
        socket_timeout=10,          # Socket timeout (seconds)
    )
)
```

### URL-based connection

```python
import pika

# Using URL format (useful for environment variables)
url = 'amqp://user:password@hostname:5672/vhost'
params = pika.URLParameters(url)
connection = pika.BlockingConnection(params)

# Example with localhost
url = 'amqp://guest:guest@localhost:5672/'
```

### Connection with environment variables

```python
import os
import pika

# Production pattern: credentials from environment
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=os.getenv('RABBITMQ_HOST', 'localhost'),
        port=int(os.getenv('RABBITMQ_PORT', 5672)),
        credentials=pika.PlainCredentials(
            username=os.getenv('RABBITMQ_USER', 'guest'),
            password=os.getenv('RABBITMQ_PASS', 'guest')
        )
    )
)
```

## Message properties

Message properties provide metadata about the message.

### BasicProperties class

```python
import pika
import json
import uuid
import time

properties = pika.BasicProperties(
    # Delivery
    delivery_mode=pika.DeliveryMode.Persistent,  # 2 = persistent

    # Content
    content_type='application/json',
    content_encoding='utf-8',

    # Correlation
    correlation_id=str(uuid.uuid4()),
    reply_to='response_queue',
    message_id=str(uuid.uuid4()),

    # Timing
    timestamp=int(time.time()),
    expiration='60000',  # TTL in milliseconds (string!)

    # Priority
    priority=5,  # 0-255

    # Application
    type='order.created',
    app_id='order-service',
    user_id='system',

    # Custom headers
    headers={
        'x-retry-count': 0,
        'x-source': 'web',
        'x-trace-id': 'abc-123'
    }
)
```

### Persistent vs transient messages

```python
# Transient (default) - lost on broker restart
properties = pika.BasicProperties(
    delivery_mode=1  # or pika.DeliveryMode.Transient
)

# Persistent - survives broker restart (if queue is also durable)
properties = pika.BasicProperties(
    delivery_mode=2  # or pika.DeliveryMode.Persistent
)
```

> [!IMPORTANT]
> For true persistence, both the **queue must be durable** AND the **message must be persistent**.

### JSON messages

```python
import json
import pika

def publish_json(channel, queue: str, data: dict) -> None:
    """Publish a JSON message with proper content type."""
    channel.basic_publish(
        exchange='',
        routing_key=queue,
        body=json.dumps(data),
        properties=pika.BasicProperties(
            delivery_mode=pika.DeliveryMode.Persistent,
            content_type='application/json',
            content_encoding='utf-8'
        )
    )

# Usage
order = {'order_id': 123, 'customer': 'Alice', 'total': 99.99}
publish_json(channel, 'orders', order)
```

## Queue options

### Durable queues

```python
# Durable queue - survives broker restart
channel.queue_declare(
    queue='important_tasks',
    durable=True  # Queue definition persists
)
```

### Exclusive queues

```python
# Exclusive queue - only this connection can use it
# Automatically deleted when connection closes
result = channel.queue_declare(
    queue='',        # Let RabbitMQ generate a name
    exclusive=True   # Only this connection
)
queue_name = result.method.queue  # e.g., 'amq.gen-JzTY...'
```

### Auto-delete queues

```python
# Auto-delete - deleted when last consumer disconnects
channel.queue_declare(
    queue='temp_queue',
    auto_delete=True
)
```

### Queue with arguments

```python
# Queue with dead-letter exchange and TTL
channel.queue_declare(
    queue='tasks',
    durable=True,
    arguments={
        'x-dead-letter-exchange': 'dlx',
        'x-dead-letter-routing-key': 'failed',
        'x-message-ttl': 300000,  # 5 minutes
        'x-max-length': 10000,    # Max messages
        'x-max-priority': 10      # Enable priority
    }
)
```

## Consumer patterns

### Basic consumer with manual ACK

```python
def callback(ch, method, properties, body):
    """Process message with manual acknowledgment."""
    try:
        data = json.loads(body)
        process_order(data)

        # Success - acknowledge
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except json.JSONDecodeError:
        # Bad message - reject without requeue
        ch.basic_nack(
            delivery_tag=method.delivery_tag,
            requeue=False  # Send to DLX if configured
        )

    except Exception as e:
        # Processing error - requeue for retry
        ch.basic_nack(
            delivery_tag=method.delivery_tag,
            requeue=True  # Back to queue
        )

channel.basic_consume(
    queue='orders',
    on_message_callback=callback,
    auto_ack=False  # IMPORTANT: Manual ACK
)
```

### Consumer with prefetch

```python
# Limit unacknowledged messages per consumer
# This enables fair dispatch among multiple consumers
channel.basic_qos(prefetch_count=1)

channel.basic_consume(
    queue='tasks',
    on_message_callback=callback,
    auto_ack=False
)
```

### Get single message (polling)

```python
# Get one message without blocking
method, properties, body = channel.basic_get(
    queue='tasks',
    auto_ack=False
)

if method:
    print(f"Got message: {body}")
    channel.basic_ack(delivery_tag=method.delivery_tag)
else:
    print("No messages available")
```

## Error handling

### Connection errors

```python
import pika
from pika.exceptions import AMQPConnectionError, AMQPChannelError


def connect_with_retry(max_attempts: int = 5):
    """Connect to RabbitMQ with retry logic."""
    for attempt in range(max_attempts):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host='localhost',
                    connection_attempts=1,
                    retry_delay=0
                )
            )
            print(f"Connected on attempt {attempt + 1}")
            return connection

        except AMQPConnectionError as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_attempts - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise

    raise AMQPConnectionError("Max connection attempts exceeded")
```

### Channel errors

```python
try:
    channel.queue_declare(queue='my_queue', durable=True)
except pika.exceptions.ChannelClosedByBroker as e:
    print(f"Channel error: {e}")
    # Channel is now closed, need to create a new one
    channel = connection.channel()
```

### Graceful shutdown

```python
import signal


def graceful_shutdown(signum, frame):
    """Handle shutdown signals."""
    print("\nShutting down gracefully...")
    channel.stop_consuming()


# Register signal handlers
signal.signal(signal.SIGINT, graceful_shutdown)
signal.signal(signal.SIGTERM, graceful_shutdown)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    pass
finally:
    connection.close()
    print("Connection closed")
```

## Production patterns

### Context manager for connections

```python
from contextlib import contextmanager
import pika


@contextmanager
def rabbitmq_connection(host='localhost'):
    """Context manager for RabbitMQ connections."""
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=host)
    )
    try:
        yield connection
    finally:
        connection.close()


# Usage
with rabbitmq_connection() as conn:
    channel = conn.channel()
    channel.basic_publish(
        exchange='',
        routing_key='tasks',
        body='Hello'
    )
# Connection automatically closed
```

### Publisher class

```python
import json
import pika
from typing import Any


class RabbitMQPublisher:
    """Reusable RabbitMQ publisher."""

    def __init__(self, host: str = 'localhost'):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host)
        )
        self.channel = self.connection.channel()

    def publish(
        self,
        queue: str,
        message: Any,
        persistent: bool = True
    ) -> None:
        """Publish a message to a queue."""
        self.channel.queue_declare(queue=queue, durable=persistent)

        body = json.dumps(message) if isinstance(message, dict) else str(message)

        self.channel.basic_publish(
            exchange='',
            routing_key=queue,
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=2 if persistent else 1,
                content_type='application/json'
            )
        )

    def close(self):
        """Close the connection."""
        self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Usage
with RabbitMQPublisher() as publisher:
    publisher.publish('orders', {'order_id': 123})
    publisher.publish('orders', {'order_id': 124})
```

### Consumer class

```python
import json
import pika
from typing import Callable


class RabbitMQConsumer:
    """Reusable RabbitMQ consumer."""

    def __init__(self, host: str = 'localhost'):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host)
        )
        self.channel = self.connection.channel()
        self.channel.basic_qos(prefetch_count=1)

    def consume(
        self,
        queue: str,
        handler: Callable[[dict], None],
        durable: bool = True
    ) -> None:
        """Start consuming messages from a queue."""
        self.channel.queue_declare(queue=queue, durable=durable)

        def callback(ch, method, properties, body):
            try:
                data = json.loads(body)
                handler(data)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                print(f"Error processing message: {e}")
                ch.basic_nack(
                    delivery_tag=method.delivery_tag,
                    requeue=False
                )

        self.channel.basic_consume(
            queue=queue,
            on_message_callback=callback,
            auto_ack=False
        )

        print(f"Consuming from '{queue}'...")
        self.channel.start_consuming()

    def close(self):
        """Close the connection."""
        self.connection.close()


# Usage
def handle_order(order: dict):
    print(f"Processing order: {order['order_id']}")

consumer = RabbitMQConsumer()
consumer.consume('orders', handle_order)
```

## Summary table

| Component | Class/Method | Purpose |
|:---|:---|:---|
| Connection | `BlockingConnection` | TCP connection to broker |
| Parameters | `ConnectionParameters` | Host, port, credentials |
| URL | `URLParameters` | Connection from URL string |
| Credentials | `PlainCredentials` | Username/password |
| Properties | `BasicProperties` | Message metadata |
| Delivery | `DeliveryMode.Persistent` | Survive restarts |
| ACK | `basic_ack()` | Acknowledge success |
| NACK | `basic_nack()` | Reject with requeue option |
| Prefetch | `basic_qos()` | Limit unacked messages |

## Key takeaways

1. **Use environment variables** for credentials in production
2. **Always set `delivery_mode=2`** for important messages
3. **Always use `auto_ack=False`** and acknowledge manually
4. **Set `prefetch_count`** for fair message distribution
5. **Handle exceptions** and decide whether to requeue
6. **Use context managers** to ensure connections close
7. **Create reusable classes** for production code

## What's next?

You've completed the foundations! In the next module, you'll dive deep into the AMQP model - exchanges, queues, bindings, and how messages are routed.

---

[← Previous: Hello World](./04_hello_world.md) | [Back to Module 1](./README.md) | [Exercises →](./exercises/)
