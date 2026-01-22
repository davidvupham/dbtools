# Module 1 Quiz: Foundations

Test your understanding of RabbitMQ basics: message brokers, producers, consumers, connections, channels, and the Pika library.

**Instructions:**
- 15 questions, approximately 20 minutes
- Mix of conceptual and code-based questions
- Check your answers at the end
- Target: 80% (12/15) before proceeding to Module 2

---

## Section 1: Conceptual questions (6 questions)

### Question 1

What is the PRIMARY benefit of using a message broker between services?

a) It makes services run faster
b) It eliminates the need for error handling
c) It decouples services so they can operate independently
d) It reduces network traffic

### Question 2

In RabbitMQ, which component is responsible for routing messages to queues?

a) Producer
b) Consumer
c) Exchange
d) Channel

### Question 3

What is the difference between a Connection and a Channel in RabbitMQ?

a) They are the same thing
b) A Connection is a TCP socket; a Channel is a virtual connection within it
c) A Channel is a TCP socket; a Connection is a virtual connection within it
d) Connections are for producers; Channels are for consumers

### Question 4

What happens to unacknowledged messages when a consumer's connection closes unexpectedly?

a) Messages are permanently lost
b) Messages are deleted from the queue
c) Messages are requeued and delivered to another consumer
d) Messages remain unacknowledged forever

### Question 5

Which statement about `auto_ack=True` is correct?

a) It is the recommended setting for production
b) Messages are acknowledged after the callback completes
c) Messages are acknowledged immediately upon delivery, before processing
d) It enables manual acknowledgment

### Question 6

What does `delivery_mode=2` (persistent) do to a message?

a) Guarantees the message will be delivered
b) Writes the message to disk for durability
c) Makes the message higher priority
d) Encrypts the message

---

## Section 2: Code reading (5 questions)

### Question 7

What is wrong with this producer code?

```python
import pika

connection = pika.BlockingConnection()
channel = connection.channel()

for i in range(1000):
    connection = pika.BlockingConnection()
    channel = connection.channel()
    channel.basic_publish(exchange='', routing_key='queue', body=f'msg{i}')
    connection.close()
```

a) Nothing is wrong
b) Creating a new connection for each message is inefficient
c) The queue is not declared
d) Both b and c

### Question 8

What will this consumer do?

```python
def callback(ch, method, properties, body):
    raise Exception("Processing failed!")

channel.basic_consume(
    queue='tasks',
    on_message_callback=callback,
    auto_ack=True
)
```

a) Requeue the message for retry
b) Send the message to a dead letter queue
c) Lose the message because auto_ack=True acknowledges before processing
d) Keep the message unacknowledged

### Question 9

What does this code output?

```python
import pika

connection = pika.BlockingConnection()
channel = connection.channel()
result = channel.queue_declare(queue='', exclusive=True)
print(result.method.queue)
```

a) An empty string
b) `None`
c) A RabbitMQ-generated unique queue name like `amq.gen-JzTY...`
d) An error because queue name is empty

### Question 10

What properties are set on this message?

```python
properties = pika.BasicProperties(
    delivery_mode=2,
    content_type='application/json',
    expiration='60000'
)
```

a) Persistent message, JSON content, expires in 60 seconds
b) Transient message, JSON content, expires in 60000 seconds
c) Persistent message, JSON content, expires in 60000 milliseconds
d) Persistent message, JSON content, priority 60000

### Question 11

What is the purpose of `prefetch_count` in this code?

```python
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='tasks', on_message_callback=callback, auto_ack=False)
```

a) Limits the queue to 1 message total
b) Limits the consumer to process 1 message per second
c) Limits the consumer to 1 unacknowledged message at a time
d) Creates 1 replica of the queue

---

## Section 3: Problem solving (4 questions)

### Question 12

You need to ensure messages survive a RabbitMQ restart. Which combination is required?

a) Durable queue only
b) Persistent messages only
c) Both durable queue AND persistent messages
d) Exclusive queue with persistent messages

### Question 13

Which approach correctly handles a message processing failure?

a)
```python
def callback(ch, method, properties, body):
    try:
        process(body)
    except Exception:
        pass  # Ignore errors
    ch.basic_ack(delivery_tag=method.delivery_tag)
```

b)
```python
def callback(ch, method, properties, body):
    try:
        process(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception:
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
```

c)
```python
def callback(ch, method, properties, body):
    process(body)  # Let exception propagate
```

d)
```python
def callback(ch, method, properties, body):
    ch.basic_ack(delivery_tag=method.delivery_tag)
    process(body)
```

### Question 14

You have 3 consumers subscribed to the same queue. You publish 6 messages. With default settings, how are messages distributed?

a) All 6 messages go to one consumer
b) Each consumer gets 2 messages (round-robin)
c) Messages are distributed based on consumer processing speed
d) Messages are duplicated to all consumers

### Question 15

Which connection pattern is most efficient for a producer that sends 100 messages?

a)
```python
for msg in messages:
    conn = pika.BlockingConnection()
    ch = conn.channel()
    ch.basic_publish(...)
    conn.close()
```

b)
```python
conn = pika.BlockingConnection()
ch = conn.channel()
for msg in messages:
    ch.basic_publish(...)
conn.close()
```

c)
```python
conn = pika.BlockingConnection()
for msg in messages:
    ch = conn.channel()
    ch.basic_publish(...)
conn.close()
```

d) All patterns have equal performance

---

## Answers

<details>
<summary>Click to reveal answers and explanations</summary>

### Question 1: **c**
Message brokers decouple services, allowing them to operate independently. Services don't need to know about each other, and one can be down without affecting the other.

### Question 2: **c**
Exchanges are responsible for routing messages to queues based on bindings and routing keys. Producers send to exchanges, not directly to queues.

### Question 3: **b**
A Connection is a TCP socket between your application and RabbitMQ. Channels are virtual connections multiplexed over a single TCP connection, allowing concurrent operations without the overhead of multiple TCP connections.

### Question 4: **c**
When a consumer disconnects without acknowledging, RabbitMQ requeues the messages and delivers them to another available consumer (or the same consumer when it reconnects).

### Question 5: **c**
With `auto_ack=True`, messages are acknowledged immediately upon delivery, before the callback even starts. If processing fails, the message is already gone.

### Question 6: **b**
`delivery_mode=2` (persistent) writes the message to disk. Combined with a durable queue, this ensures messages survive broker restarts. Note: It doesn't guarantee delivery in case of disk failure.

### Question 7: **d**
Both issues exist: Creating a new connection for each message is extremely inefficient (connections are expensive TCP sockets), and the queue is never declared, which may cause errors if the queue doesn't exist.

### Question 8: **c**
With `auto_ack=True`, the message is acknowledged immediately when delivered, before the callback runs. When the exception occurs, the message is already gone from the queue.

### Question 9: **c**
When `queue=''` and `exclusive=True`, RabbitMQ generates a unique queue name. This pattern is used for temporary, private queues (often for RPC responses).

### Question 10: **a**
The message is persistent (`delivery_mode=2`), has JSON content type, and expires in 60 seconds. The `expiration` property is in milliseconds, so 60000ms = 60 seconds.

### Question 11: **c**
`prefetch_count=1` limits the consumer to having only 1 unacknowledged message at a time. This enables fair dispatch - a slow consumer won't accumulate messages while faster consumers are idle.

### Question 12: **c**
Both conditions are required: the queue must be declared with `durable=True` (so the queue definition survives restart), AND messages must be published with `delivery_mode=2` (so message content is persisted to disk).

### Question 13: **b**
Option b correctly acknowledges on success and negative-acknowledges on failure. Option a loses the error. Option c lets the exception crash the consumer. Option d acknowledges before processing (message lost if processing fails).

### Question 14: **b**
By default, RabbitMQ distributes messages round-robin to consumers subscribed to the same queue. Each consumer gets approximately equal messages regardless of processing speed (unless `prefetch_count` is set).

### Question 15: **b**
Reusing one connection and one channel for all messages is most efficient. Option a creates 100 connections (very expensive). Option c creates 100 channels (unnecessary overhead). Connections are expensive; reuse them.

---

### Score interpretation

- **13-15 correct**: Excellent! You have a solid foundation. Proceed to Module 2.
- **10-12 correct**: Good understanding. Review the topics you missed before continuing.
- **7-9 correct**: Fair. Re-read the relevant lessons and redo the exercises.
- **Below 7**: Review Module 1 thoroughly before attempting Module 2.

</details>

---

[← Back to Module 1](./README.md) | [Proceed to Module 2 →](../module_2_core_concepts/README.md)
