# Exercise 1: Connection Basics

## Learning objectives

After completing this exercise, you will be able to:
- Create connections with different parameters
- Work with multiple channels
- Handle connection errors gracefully

---

## Exercise 1.1: Connection parameters (Warm-up)

**Bloom Level**: Apply

Create a function that connects to RabbitMQ using URL parameters instead of `ConnectionParameters`.

```python
import pika


def connect_with_url(url: str):
    """
    Connect to RabbitMQ using a URL string.

    Args:
        url: AMQP URL (e.g., 'amqp://guest:guest@localhost:5672/')

    Returns:
        BlockingConnection object
    """
    # Your code here
    pass


# Test
connection = connect_with_url('amqp://guest:guest@localhost:5672/')
print(f"Connected: {connection.is_open}")
connection.close()
```

---

## Exercise 1.2: Environment-based connection (Practice)

**Bloom Level**: Apply

Create a function that reads connection parameters from environment variables with sensible defaults.

```python
import os
import pika


def get_connection():
    """
    Create a RabbitMQ connection using environment variables.

    Environment variables:
        RABBITMQ_HOST (default: localhost)
        RABBITMQ_PORT (default: 5672)
        RABBITMQ_USER (default: guest)
        RABBITMQ_PASS (default: guest)
        RABBITMQ_VHOST (default: /)

    Returns:
        BlockingConnection object
    """
    # Your code here
    pass


# Test (set environment variables first if needed)
connection = get_connection()
print(f"Connected to: {connection._impl.params.host}")
connection.close()
```

---

## Exercise 1.3: Multiple channels (Practice)

**Bloom Level**: Apply

Create a script that demonstrates using multiple channels for different operations on a single connection.

Requirements:
1. Create one connection
2. Create two channels: one for publishing, one for consuming
3. Declare a queue on both channels
4. Publish 3 messages using the publishing channel
5. Consume those messages using the consuming channel

```python
import pika


def multi_channel_demo():
    """Demonstrate multiple channels on one connection."""
    # Your code here
    pass


if __name__ == '__main__':
    multi_channel_demo()
```

Expected output:
```
Created publishing channel
Created consuming channel
Published: Message 1
Published: Message 2
Published: Message 3
Received: Message 1
Received: Message 2
Received: Message 3
```

---

## Exercise 1.4: Connection retry logic (Challenge)

**Bloom Level**: Analyze

Implement a robust connection function with exponential backoff retry logic.

Requirements:
1. Attempt to connect up to `max_attempts` times
2. On failure, wait before retrying (exponential backoff: 1s, 2s, 4s, 8s...)
3. Log each attempt
4. Raise the last exception if all attempts fail

```python
import time
import pika
from pika.exceptions import AMQPConnectionError


def connect_with_retry(
    host: str = 'localhost',
    max_attempts: int = 5,
    initial_delay: float = 1.0
) -> pika.BlockingConnection:
    """
    Connect to RabbitMQ with exponential backoff retry.

    Args:
        host: RabbitMQ hostname
        max_attempts: Maximum connection attempts
        initial_delay: Initial delay between retries (seconds)

    Returns:
        BlockingConnection object

    Raises:
        AMQPConnectionError: If all attempts fail
    """
    # Your code here
    pass


# Test (with RabbitMQ running)
connection = connect_with_retry()
print("Successfully connected!")
connection.close()

# Test (with RabbitMQ stopped - should see retry attempts)
# connection = connect_with_retry(host='nonexistent-host', max_attempts=3)
```

---

## Exercise 1.5: Connection health check (Challenge)

**Bloom Level**: Create

Create a reusable class that manages a RabbitMQ connection with automatic health checking and reconnection.

Requirements:
1. Store connection parameters
2. Implement `connect()` method
3. Implement `is_healthy()` method that checks if connection is alive
4. Implement `get_channel()` that returns a channel (reconnecting if needed)
5. Implement context manager protocol (`__enter__`, `__exit__`)

```python
import pika


class RabbitMQConnection:
    """Managed RabbitMQ connection with health checking."""

    def __init__(self, host: str = 'localhost', port: int = 5672):
        self.host = host
        self.port = port
        self._connection = None

    def connect(self):
        """Establish connection to RabbitMQ."""
        # Your code here
        pass

    def is_healthy(self) -> bool:
        """Check if connection is alive and healthy."""
        # Your code here
        pass

    def get_channel(self):
        """Get a channel, reconnecting if necessary."""
        # Your code here
        pass

    def close(self):
        """Close the connection."""
        # Your code here
        pass

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Test
with RabbitMQConnection() as conn:
    print(f"Healthy: {conn.is_healthy()}")
    channel = conn.get_channel()
    channel.queue_declare(queue='test_health')
    print("Queue declared successfully")
```

---

## Deliverables

Submit your solutions for all exercises with:
- Working code that runs without errors
- Comments explaining your approach
- Test output demonstrating functionality

---

[← Back to Module 1](../README.md) | [Next Exercise: Message Properties →](./ex_02_properties.md)
