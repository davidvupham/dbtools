# Exercise 2: Message Properties

## Learning objectives

After completing this exercise, you will be able to:
- Set and read message properties
- Work with different delivery modes
- Use custom headers for metadata

---

## Exercise 2.1: Basic properties (Warm-up)

**Bloom Level**: Apply

Create a function that publishes a message with essential properties.

```python
import pika
import uuid
import time


def publish_with_properties(
    channel,
    queue: str,
    message: str,
    content_type: str = 'text/plain'
) -> str:
    """
    Publish a message with standard properties.

    Set the following properties:
    - content_type: from parameter
    - timestamp: current time
    - message_id: generated UUID
    - delivery_mode: persistent (2)

    Args:
        channel: Pika channel
        queue: Queue name
        message: Message body
        content_type: MIME type

    Returns:
        The generated message_id
    """
    # Your code here
    pass


# Test
connection = pika.BlockingConnection()
channel = connection.channel()
channel.queue_declare(queue='properties_test', durable=True)

msg_id = publish_with_properties(
    channel,
    'properties_test',
    'Hello with properties!'
)
print(f"Published message with ID: {msg_id}")

connection.close()
```

---

## Exercise 2.2: JSON messages (Practice)

**Bloom Level**: Apply

Create producer and consumer functions for JSON messages with proper content type handling.

```python
import json
import pika


def publish_json(channel, queue: str, data: dict) -> None:
    """
    Publish a JSON message with correct content type.

    Properties to set:
    - content_type: application/json
    - content_encoding: utf-8
    - delivery_mode: persistent
    """
    # Your code here
    pass


def consume_json(channel, queue: str, callback):
    """
    Consume JSON messages, automatically parsing the body.

    The callback should receive parsed dict, not bytes.
    """
    def wrapper(ch, method, properties, body):
        # Your code here - parse JSON and call callback
        pass

    channel.basic_consume(
        queue=queue,
        on_message_callback=wrapper,
        auto_ack=True
    )


# Test
def handle_order(data: dict):
    print(f"Received order: {data}")

connection = pika.BlockingConnection()
channel = connection.channel()
channel.queue_declare(queue='json_test')

publish_json(channel, 'json_test', {'order_id': 123, 'item': 'Widget'})
publish_json(channel, 'json_test', {'order_id': 124, 'item': 'Gadget'})

# Get messages (non-blocking)
for _ in range(2):
    method, props, body = channel.basic_get('json_test', auto_ack=True)
    if body:
        print(f"Content-Type: {props.content_type}")
        print(f"Data: {json.loads(body)}")

connection.close()
```

---

## Exercise 2.3: Priority messages (Practice)

**Bloom Level**: Apply

Set up a priority queue and demonstrate message ordering based on priority.

```python
import pika


def setup_priority_queue(channel, queue: str, max_priority: int = 10):
    """
    Declare a queue that supports message priorities.

    Hint: Use x-max-priority argument
    """
    # Your code here
    pass


def publish_with_priority(
    channel,
    queue: str,
    message: str,
    priority: int
) -> None:
    """Publish a message with a specific priority."""
    # Your code here
    pass


# Test
connection = pika.BlockingConnection()
channel = connection.channel()

# Create priority queue
setup_priority_queue(channel, 'priority_test', max_priority=10)

# Publish messages with different priorities
publish_with_priority(channel, 'priority_test', 'Low priority', 1)
publish_with_priority(channel, 'priority_test', 'Medium priority', 5)
publish_with_priority(channel, 'priority_test', 'High priority', 10)
publish_with_priority(channel, 'priority_test', 'Another low', 2)

# Consume and observe order
print("Consuming messages (should be ordered by priority):")
for _ in range(4):
    method, props, body = channel.basic_get('priority_test', auto_ack=True)
    if body:
        print(f"Priority {props.priority}: {body.decode()}")

connection.close()
```

Expected output:
```
Consuming messages (should be ordered by priority):
Priority 10: High priority
Priority 5: Medium priority
Priority 2: Another low
Priority 1: Low priority
```

---

## Exercise 2.4: Custom headers (Practice)

**Bloom Level**: Analyze

Use custom headers to add metadata for routing and filtering.

```python
import pika
from datetime import datetime


def publish_with_headers(
    channel,
    queue: str,
    message: str,
    headers: dict
) -> None:
    """Publish a message with custom headers."""
    # Your code here
    pass


def consume_with_header_filter(
    channel,
    queue: str,
    header_name: str,
    header_value: str,
    callback
):
    """
    Consume messages but only process those matching a header value.

    Messages not matching should be acknowledged but skipped.
    """
    def wrapper(ch, method, properties, body):
        # Your code here
        pass

    channel.basic_consume(
        queue=queue,
        on_message_callback=wrapper,
        auto_ack=False
    )


# Test
connection = pika.BlockingConnection()
channel = connection.channel()
channel.queue_declare(queue='headers_test')

# Publish messages with different headers
publish_with_headers(channel, 'headers_test', 'Order from web',
                     {'source': 'web', 'priority': 'normal'})
publish_with_headers(channel, 'headers_test', 'Order from mobile',
                     {'source': 'mobile', 'priority': 'high'})
publish_with_headers(channel, 'headers_test', 'Order from API',
                     {'source': 'api', 'priority': 'normal'})

# Consume only mobile orders
print("Processing only mobile orders:")
# ... test consume_with_header_filter

connection.close()
```

---

## Exercise 2.5: Message TTL and expiration (Challenge)

**Bloom Level**: Create

Create a system that uses message TTL for time-sensitive messages.

Requirements:
1. Publish messages with different expiration times
2. Demonstrate that expired messages are removed from the queue
3. Optionally route expired messages to a dead letter queue

```python
import pika
import time


def setup_ttl_demo(channel):
    """
    Set up queues for TTL demonstration.

    Create:
    - 'ttl_queue' with a dead letter exchange
    - 'expired_queue' to receive expired messages
    """
    # Your code here
    pass


def publish_with_ttl(
    channel,
    queue: str,
    message: str,
    ttl_ms: int
) -> None:
    """
    Publish a message that expires after ttl_ms milliseconds.

    Hint: Use the 'expiration' property (string value)
    """
    # Your code here
    pass


# Test
connection = pika.BlockingConnection()
channel = connection.channel()

setup_ttl_demo(channel)

# Publish messages with different TTLs
publish_with_ttl(channel, 'ttl_queue', 'Expires in 2 seconds', 2000)
publish_with_ttl(channel, 'ttl_queue', 'Expires in 10 seconds', 10000)

print("Published 2 messages with different TTLs")
print("Waiting 3 seconds...")
time.sleep(3)

# Check what's left
method, _, body = channel.basic_get('ttl_queue', auto_ack=True)
if body:
    print(f"Still in queue: {body.decode()}")
else:
    print("First message expired")

# Check dead letter queue
method, _, body = channel.basic_get('expired_queue', auto_ack=True)
if body:
    print(f"In expired queue: {body.decode()}")

connection.close()
```

---

## Deliverables

Submit your solutions with:
- Working code demonstrating each property type
- Output showing the properties being used correctly
- Comments explaining when to use each property

---

[← Previous Exercise](./ex_01_connections.md) | [Back to Module 1](../README.md) | [Next Exercise →](./ex_03_producer.md)
