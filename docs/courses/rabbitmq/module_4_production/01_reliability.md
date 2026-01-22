# Reliability

In this lesson, you learn to build reliable messaging systems that don't lose messages, even when components fail.

## The reliability challenge

Messages can be lost at multiple points:

```
Producer ──▶ [Broker] ──▶ Consumer
    │           │            │
    ▼           ▼            ▼
 Network      Crash       Processing
  error      restart        error
```

To build a reliable system, you must address all three points.

## Three pillars of reliability

### 1. Message persistence

Messages survive broker restarts.

```python
# Durable queue
channel.queue_declare(queue='orders', durable=True)

# Persistent message
channel.basic_publish(
    exchange='',
    routing_key='orders',
    body=message,
    properties=pika.BasicProperties(
        delivery_mode=pika.DeliveryMode.Persistent
    )
)
```

> [!IMPORTANT]
> Both are required - durable queue AND persistent message.

### 2. Consumer acknowledgments

Messages aren't removed until processed.

```python
def callback(ch, method, properties, body):
    try:
        process_order(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception:
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

channel.basic_consume(
    queue='orders',
    on_message_callback=callback,
    auto_ack=False  # Critical!
)
```

### 3. Publisher confirms

Know when messages reach the broker.

```python
channel.confirm_delivery()

try:
    channel.basic_publish(
        exchange='',
        routing_key='orders',
        body=message,
        properties=pika.BasicProperties(delivery_mode=2),
        mandatory=True
    )
    print("Message confirmed")
except pika.exceptions.UnroutableError:
    print("Message could not be routed")
```

## Publisher confirms in detail

### Synchronous confirms

Wait for each message to be confirmed:

```python
channel.confirm_delivery()

for order in orders:
    try:
        channel.basic_publish(
            exchange='orders',
            routing_key='new',
            body=json.dumps(order),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        # Blocks until confirmed or nacked
        print(f"Order {order['id']} confirmed")
    except Exception as e:
        print(f"Order {order['id']} failed: {e}")
        # Handle failure - retry, log, etc.
```

### Batch confirms

Confirm multiple messages at once:

```python
channel.confirm_delivery()

for i, order in enumerate(orders):
    channel.basic_publish(
        exchange='orders',
        routing_key='new',
        body=json.dumps(order),
        properties=pika.BasicProperties(delivery_mode=2)
    )

    # Confirm every 100 messages
    if (i + 1) % 100 == 0:
        channel.wait_for_pending_acks()  # Block until all confirmed
        print(f"Batch of 100 confirmed")
```

### Asynchronous confirms

Non-blocking confirmation with callbacks:

```python
from pika import SelectConnection

def on_delivery_confirmation(frame):
    if frame.method.NAME == 'Basic.Ack':
        print(f"Message {frame.method.delivery_tag} confirmed")
    else:
        print(f"Message {frame.method.delivery_tag} nacked")

# With SelectConnection adapter
channel.add_on_delivery_callback(on_delivery_confirmation)
channel.confirm_delivery()
```

## Mandatory flag

The `mandatory` flag ensures messages are routed to at least one queue:

```python
channel.confirm_delivery()

try:
    channel.basic_publish(
        exchange='orders',
        routing_key='nonexistent',
        body='test',
        mandatory=True  # Return if unroutable
    )
except pika.exceptions.UnroutableError:
    print("Message returned - no matching queue")
```

Without `mandatory`, unroutable messages are silently dropped.

## Consumer acknowledgment patterns

### Positive acknowledgment (ACK)

```python
# Simple ACK
ch.basic_ack(delivery_tag=method.delivery_tag)

# Multiple ACK (acknowledge all messages up to this one)
ch.basic_ack(delivery_tag=method.delivery_tag, multiple=True)
```

### Negative acknowledgment (NACK)

```python
# Requeue for retry
ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

# Don't requeue (send to DLX if configured)
ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

# Nack multiple messages
ch.basic_nack(delivery_tag=method.delivery_tag, multiple=True, requeue=False)
```

### Reject (single message)

```python
# Requeue
ch.basic_reject(delivery_tag=method.delivery_tag, requeue=True)

# Don't requeue
ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
```

## Acknowledgment strategies

### Strategy 1: Acknowledge after processing

Safest but slowest:

```python
def callback(ch, method, properties, body):
    process(body)  # May take time
    ch.basic_ack(delivery_tag=method.delivery_tag)
```

### Strategy 2: Batch acknowledgment

Better throughput:

```python
messages_since_ack = 0
BATCH_SIZE = 10

def callback(ch, method, properties, body):
    global messages_since_ack

    process(body)
    messages_since_ack += 1

    if messages_since_ack >= BATCH_SIZE:
        ch.basic_ack(delivery_tag=method.delivery_tag, multiple=True)
        messages_since_ack = 0
```

### Strategy 3: Prefetch with individual ACK

Good balance:

```python
channel.basic_qos(prefetch_count=10)

def callback(ch, method, properties, body):
    try:
        process(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception:
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
```

## Complete reliable producer

```python
#!/usr/bin/env python
"""Production-ready reliable producer."""
import json
import logging
import time
import pika

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReliableProducer:
    def __init__(self, host='localhost', max_retries=3):
        self.host = host
        self.max_retries = max_retries
        self.connection = None
        self.channel = None

    def connect(self):
        """Establish connection with retry."""
        for attempt in range(self.max_retries):
            try:
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host=self.host,
                        heartbeat=600,
                        blocked_connection_timeout=300
                    )
                )
                self.channel = self.connection.channel()
                self.channel.confirm_delivery()
                logger.info("Connected to RabbitMQ")
                return
            except pika.exceptions.AMQPConnectionError as e:
                logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise

    def publish(self, exchange: str, routing_key: str, message: dict) -> bool:
        """Publish with confirmation and retry."""
        body = json.dumps(message)

        for attempt in range(self.max_retries):
            try:
                if not self.connection or self.connection.is_closed:
                    self.connect()

                self.channel.basic_publish(
                    exchange=exchange,
                    routing_key=routing_key,
                    body=body,
                    properties=pika.BasicProperties(
                        delivery_mode=pika.DeliveryMode.Persistent,
                        content_type='application/json'
                    ),
                    mandatory=True
                )
                logger.info(f"Message published to {routing_key}")
                return True

            except pika.exceptions.UnroutableError:
                logger.error(f"Message unroutable: {routing_key}")
                return False

            except pika.exceptions.AMQPError as e:
                logger.warning(f"Publish attempt {attempt + 1} failed: {e}")
                self.connection = None  # Force reconnect
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)

        logger.error(f"Failed to publish after {self.max_retries} attempts")
        return False

    def close(self):
        if self.connection:
            self.connection.close()


# Usage
producer = ReliableProducer()
success = producer.publish('', 'orders', {'order_id': 123})
producer.close()
```

## Complete reliable consumer

```python
#!/usr/bin/env python
"""Production-ready reliable consumer."""
import json
import logging
import signal
import time
import pika

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReliableConsumer:
    def __init__(self, queue: str, handler, prefetch: int = 10):
        self.queue = queue
        self.handler = handler
        self.prefetch = prefetch
        self.connection = None
        self.channel = None
        self._should_stop = False

    def connect(self):
        """Establish connection."""
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='localhost',
                heartbeat=600,
                blocked_connection_timeout=300
            )
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue, durable=True)
        self.channel.basic_qos(prefetch_count=self.prefetch)

    def _callback(self, ch, method, properties, body):
        """Handle message with proper acknowledgment."""
        try:
            data = json.loads(body)
            self.handler(data)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"Processed message: {method.delivery_tag}")

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        except Exception as e:
            logger.error(f"Processing error: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def start(self):
        """Start consuming with automatic reconnection."""
        while not self._should_stop:
            try:
                self.connect()
                self.channel.basic_consume(
                    queue=self.queue,
                    on_message_callback=self._callback,
                    auto_ack=False
                )
                logger.info(f"Consuming from {self.queue}")
                self.channel.start_consuming()

            except pika.exceptions.AMQPConnectionError as e:
                logger.warning(f"Connection lost: {e}")
                time.sleep(5)

            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                time.sleep(5)

    def stop(self):
        """Stop consuming gracefully."""
        self._should_stop = True
        if self.channel:
            self.channel.stop_consuming()
        if self.connection:
            self.connection.close()


# Usage
def process_order(data):
    print(f"Processing order: {data['order_id']}")

consumer = ReliableConsumer('orders', process_order)

def signal_handler(sig, frame):
    consumer.stop()

signal.signal(signal.SIGINT, signal_handler)
consumer.start()
```

## Key takeaways

1. **Three pillars**: Persistence, acknowledgments, and publisher confirms
2. **Never use auto_ack=True** in production
3. **Enable publisher confirms** to know messages are received
4. **Use mandatory flag** to detect unroutable messages
5. **Implement retry logic** with exponential backoff
6. **Handle reconnection** gracefully

## What's next?

In the next lesson, you'll learn about Dead Letter Exchanges for handling message failures.

---

[← Back to Module 4](./README.md) | [Next: Dead Letter Exchanges →](./02_dead_letter_exchanges.md)
