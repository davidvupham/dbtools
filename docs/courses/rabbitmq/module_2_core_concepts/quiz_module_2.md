# Module 2 Quiz: Core Concepts

Test your understanding of the AMQP model, exchanges, queues, bindings, and message properties.

**Instructions:**
- 15 questions, approximately 20 minutes
- Mix of conceptual and code-based questions
- Check your answers at the end
- Target: 80% (12/15) before proceeding to Module 3

---

## Section 1: Conceptual questions (6 questions)

### Question 1

In the AMQP model, which component is responsible for storing messages until they are consumed?

a) Exchange
b) Binding
c) Queue
d) Channel

### Question 2

Which exchange type should you use to broadcast a message to ALL bound queues, regardless of routing key?

a) Direct
b) Topic
c) Fanout
d) Headers

### Question 3

For a topic exchange, what does the binding pattern `order.#` match?

a) Only `order`
b) `order.created` but not `order.item.added`
c) `order`, `order.created`, and `order.item.added`
d) Only routing keys starting with `#`

### Question 4

What TWO things are required for a message to survive a RabbitMQ broker restart?

a) Durable exchange and persistent message
b) Durable queue and persistent message
c) Exclusive queue and durable exchange
d) Auto-delete queue and durable binding

### Question 5

What is the difference between a "routing key" and a "binding key"?

a) They are the same thing
b) Routing key is on the message; binding key is on the binding rule
c) Binding key is on the message; routing key is on the binding rule
d) Routing key is for topic exchanges; binding key is for direct exchanges

### Question 6

What happens to messages in a queue when the queue's TTL expires?

a) Messages are deleted immediately
b) Messages are returned to the publisher
c) Messages are moved to a dead letter exchange (if configured)
d) Nothing, queue TTL only affects the queue, not messages

---

## Section 2: Code reading (5 questions)

### Question 7

What type of queue does this declaration create?

```python
result = channel.queue_declare(queue='', exclusive=True)
```

a) A permanent queue named '' (empty string)
b) A temporary queue with an auto-generated name, deleted when connection closes
c) A durable queue visible to all connections
d) An error - queue name cannot be empty

### Question 8

Given this setup, which queue(s) will receive a message with `routing_key='user.created'`?

```python
channel.exchange_declare(exchange='events', exchange_type='topic')
channel.queue_bind(exchange='events', queue='all_events', routing_key='#')
channel.queue_bind(exchange='events', queue='user_events', routing_key='user.*')
channel.queue_bind(exchange='events', queue='creations', routing_key='*.created')
```

a) Only `all_events`
b) `all_events` and `user_events`
c) `all_events`, `user_events`, and `creations`
d) Only `user_events` and `creations`

### Question 9

What is wrong with this persistence setup?

```python
channel.queue_declare(queue='important', durable=False)

channel.basic_publish(
    exchange='',
    routing_key='important',
    body='data',
    properties=pika.BasicProperties(delivery_mode=2)
)
```

a) Nothing is wrong
b) The queue is not durable, so messages will be lost on restart despite being persistent
c) `delivery_mode=2` is invalid
d) Cannot publish to the default exchange

### Question 10

What does the `expiration` property do?

```python
properties = pika.BasicProperties(expiration='30000')
```

a) Message expires after 30000 seconds
b) Message expires after 30000 milliseconds (30 seconds)
c) Queue expires after 30000 milliseconds
d) Consumer must acknowledge within 30000 milliseconds

### Question 11

Which messages will be routed to `pdf_reports` queue?

```python
channel.exchange_declare(exchange='reports', exchange_type='headers')
channel.queue_bind(
    exchange='reports',
    queue='pdf_reports',
    arguments={
        'x-match': 'all',
        'format': 'pdf',
        'department': 'finance'
    }
)
```

a) Messages with header `format='pdf'` OR `department='finance'`
b) Messages with header `format='pdf'` AND `department='finance'`
c) All messages (headers exchange matches everything)
d) No messages (invalid binding)

---

## Section 3: Problem solving (4 questions)

### Question 12

You need to implement a logging system where:
- All services publish logs to one exchange
- Error logs go to `error_queue`
- All logs go to `all_logs_queue`

Which exchange type and bindings should you use?

a) Fanout exchange with two bindings
b) Direct exchange: bind `error_queue` to `error`, bind `all_logs_queue` to `error`, `warning`, and `info`
c) Topic exchange: bind `error_queue` to `*.error`, bind `all_logs_queue` to `#`
d) Headers exchange with `x-match=any`

### Question 13

You want to create a queue that:
- Survives broker restarts
- Has a maximum of 10,000 messages
- Dead-letters rejected messages

Which declaration is correct?

a)
```python
channel.queue_declare(
    queue='tasks',
    durable=True,
    arguments={
        'x-max-length': 10000,
        'x-dead-letter-exchange': 'dlx'
    }
)
```

b)
```python
channel.queue_declare(
    queue='tasks',
    durable=False,
    auto_delete=True,
    arguments={
        'x-max-length': 10000,
        'x-dead-letter-exchange': 'dlx'
    }
)
```

c)
```python
channel.queue_declare(
    queue='tasks',
    exclusive=True,
    arguments={
        'x-max-length': 10000
    }
)
```

d)
```python
channel.queue_declare(
    queue='tasks',
    durable=True
)
```

### Question 14

For an RPC pattern, which message properties are essential for the client to correlate responses?

a) `message_id` and `timestamp`
b) `correlation_id` and `reply_to`
c) `type` and `app_id`
d) `priority` and `expiration`

### Question 15

You have a topic exchange with this binding:

```python
channel.queue_bind(
    exchange='logs',
    queue='critical_only',
    routing_key='*.*.critical'
)
```

Which of these routing keys will match?

a) `app.critical`
b) `app.db.critical`
c) `critical`
d) `app.db.server.critical`

---

## Answers

<details>
<summary>Click to reveal answers and explanations</summary>

### Question 1: **c**
Queues store messages. Exchanges route messages. Bindings are rules. Channels are virtual connections.

### Question 2: **c**
Fanout exchanges broadcast to all bound queues, ignoring the routing key entirely. Direct requires exact match, Topic uses patterns, Headers uses message headers.

### Question 3: **c**
The `#` wildcard matches zero or more words. So `order.#` matches `order` (zero words after), `order.created` (one word), and `order.item.added` (two words).

### Question 4: **b**
For messages to survive restart, you need: (1) durable queue (`durable=True`) AND (2) persistent messages (`delivery_mode=2`). Exchange durability is separate from message durability.

### Question 5: **b**
The routing key is attached to the message when publishing. The binding key is specified when creating a binding between an exchange and queue. The exchange compares them to route messages.

### Question 6: **c**
When messages expire (due to message TTL or queue TTL), they are moved to the dead letter exchange if one is configured. Otherwise, they are discarded.

### Question 7: **b**
`queue=''` tells RabbitMQ to generate a unique name. `exclusive=True` means only this connection can use it and it's deleted when the connection closes. This is the pattern for temporary reply queues.

### Question 8: **c**
All three queues receive the message:
- `all_events`: `#` matches everything
- `user_events`: `user.*` matches `user.created` (user + one word)
- `creations`: `*.created` matches `user.created` (one word + created)

### Question 9: **b**
The queue is not durable (`durable=False`), so it will be deleted on broker restart. Even though messages are published with `delivery_mode=2` (persistent), they're stored in a non-durable queue that won't exist after restart.

### Question 10: **b**
The `expiration` property sets message TTL in milliseconds. `30000` ms = 30 seconds. Note: it's a string, not an integer, due to AMQP specification quirks.

### Question 11: **b**
With `x-match: 'all'`, the message must have ALL the specified headers. So it needs BOTH `format='pdf'` AND `department='finance'` to match.

### Question 12: **b** (or **c**)
Both b and c work, but b (direct) is simpler for this case. Direct exchange with explicit bindings for each log level is straightforward. Topic would also work with patterns like `*.error` for errors and `#` for all.

### Question 13: **a**
Option a correctly declares a durable queue with max-length and dead-letter exchange. Option b is not durable. Option c is exclusive (deleted on disconnect). Option d lacks the arguments.

### Question 14: **b**
`correlation_id` lets the client match responses to requests. `reply_to` tells the server where to send the response. These are the essential RPC properties.

### Question 15: **b**
The pattern `*.*.critical` requires exactly three words separated by dots, with the last word being `critical`. Only `app.db.critical` matches. Option a has 2 words, c has 1 word, d has 4 words.

---

### Score interpretation

- **13-15 correct**: Excellent! You have a solid understanding. Proceed to Module 3.
- **10-12 correct**: Good understanding. Review the topics you missed before continuing.
- **7-9 correct**: Fair. Re-read the relevant lessons and redo the exercises.
- **Below 7**: Review Module 2 thoroughly before attempting Module 3.

</details>

---

[← Back to Module 2](./README.md) | [Proceed to Module 3 →](../module_3_messaging_patterns/README.md)
