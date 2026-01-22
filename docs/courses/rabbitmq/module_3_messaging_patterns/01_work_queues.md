# Work Queues

In this lesson, you learn to implement the Work Queue pattern - distributing time-consuming tasks among multiple workers.

## The pattern

**Work Queues** (aka Task Queues) distribute tasks among multiple workers. This is useful for processing resource-intensive tasks asynchronously.

```
                        ┌─────────────┐
                   ┌───▶│  Worker 1   │
                   │    └─────────────┘
┌──────────┐    ┌──┴──┐
│ Producer │───▶│Queue│  Round-robin dispatch
└──────────┘    └──┬──┘
                   │    ┌─────────────┐
                   └───▶│  Worker 2   │
                        └─────────────┘
```

**Key characteristics:**
- Multiple consumers share one queue
- Each message is delivered to exactly one consumer
- Work is distributed round-robin by default
- Tasks are processed in parallel

## When to use work queues

- **Image processing** - Resize, compress, convert images
- **PDF generation** - Create reports from data
- **Email sending** - Send bulk emails in background
- **Data import** - Process uploaded files
- **Video encoding** - Transcode video files

## Basic implementation

### Producer: new_task.py

```python
#!/usr/bin/env python
"""
new_task.py - Sends tasks to the work queue.

Usage: python new_task.py "Task description..."
"""
import sys
import pika


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost')
    )
    channel = connection.channel()

    # Declare a durable queue
    channel.queue_declare(queue='task_queue', durable=True)

    message = ' '.join(sys.argv[1:]) or 'Hello World!'

    # Publish with persistence
    channel.basic_publish(
        exchange='',
        routing_key='task_queue',
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=pika.DeliveryMode.Persistent
        )
    )

    print(f" [x] Sent '{message}'")
    connection.close()


if __name__ == '__main__':
    main()
```

### Consumer: worker.py

```python
#!/usr/bin/env python
"""
worker.py - Processes tasks from the work queue.

The number of dots in the message simulates processing time.
"""
import time
import pika


def callback(ch, method, properties, body):
    message = body.decode()
    print(f" [x] Received '{message}'")

    # Simulate work - count dots for sleep duration
    time.sleep(message.count('.'))

    print(f" [x] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost')
    )
    channel = connection.channel()

    channel.queue_declare(queue='task_queue', durable=True)

    # Fair dispatch - don't give more than one message at a time
    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(
        queue='task_queue',
        on_message_callback=callback,
        auto_ack=False  # Manual acknowledgment!
    )

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    main()
```

## Testing the pattern

### Terminal 1 & 2: Start workers

```bash
# Terminal 1
python worker.py
# [*] Waiting for messages...

# Terminal 2
python worker.py
# [*] Waiting for messages...
```

### Terminal 3: Send tasks

```bash
python new_task.py "Task 1."        # 1 second
python new_task.py "Task 2.."       # 2 seconds
python new_task.py "Task 3..."      # 3 seconds
python new_task.py "Task 4...."     # 4 seconds
```

### Observe distribution

```
# Terminal 1 (Worker 1)
[x] Received 'Task 1.'
[x] Done
[x] Received 'Task 3...'
[x] Done

# Terminal 2 (Worker 2)
[x] Received 'Task 2..'
[x] Done
[x] Received 'Task 4....'
[x] Done
```

## Message acknowledgment

### Why acknowledgment matters

Without proper acknowledgment, message loss can occur:

```python
# DANGEROUS - message lost if worker crashes during processing
channel.basic_consume(
    queue='tasks',
    on_message_callback=callback,
    auto_ack=True  # Message removed immediately on delivery
)
```

### Proper acknowledgment

```python
def callback(ch, method, properties, body):
    try:
        process_task(body)
        # Only acknowledge after successful processing
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Error: {e}")
        # Requeue for retry
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

channel.basic_consume(
    queue='tasks',
    on_message_callback=callback,
    auto_ack=False  # Manual acknowledgment
)
```

### Acknowledgment timeout

RabbitMQ has a default 30-minute timeout for acknowledgments. For long tasks:

```python
# In rabbitmq.conf
# consumer_timeout = 3600000  # 1 hour in milliseconds
```

## Fair dispatch with prefetch

### The problem without prefetch

By default, RabbitMQ pushes messages as fast as possible:

```
Without prefetch:
Worker 1 (slow):  [task1...] [task3...] [task5...] [task7...]
Worker 2 (fast):  [task2] [task4] [task6] [task8] [idle] [idle]
```

### Solution: prefetch_count

```python
# Only give me one message at a time
channel.basic_qos(prefetch_count=1)
```

Now messages go to available workers:

```
With prefetch_count=1:
Worker 1 (slow):  [task1...] [task5...]
Worker 2 (fast):  [task2] [task3] [task4] [task6] [task7] [task8]
```

### Choosing prefetch value

| Value | Behavior | Use Case |
|:---|:---|:---|
| 1 | Strictest fair dispatch | Variable task duration |
| 10-50 | Batched delivery | Similar task duration |
| 0 | Unlimited (default) | Fast tasks, max throughput |

```python
# For CPU-bound tasks with variable duration
channel.basic_qos(prefetch_count=1)

# For I/O-bound tasks (network calls, etc.)
channel.basic_qos(prefetch_count=10)

# For very fast tasks
channel.basic_qos(prefetch_count=50)
```

## Message durability

For tasks to survive broker restart:

### 1. Durable queue

```python
channel.queue_declare(queue='task_queue', durable=True)
```

### 2. Persistent messages

```python
channel.basic_publish(
    exchange='',
    routing_key='task_queue',
    body=task,
    properties=pika.BasicProperties(
        delivery_mode=pika.DeliveryMode.Persistent
    )
)
```

> [!NOTE]
> Persistence has a performance cost. Messages are written to disk, which is slower than memory. For high-throughput scenarios, consider publisher confirms instead of relying solely on persistence.

## Handling failures

### Retry with requeue

```python
def callback(ch, method, properties, body):
    try:
        process(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except TemporaryError:
        # Requeue for immediate retry
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    except PermanentError:
        # Don't requeue - send to DLQ
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
```

### Retry with delay

Use dead letter exchange for delayed retry:

```python
# Setup delayed retry queue
channel.exchange_declare(exchange='dlx', exchange_type='direct')

# Main queue with DLX and TTL
channel.queue_declare(
    queue='tasks',
    durable=True,
    arguments={
        'x-dead-letter-exchange': 'retry_exchange',
        'x-dead-letter-routing-key': 'tasks'
    }
)

# Retry queue with delay
channel.queue_declare(
    queue='tasks_retry',
    durable=True,
    arguments={
        'x-message-ttl': 30000,  # 30 second delay
        'x-dead-letter-exchange': '',
        'x-dead-letter-routing-key': 'tasks'
    }
)
```

### Tracking retry count

```python
def callback(ch, method, properties, body):
    headers = properties.headers or {}
    retry_count = headers.get('x-retry-count', 0)

    if retry_count >= 3:
        # Max retries exceeded
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        return

    try:
        process(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception:
        # Republish with incremented retry count
        new_headers = dict(headers)
        new_headers['x-retry-count'] = retry_count + 1

        ch.basic_publish(
            exchange='',
            routing_key='tasks_retry',
            body=body,
            properties=pika.BasicProperties(
                headers=new_headers,
                delivery_mode=2
            )
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)
```

## Complete production example

```python
#!/usr/bin/env python
"""Production-ready work queue consumer."""
import json
import logging
import signal
import sys
import pika

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskWorker:
    """Worker that processes tasks from a queue."""

    def __init__(self, queue_name: str, prefetch: int = 1):
        self.queue_name = queue_name
        self.prefetch = prefetch
        self.connection = None
        self.channel = None
        self._should_stop = False

    def connect(self):
        """Establish connection to RabbitMQ."""
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='localhost',
                heartbeat=600,
                blocked_connection_timeout=300
            )
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name, durable=True)
        self.channel.basic_qos(prefetch_count=self.prefetch)

    def process_task(self, body: bytes) -> None:
        """Process a single task. Override in subclass."""
        data = json.loads(body)
        logger.info(f"Processing: {data}")
        # Actual processing here

    def callback(self, ch, method, properties, body):
        """Handle incoming messages."""
        try:
            self.process_task(body)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info("Task completed")
        except Exception as e:
            logger.error(f"Task failed: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def start(self):
        """Start consuming messages."""
        self.connect()
        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=self.callback,
            auto_ack=False
        )

        logger.info(f"Worker started, consuming from '{self.queue_name}'")

        while not self._should_stop:
            self.connection.process_data_events(time_limit=1)

    def stop(self):
        """Stop the worker gracefully."""
        self._should_stop = True
        if self.connection:
            self.connection.close()


def main():
    worker = TaskWorker('task_queue')

    def signal_handler(sig, frame):
        logger.info("Shutting down...")
        worker.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    worker.start()


if __name__ == '__main__':
    main()
```

## Key takeaways

1. **Work queues distribute tasks** - One message goes to one consumer
2. **Use manual acknowledgment** - Never `auto_ack=True` in production
3. **Set prefetch_count** - Enables fair dispatch among workers
4. **Make queues durable** - Combined with persistent messages for reliability
5. **Handle failures gracefully** - Requeue or dead-letter based on error type
6. **Scale by adding workers** - Just start more consumer processes

## What's next?

In the next lesson, you'll learn the Publish/Subscribe pattern for broadcasting messages to multiple consumers.

---

[← Back to Module 3](./README.md) | [Next: Publish/Subscribe →](./02_publish_subscribe.md)
