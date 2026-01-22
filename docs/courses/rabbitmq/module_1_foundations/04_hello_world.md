# Hello World: Your First Producer and Consumer

In this lesson, you write your first RabbitMQ programs - a producer that sends messages and a consumer that receives them. This is the foundation for all RabbitMQ patterns.

## Overview

The "Hello World" of messaging involves two programs:

```
┌──────────┐     ┌────────────┐     ┌─────────┐     ┌──────────┐
│  send.py │────▶│  RabbitMQ  │────▶│  hello  │────▶│receive.py│
│(producer)│     │            │     │ (queue) │     │(consumer)│
└──────────┘     └────────────┘     └─────────┘     └──────────┘
```

1. **send.py** - Publishes a message to a queue
2. **receive.py** - Consumes messages from the queue

## Prerequisites

Ensure RabbitMQ is running:

```bash
# Check container is running
docker ps | grep rabbitmq

# If not running, start it
docker start rabbitmq
# Or: docker-compose up -d
```

## Part 1: The producer (send.py)

The producer connects to RabbitMQ, declares a queue, and sends a message.

### Create send.py

```python
#!/usr/bin/env python
"""
send.py - Simple producer that sends a message to a queue.

This is the "Hello World" producer for RabbitMQ.
It connects to RabbitMQ, declares a queue, and publishes one message.
"""
import pika


def main():
    # Step 1: Create a connection to RabbitMQ
    # ConnectionParameters defaults to localhost:5672
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost')
    )

    # Step 2: Create a channel
    # Channels are where most of the API lives
    channel = connection.channel()

    # Step 3: Declare a queue named 'hello'
    # queue_declare is idempotent - safe to call multiple times
    # If the queue doesn't exist, it will be created
    channel.queue_declare(queue='hello')

    # Step 4: Publish a message
    # exchange='' means use the default exchange
    # routing_key='hello' routes to the 'hello' queue
    message = 'Hello World!'
    channel.basic_publish(
        exchange='',           # Default exchange
        routing_key='hello',   # Queue name
        body=message           # Message content
    )

    print(f" [x] Sent '{message}'")

    # Step 5: Close the connection
    # This also closes all channels
    connection.close()


if __name__ == '__main__':
    main()
```

### Understanding the producer

**Step 1: Connection**
```python
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost')
)
```
- Creates a TCP connection to the RabbitMQ server
- `BlockingConnection` is synchronous (simplest to use)
- Default port is 5672

**Step 2: Channel**
```python
channel = connection.channel()
```
- Creates a virtual connection within the TCP connection
- All operations happen on channels, not connections

**Step 3: Queue declaration**
```python
channel.queue_declare(queue='hello')
```
- Creates the queue if it doesn't exist
- Does nothing if queue already exists (idempotent)
- Important: Both producer and consumer should declare the queue

**Step 4: Publishing**
```python
channel.basic_publish(
    exchange='',
    routing_key='hello',
    body=message
)
```
- `exchange=''` - Uses the default (nameless) exchange
- `routing_key='hello'` - With default exchange, this is the queue name
- `body` - The message content (bytes or string)

### Run the producer

```bash
python send.py
```

**Expected output:**
```
 [x] Sent 'Hello World!'
```

### Verify in Management UI

1. Go to http://localhost:15672
2. Click **Queues** tab
3. You should see the `hello` queue with 1 message

```
┌──────────────────────────────────────────────────────────────┐
│ Queues                                                        │
├──────────────────────────────────────────────────────────────┤
│ Name    │ Type    │ State   │ Ready │ Unacked │ Total        │
│ hello   │ classic │ running │ 1     │ 0       │ 1            │
└──────────────────────────────────────────────────────────────┘
```

## Part 2: The consumer (receive.py)

The consumer connects to RabbitMQ, subscribes to the queue, and processes messages.

### Create receive.py

```python
#!/usr/bin/env python
"""
receive.py - Simple consumer that receives messages from a queue.

This is the "Hello World" consumer for RabbitMQ.
It connects to RabbitMQ, subscribes to a queue, and processes messages.
The consumer runs continuously until interrupted (Ctrl+C).
"""
import pika


def callback(ch, method, properties, body):
    """
    Callback function called for each message received.

    Args:
        ch: Channel object
        method: Delivery metadata (delivery_tag, exchange, routing_key)
        properties: Message properties (content_type, headers, etc.)
        body: Message body (bytes)
    """
    print(f" [x] Received '{body.decode()}'")


def main():
    # Step 1: Create a connection to RabbitMQ
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost')
    )

    # Step 2: Create a channel
    channel = connection.channel()

    # Step 3: Declare the queue (same as producer)
    # This ensures the queue exists before we try to consume from it
    channel.queue_declare(queue='hello')

    # Step 4: Set up subscription
    # Tell RabbitMQ to call our callback function for each message
    channel.basic_consume(
        queue='hello',              # Queue to consume from
        on_message_callback=callback,  # Function to call
        auto_ack=True               # Automatic acknowledgment
    )

    # Step 5: Start consuming
    # This is a blocking call - the program will wait for messages
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nInterrupted')
```

### Understanding the consumer

**Step 3: Queue declaration (again)**
```python
channel.queue_declare(queue='hello')
```
- Consumer also declares the queue
- This is **defensive programming** - consumer might start before producer
- If producer already created the queue, this does nothing

**Step 4: Setting up the callback**
```python
def callback(ch, method, properties, body):
    print(f" [x] Received '{body.decode()}'")

channel.basic_consume(
    queue='hello',
    on_message_callback=callback,
    auto_ack=True
)
```
- `callback` is called for each message
- `body` is bytes, so we decode to string
- `auto_ack=True` - Message is acknowledged automatically upon delivery

**Step 5: Start consuming**
```python
channel.start_consuming()
```
- This is a **blocking call**
- The program waits here for messages
- Each message triggers the callback
- Press Ctrl+C to stop

### Run the consumer

Open a **new terminal** and run:

```bash
python receive.py
```

**Expected output:**
```
 [*] Waiting for messages. To exit press CTRL+C
 [x] Received 'Hello World!'
```

The message we sent earlier is now consumed!

## Part 3: Interactive testing

Let's see the real-time interaction between producer and consumer.

### Terminal 1: Start the consumer

```bash
python receive.py
# Waiting for messages...
```

### Terminal 2: Send multiple messages

```bash
python send.py
python send.py
python send.py
```

### Terminal 1: Watch messages arrive

```
 [*] Waiting for messages. To exit press CTRL+C
 [x] Received 'Hello World!'
 [x] Received 'Hello World!'
 [x] Received 'Hello World!'
```

## Part 4: Enhanced producer with custom messages

Let's make the producer more useful by accepting command-line arguments:

### Create send_message.py

```python
#!/usr/bin/env python
"""
send_message.py - Producer that sends custom messages.

Usage: python send_message.py "Your message here"
"""
import sys
import pika


def send_message(message: str) -> None:
    """Send a message to the hello queue."""
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost')
    )
    channel = connection.channel()
    channel.queue_declare(queue='hello')

    channel.basic_publish(
        exchange='',
        routing_key='hello',
        body=message
    )

    print(f" [x] Sent '{message}'")
    connection.close()


def main():
    # Get message from command line, or use default
    message = ' '.join(sys.argv[1:]) or 'Hello World!'
    send_message(message)


if __name__ == '__main__':
    main()
```

### Test custom messages

```bash
# Terminal 1: Consumer running
python receive.py

# Terminal 2: Send custom messages
python send_message.py Hello from Python!
python send_message.py "This is a longer message with spaces"
python send_message.py Order #12345 has been placed
```

**Consumer output:**
```
 [x] Received 'Hello from Python!'
 [x] Received 'This is a longer message with spaces'
 [x] Received 'Order #12345 has been placed'
```

## Part 5: Understanding message persistence

Currently, our messages are transient - they're lost if RabbitMQ restarts.

### Test message loss

```bash
# Send a message while consumer is stopped
python send.py

# Check queue has 1 message
# Management UI > Queues > hello > Ready: 1

# Restart RabbitMQ
docker restart rabbitmq
# Wait 10 seconds

# Check queue again
# Messages are gone! Ready: 0
```

### Why? Two reasons:

1. **Queue is not durable** - Queue definition lost on restart
2. **Message is not persistent** - Message not written to disk

We'll fix this in the next lesson when we cover message properties in depth.

## Common patterns you've learned

### Pattern 1: Fire and forget

```python
# Producer sends and doesn't wait
channel.basic_publish(exchange='', routing_key='queue', body=msg)
connection.close()  # Done, don't care about confirmation
```

### Pattern 2: Long-running consumer

```python
# Consumer runs forever, processing messages as they arrive
channel.start_consuming()  # Blocks until Ctrl+C
```

### Pattern 3: Defensive queue declaration

```python
# Both producer and consumer declare the queue
# Whoever runs first creates it
channel.queue_declare(queue='my_queue')
```

## Exercises

1. **Multiple consumers**: Start 3 consumers, then send 5 messages. Which consumer gets which message?

2. **Message order**: Send messages "1", "2", "3", "4", "5". Are they received in order?

3. **Consumer crashes**: Start consumer, stop it (Ctrl+C), send messages, restart consumer. What happens to messages?

4. **Custom queue**: Modify the code to use a queue named "greetings" instead of "hello".

## Key takeaways

1. **Producers send to exchanges** - Even the "default" exchange
2. **Consumers subscribe to queues** - Using `basic_consume`
3. **Queue declaration is idempotent** - Both sides should declare
4. **Consumers are long-running** - `start_consuming()` blocks
5. **auto_ack=True is dangerous** - We'll fix this in the next module
6. **Messages are transient by default** - Need explicit persistence

## What's next?

In the next lesson, you'll learn the Python Pika library in depth - connection parameters, message properties, error handling, and best practices.

---

[← Previous: Installation](./03_installation.md) | [Back to Module 1](./README.md) | [Next: Python Pika →](./05_python_pika.md)
