# Module 3 Quiz: Messaging Patterns

Test your understanding of work queues, pub/sub, routing, topics, and RPC patterns.

**Instructions:**
- 15 questions, approximately 20 minutes
- Mix of conceptual and code-based questions
- Check your answers at the end
- Target: 80% (12/15) before proceeding to Module 4

---

## Section 1: Conceptual questions (6 questions)

### Question 1

In a Work Queue pattern with 3 workers and `prefetch_count=1`, you publish 6 messages. How are they distributed?

a) All 6 go to the first available worker
b) Each worker gets exactly 2 messages immediately
c) Workers receive 1 message at a time, getting the next after acknowledging
d) Messages are randomly distributed

### Question 2

What is the key difference between Work Queues and Pub/Sub?

a) Work Queues use exchanges; Pub/Sub doesn't
b) In Work Queues, each message goes to one consumer; in Pub/Sub, each message goes to all subscribers
c) Pub/Sub is faster than Work Queues
d) Work Queues require durable queues; Pub/Sub doesn't

### Question 3

For a topic exchange, which pattern matches the routing key `order.created.us`?

a) `order.*`
b) `order.*.us`
c) `*.created`
d) `created.#`

### Question 4

In the RPC pattern, what is the purpose of the `correlation_id`?

a) To track message delivery status
b) To match responses with their original requests
c) To prioritize messages
d) To route messages to the correct queue

### Question 5

Which exchange type should you use for a logging system where you want to route logs to different queues based on exact severity levels (error, warning, info)?

a) Fanout
b) Topic
c) Direct
d) Headers

### Question 6

When using Pub/Sub with temporary queues (`queue='', exclusive=True`), what happens to messages published while a subscriber is disconnected?

a) Messages are stored until the subscriber reconnects
b) Messages are lost - they're only delivered to connected subscribers
c) Messages are sent to a dead letter queue
d) RabbitMQ buffers the last 100 messages

---

## Section 2: Code reading (5 questions)

### Question 7

What will happen when this consumer processes a message?

```python
def callback(ch, method, properties, body):
    process(body)
    # No acknowledgment

channel.basic_consume(
    queue='tasks',
    on_message_callback=callback,
    auto_ack=False
)
```

a) Message is acknowledged automatically after callback returns
b) Message remains unacknowledged; will be redelivered if connection closes
c) Message is deleted from the queue
d) An error is raised

### Question 8

Given this topic exchange setup, which queues receive a message with `routing_key='api.auth.error'`?

```python
channel.queue_bind(exchange='logs', queue='all_logs', routing_key='#')
channel.queue_bind(exchange='logs', queue='api_logs', routing_key='api.#')
channel.queue_bind(exchange='logs', queue='errors', routing_key='*.*.error')
channel.queue_bind(exchange='logs', queue='auth', routing_key='*.auth.*')
```

a) Only `all_logs`
b) `all_logs` and `api_logs`
c) `all_logs`, `api_logs`, `errors`, and `auth`
d) `all_logs`, `api_logs`, and `errors`

### Question 9

What is wrong with this RPC client code?

```python
class RpcClient:
    def call(self, request):
        corr_id = str(uuid.uuid4())

        self.channel.basic_publish(
            exchange='',
            routing_key='rpc_queue',
            properties=pika.BasicProperties(
                correlation_id=corr_id
                # Missing reply_to!
            ),
            body=request
        )

        # Wait for response...
```

a) Nothing is wrong
b) Missing `reply_to` property - server doesn't know where to send response
c) Missing `delivery_mode` property
d) `correlation_id` should be an integer

### Question 10

What does `channel.basic_qos(prefetch_count=10)` do?

a) Limits the queue to 10 messages
b) Limits the consumer to acknowledge within 10 seconds
c) Limits the consumer to 10 unacknowledged messages at a time
d) Creates 10 parallel consumers

### Question 11

In this routing setup, what happens to a message with `routing_key='payment'`?

```python
channel.exchange_declare(exchange='orders', exchange_type='direct')
channel.queue_bind(exchange='orders', queue='order_queue', routing_key='order')
channel.queue_bind(exchange='orders', queue='refund_queue', routing_key='refund')
```

a) Goes to `order_queue`
b) Goes to `refund_queue`
c) Goes to both queues
d) Is discarded (no matching binding)

---

## Section 3: Problem solving (4 questions)

### Question 12

You're designing a notification system where:
- User events (created, updated, deleted) should notify the email service
- Order events (created, shipped, delivered) should notify the SMS service
- All events should be logged

Which exchange type and binding patterns work best?

a) Fanout exchange (broadcasts everything)
b) Direct exchange with bindings for each event type
c) Topic exchange: `user.*` → email, `order.*` → SMS, `#` → logging
d) Headers exchange with x-match=any

### Question 13

You have a work queue processing images. Processing takes 5-30 seconds per image. Workers occasionally crash. Which configuration ensures no image is lost?

a)
```python
channel.queue_declare(queue='images')
channel.basic_consume(queue='images', auto_ack=True)
```

b)
```python
channel.queue_declare(queue='images', durable=True)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='images', auto_ack=False)
# Acknowledge AFTER processing completes
```

c)
```python
channel.queue_declare(queue='images', exclusive=True)
channel.basic_consume(queue='images', auto_ack=True)
```

d)
```python
channel.queue_declare(queue='images', auto_delete=True)
channel.basic_consume(queue='images', auto_ack=False)
```

### Question 14

An RPC client is waiting for a response, but the server crashed. What should the client do?

a) Wait indefinitely - the server will eventually recover
b) Use a timeout; if exceeded, retry or return an error
c) Close the connection immediately
d) Publish the request again without waiting

### Question 15

You need to route messages where:
- `log.app.api.error` goes to error alerts
- `log.app.api.info` goes to analytics
- `log.app.db.warning` goes to DBA team
- All `log.*` should also go to the archive

Which binding patterns achieve this with a topic exchange?

a)
```python
channel.queue_bind(exchange='logs', queue='errors', routing_key='*.error')
channel.queue_bind(exchange='logs', queue='analytics', routing_key='*.info')
channel.queue_bind(exchange='logs', queue='dba', routing_key='*.db.*')
channel.queue_bind(exchange='logs', queue='archive', routing_key='log.*')
```

b)
```python
channel.queue_bind(exchange='logs', queue='errors', routing_key='#.error')
channel.queue_bind(exchange='logs', queue='analytics', routing_key='#.info')
channel.queue_bind(exchange='logs', queue='dba', routing_key='log.app.db.*')
channel.queue_bind(exchange='logs', queue='archive', routing_key='log.#')
```

c)
```python
channel.queue_bind(exchange='logs', queue='errors', routing_key='log.app.api.error')
channel.queue_bind(exchange='logs', queue='analytics', routing_key='log.app.api.info')
channel.queue_bind(exchange='logs', queue='dba', routing_key='log.app.db.warning')
channel.queue_bind(exchange='logs', queue='archive', routing_key='#')
```

d)
```python
channel.queue_bind(exchange='logs', queue='errors', routing_key='error')
channel.queue_bind(exchange='logs', queue='analytics', routing_key='info')
channel.queue_bind(exchange='logs', queue='dba', routing_key='warning')
channel.queue_bind(exchange='logs', queue='archive', routing_key='log')
```

---

## Answers

<details>
<summary>Click to reveal answers and explanations</summary>

### Question 1: **c**
With `prefetch_count=1`, each worker receives only 1 unacknowledged message at a time. They process, acknowledge, then receive the next. This ensures fair dispatch - slow workers don't accumulate messages.

### Question 2: **b**
In Work Queues, each message is delivered to exactly one consumer (round-robin). In Pub/Sub, each message is delivered to ALL subscribed consumers (each has their own queue).

### Question 3: **b**
`order.*.us` matches `order.created.us` - the `*` matches exactly one word (`created`). Options a and c don't have enough words, and d has them in wrong order.

### Question 4: **b**
The `correlation_id` is included in both request and response, allowing the client to match incoming responses with the requests that generated them. This is essential when multiple RPC calls are in flight.

### Question 5: **c**
Direct exchange routes by exact routing key match, perfect for discrete categories like log levels. Topic would work but is overkill. Fanout would send everything everywhere.

### Question 6: **b**
Temporary exclusive queues are deleted when the connection closes. Any messages published while disconnected are delivered to existing queues only - there's no queue to receive them for the disconnected subscriber.

### Question 7: **b**
With `auto_ack=False`, the message stays unacknowledged. If the connection closes (or consumer crashes), RabbitMQ redelivers the message to another consumer. This is the safe approach but requires explicit acknowledgment.

### Question 8: **c**
All four queues receive it:
- `all_logs`: `#` matches everything
- `api_logs`: `api.#` matches `api.auth.error`
- `errors`: `*.*.error` matches three words ending in `error`
- `auth`: `*.auth.*` matches `api.auth.error`

### Question 9: **b**
Without `reply_to`, the server doesn't know where to send the response. The `correlation_id` identifies the request, but `reply_to` specifies the callback queue.

### Question 10: **c**
`prefetch_count=10` means the consumer can have up to 10 unacknowledged messages. RabbitMQ won't send more until some are acknowledged. This controls flow and enables fair dispatch.

### Question 11: **d**
Direct exchange requires exact routing key match. There's no binding for `payment`, so the message is discarded. Direct exchanges don't have a fallback behavior.

### Question 12: **c**
Topic exchange with patterns provides the right flexibility:
- `user.*` catches user.created, user.updated, user.deleted → email
- `order.*` catches order.created, order.shipped, order.delivered → SMS
- `#` catches everything → logging

### Question 13: **b**
Correct configuration:
- Durable queue survives broker restart
- `prefetch_count=1` ensures only one message at a time
- `auto_ack=False` with manual acknowledgment AFTER processing ensures the message isn't lost if worker crashes

### Question 14: **b**
Always use timeouts in RPC. If the timeout expires, return an error or retry. Waiting indefinitely can hang your application. Message TTL (`expiration` property) also helps prevent stale requests.

### Question 15: **b**
Correct patterns:
- `#.error` matches `log.app.api.error` (zero or more words before `error`)
- `#.info` matches `log.app.api.info`
- `log.app.db.*` matches `log.app.db.warning` specifically
- `log.#` matches all log messages for archive

Option a's patterns don't have enough words. Option c would work but the archive uses `#` which catches non-log messages too. Option d uses exact matches without structure.

---

### Score interpretation

- **13-15 correct**: Excellent! You understand messaging patterns well. Proceed to Module 4.
- **10-12 correct**: Good understanding. Review topics and RPC patterns before continuing.
- **7-9 correct**: Fair. Re-read the pattern lessons and do the exercises.
- **Below 7**: Review Module 3 thoroughly before attempting Module 4.

</details>

---

[← Back to Module 3](./README.md) | [Proceed to Module 4 →](../module_4_production/README.md)
