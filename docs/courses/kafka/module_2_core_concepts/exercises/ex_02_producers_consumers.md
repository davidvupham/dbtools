# Module 2 exercises: Producers and consumers

**[← Back to Module 2](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

## Overview

These exercises will help you master Kafka producers and consumers through hands-on practice. Complete all exercises to solidify your understanding of core Kafka concepts.

**Prerequisites:**
- Completed Lessons 05-08
- Docker environment running (see [Docker Setup](../../docker/README.md))

---

## Exercise 1: Producer basics

**Objective:** Create a producer that sends messages with keys to control partition assignment.

### Setup

```bash
# Create a topic with 4 partitions
docker exec -it kafka kafka-topics --create --topic orders \
    --bootstrap-server localhost:9092 --partitions 4 --replication-factor 1
```

### Task

Create a Python producer that:
1. Sends 100 order messages
2. Uses the customer ID as the key (ensures same customer goes to same partition)
3. Implements delivery callbacks to track success/failure

### Template

```python
# exercise_producer.py
from confluent_kafka import Producer
import json
import random

def delivery_callback(err, msg):
    """Called when a message is delivered or fails."""
    # TODO: Implement callback
    pass

def create_order(order_id: int) -> dict:
    """Generate a sample order."""
    customers = ['CUST-001', 'CUST-002', 'CUST-003', 'CUST-004', 'CUST-005']
    products = ['laptop', 'phone', 'tablet', 'headphones', 'keyboard']

    return {
        'order_id': f'ORD-{order_id:05d}',
        'customer_id': random.choice(customers),
        'product': random.choice(products),
        'quantity': random.randint(1, 5),
        'price': round(random.uniform(10.0, 500.0), 2)
    }

def main():
    config = {
        'bootstrap.servers': 'localhost:9092',
        # TODO: Add recommended producer settings
    }

    producer = Producer(config)

    # TODO: Send 100 orders with appropriate keys
    # TODO: Track which partitions received messages

    producer.flush()
    print("All messages sent!")

if __name__ == '__main__':
    main()
```

### Expected output

```
Sent ORD-00001 (customer=CUST-003) to partition 2
Sent ORD-00002 (customer=CUST-001) to partition 0
...
Partition distribution:
  Partition 0: 23 messages
  Partition 1: 25 messages
  Partition 2: 28 messages
  Partition 3: 24 messages
```

### Solution

<details>
<summary>Click to reveal solution</summary>

```python
from confluent_kafka import Producer
import json
import random
from collections import defaultdict

partition_counts = defaultdict(int)

def delivery_callback(err, msg):
    if err is not None:
        print(f"Delivery failed: {err}")
    else:
        partition_counts[msg.partition()] += 1
        print(f"Sent {msg.key().decode()} to partition {msg.partition()}")

def create_order(order_id: int) -> dict:
    customers = ['CUST-001', 'CUST-002', 'CUST-003', 'CUST-004', 'CUST-005']
    products = ['laptop', 'phone', 'tablet', 'headphones', 'keyboard']

    return {
        'order_id': f'ORD-{order_id:05d}',
        'customer_id': random.choice(customers),
        'product': random.choice(products),
        'quantity': random.randint(1, 5),
        'price': round(random.uniform(10.0, 500.0), 2)
    }

def main():
    config = {
        'bootstrap.servers': 'localhost:9092',
        'acks': 'all',
        'enable.idempotence': True,
        'retries': 3
    }

    producer = Producer(config)

    for i in range(100):
        order = create_order(i + 1)

        # Use customer_id as key for partition affinity
        producer.produce(
            topic='orders',
            key=order['customer_id'].encode('utf-8'),
            value=json.dumps(order).encode('utf-8'),
            callback=delivery_callback
        )

        # Trigger delivery callbacks
        producer.poll(0)

    producer.flush()

    print("\nPartition distribution:")
    for partition in sorted(partition_counts.keys()):
        print(f"  Partition {partition}: {partition_counts[partition]} messages")

if __name__ == '__main__':
    main()
```

</details>

---

## Exercise 2: Consumer with manual commits

**Objective:** Create a consumer that processes messages and commits offsets manually.

### Task

Create a Python consumer that:
1. Reads from the 'orders' topic
2. Processes each order (simulate with a print statement)
3. Commits offsets after every 10 messages
4. Handles errors gracefully

### Template

```python
# exercise_consumer.py
from confluent_kafka import Consumer, KafkaError
import json

def process_order(order: dict):
    """Process an order (simulated)."""
    # TODO: Add processing logic
    pass

def main():
    config = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'order-processor',
        # TODO: Configure for manual commits
    }

    consumer = Consumer(config)
    consumer.subscribe(['orders'])

    processed = 0

    try:
        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue

            # TODO: Handle errors

            # TODO: Process message

            # TODO: Commit every 10 messages

    except KeyboardInterrupt:
        print(f"\nProcessed {processed} orders")
    finally:
        # TODO: Final commit and cleanup
        pass

if __name__ == '__main__':
    main()
```

### Solution

<details>
<summary>Click to reveal solution</summary>

```python
from confluent_kafka import Consumer, KafkaError
import json

def process_order(order: dict):
    print(f"Processing order {order['order_id']}: "
          f"{order['quantity']}x {order['product']} = ${order['price']}")

def main():
    config = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'order-processor',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': False  # Manual commits
    }

    consumer = Consumer(config)
    consumer.subscribe(['orders'])

    processed = 0
    batch = []

    try:
        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    print(f"Reached end of partition {msg.partition()}")
                else:
                    print(f"Error: {msg.error()}")
                continue

            # Process message
            order = json.loads(msg.value().decode('utf-8'))
            process_order(order)
            processed += 1
            batch.append(msg)

            # Commit every 10 messages
            if len(batch) >= 10:
                consumer.commit(asynchronous=False)
                print(f"Committed {len(batch)} messages (total: {processed})")
                batch = []

    except KeyboardInterrupt:
        print(f"\nProcessed {processed} orders")
    finally:
        # Final commit
        if batch:
            consumer.commit(asynchronous=False)
            print(f"Final commit: {len(batch)} messages")
        consumer.close()

if __name__ == '__main__':
    main()
```

</details>

---

## Exercise 3: Consumer group scaling

**Objective:** Observe how Kafka distributes partitions across multiple consumers.

### Setup

```bash
# Create a high-volume topic
docker exec -it kafka kafka-topics --create --topic high-volume \
    --bootstrap-server localhost:9092 --partitions 6 --replication-factor 1
```

### Task

1. Create a producer that continuously sends messages
2. Start one consumer and observe partition assignment
3. Start a second consumer (same group) and observe rebalancing
4. Stop one consumer and observe rebalancing

### Producer script

```python
# producer_continuous.py
from confluent_kafka import Producer
import time
import json

producer = Producer({'bootstrap.servers': 'localhost:9092'})

count = 0
try:
    while True:
        producer.produce(
            'high-volume',
            key=str(count % 6).encode(),
            value=json.dumps({'id': count, 'timestamp': time.time()}).encode()
        )
        count += 1
        producer.poll(0)

        if count % 100 == 0:
            producer.flush()
            print(f"Sent {count} messages")
            time.sleep(0.1)

except KeyboardInterrupt:
    producer.flush()
    print(f"Total sent: {count}")
```

### Consumer script

```python
# consumer_scaling.py
from confluent_kafka import Consumer
import socket
import os

consumer_id = f"{socket.gethostname()}-{os.getpid()}"

def on_assign(consumer, partitions):
    parts = [p.partition for p in partitions]
    print(f"[{consumer_id}] ASSIGNED: {parts}")

def on_revoke(consumer, partitions):
    parts = [p.partition for p in partitions]
    print(f"[{consumer_id}] REVOKED: {parts}")

config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'scaling-demo',
    'auto.offset.reset': 'latest',
    'partition.assignment.strategy': 'cooperative-sticky'
}

consumer = Consumer(config)
consumer.subscribe(['high-volume'], on_assign=on_assign, on_revoke=on_revoke)

print(f"Consumer {consumer_id} started")

try:
    message_count = 0
    while True:
        msg = consumer.poll(1.0)
        if msg and not msg.error():
            message_count += 1
            if message_count % 100 == 0:
                assignment = [p.partition for p in consumer.assignment()]
                print(f"[{consumer_id}] Processed {message_count}, partitions: {assignment}")
except KeyboardInterrupt:
    pass
finally:
    consumer.close()
```

### Expected observations

1. First consumer gets all 6 partitions
2. When second consumer joins, partitions are redistributed (3 each)
3. When one consumer stops, remaining consumer gets all partitions back

---

## Exercise 4: Exactly-once processing simulation

**Objective:** Implement idempotent message processing using a deduplication strategy.

### Scenario

Process payment events exactly once, even if the consumer restarts and reprocesses messages.

### Task

Create a consumer that:
1. Tracks processed message IDs in a set (simulating a database)
2. Skips messages that have already been processed
3. Demonstrates idempotent behavior

### Template

```python
# exercise_exactly_once.py
from confluent_kafka import Consumer, Producer
import json
import uuid

# Simulated "database" of processed IDs
processed_ids = set()

def is_duplicate(message_id: str) -> bool:
    """Check if message was already processed."""
    # TODO: Implement
    pass

def mark_processed(message_id: str):
    """Mark message as processed."""
    # TODO: Implement
    pass

def process_payment(payment: dict) -> bool:
    """Process a payment event. Returns True if processed, False if duplicate."""
    # TODO: Implement idempotent processing
    pass

def main():
    # First, produce some test messages
    producer = Producer({'bootstrap.servers': 'localhost:9092'})

    # Create topic
    # (In real scenario, topic already exists)

    # Send 10 payment events
    for i in range(10):
        payment = {
            'payment_id': str(uuid.uuid4()),
            'amount': 100.00 + i,
            'customer': f'CUST-{i:03d}'
        }
        producer.produce(
            'payments',
            key=payment['payment_id'].encode(),
            value=json.dumps(payment).encode()
        )
    producer.flush()

    # Now consume (simulating restart by consuming twice)
    # TODO: Implement consumer that processes each payment exactly once

if __name__ == '__main__':
    main()
```

### Solution

<details>
<summary>Click to reveal solution</summary>

```python
from confluent_kafka import Consumer, Producer
import json
import uuid

# Simulated "database" of processed IDs
processed_ids = set()

def is_duplicate(message_id: str) -> bool:
    return message_id in processed_ids

def mark_processed(message_id: str):
    processed_ids.add(message_id)

def process_payment(payment: dict) -> bool:
    payment_id = payment['payment_id']

    if is_duplicate(payment_id):
        print(f"SKIP (duplicate): {payment_id}")
        return False

    # Process the payment
    print(f"PROCESS: {payment_id} - ${payment['amount']} from {payment['customer']}")

    # Mark as processed AFTER successful processing
    mark_processed(payment_id)
    return True

def main():
    # Create topic
    import subprocess
    subprocess.run([
        'docker', 'exec', 'kafka', 'kafka-topics',
        '--create', '--topic', 'payments',
        '--bootstrap-server', 'localhost:9092',
        '--partitions', '1', '--replication-factor', '1',
        '--if-not-exists'
    ], capture_output=True)

    # Produce test messages
    producer = Producer({'bootstrap.servers': 'localhost:9092'})

    for i in range(10):
        payment = {
            'payment_id': str(uuid.uuid4()),
            'amount': 100.00 + i,
            'customer': f'CUST-{i:03d}'
        }
        producer.produce(
            'payments',
            key=payment['payment_id'].encode(),
            value=json.dumps(payment).encode()
        )
    producer.flush()
    print("Produced 10 payment events\n")

    # Consume - first pass
    print("=== First consumption pass ===")
    consume_payments()

    # Reset consumer offset to simulate restart
    print("\n=== Second pass (simulating restart) ===")
    consume_payments_from_start()

def consume_payments():
    config = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'payment-processor',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': False
    }

    consumer = Consumer(config)
    consumer.subscribe(['payments'])

    processed = 0
    duplicates = 0

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                if processed + duplicates >= 10:
                    break
                continue
            if msg.error():
                continue

            payment = json.loads(msg.value().decode())
            if process_payment(payment):
                processed += 1
            else:
                duplicates += 1

            consumer.commit(msg)

    finally:
        consumer.close()
        print(f"\nProcessed: {processed}, Duplicates skipped: {duplicates}")

def consume_payments_from_start():
    config = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'payment-processor-2',  # New group = start from beginning
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': False
    }

    consumer = Consumer(config)
    consumer.subscribe(['payments'])

    processed = 0
    duplicates = 0

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                if processed + duplicates >= 10:
                    break
                continue
            if msg.error():
                continue

            payment = json.loads(msg.value().decode())
            if process_payment(payment):
                processed += 1
            else:
                duplicates += 1

    finally:
        consumer.close()
        print(f"\nProcessed: {processed}, Duplicates skipped: {duplicates}")

if __name__ == '__main__':
    main()
```

</details>

---

## Exercise 5: Dead letter queue

**Objective:** Implement a dead letter queue for messages that fail processing.

### Task

Create a consumer that:
1. Attempts to process orders
2. Fails some orders intentionally (simulate with random failures)
3. Retries failed orders up to 3 times
4. Sends persistently failing orders to a DLQ topic

### Template

```python
# exercise_dlq.py
from confluent_kafka import Consumer, Producer
import json
import random

MAX_RETRIES = 3

def process_order(order: dict) -> bool:
    """
    Process an order. Returns True on success.
    Simulates ~20% failure rate.
    """
    if random.random() < 0.2:
        raise Exception("Random processing failure")
    print(f"Successfully processed: {order['order_id']}")
    return True

def send_to_dlq(producer, msg, error: str):
    """Send failed message to dead letter queue."""
    # TODO: Implement
    pass

def main():
    # TODO: Create DLQ topic

    consumer_config = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'order-processor-dlq',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': False
    }

    producer_config = {
        'bootstrap.servers': 'localhost:9092'
    }

    consumer = Consumer(consumer_config)
    dlq_producer = Producer(producer_config)

    consumer.subscribe(['orders'])

    # TODO: Implement retry logic with DLQ

if __name__ == '__main__':
    main()
```

### Solution

<details>
<summary>Click to reveal solution</summary>

```python
from confluent_kafka import Consumer, Producer
import json
import random
import time
import subprocess

MAX_RETRIES = 3

def process_order(order: dict) -> bool:
    if random.random() < 0.2:
        raise Exception("Random processing failure")
    print(f"SUCCESS: {order['order_id']}")
    return True

def send_to_dlq(producer, msg, error: str, retries: int):
    headers = [
        ('original_topic', msg.topic().encode()),
        ('original_partition', str(msg.partition()).encode()),
        ('original_offset', str(msg.offset()).encode()),
        ('error', str(error).encode()),
        ('retry_count', str(retries).encode())
    ]

    producer.produce(
        'orders-dlq',
        key=msg.key(),
        value=msg.value(),
        headers=headers
    )
    producer.flush()
    print(f"SENT TO DLQ: {msg.key().decode()} after {retries} retries - {error}")

def main():
    # Create DLQ topic
    subprocess.run([
        'docker', 'exec', 'kafka', 'kafka-topics',
        '--create', '--topic', 'orders-dlq',
        '--bootstrap-server', 'localhost:9092',
        '--partitions', '1', '--replication-factor', '1',
        '--if-not-exists'
    ], capture_output=True)

    consumer_config = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'order-processor-dlq',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': False
    }

    producer_config = {'bootstrap.servers': 'localhost:9092'}

    consumer = Consumer(consumer_config)
    dlq_producer = Producer(producer_config)

    consumer.subscribe(['orders'])

    stats = {'success': 0, 'dlq': 0}

    try:
        processed = 0
        while processed < 100:  # Process up to 100 messages
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                continue

            order = json.loads(msg.value().decode())
            retries = 0
            success = False

            while retries < MAX_RETRIES and not success:
                try:
                    process_order(order)
                    success = True
                    stats['success'] += 1
                except Exception as e:
                    retries += 1
                    if retries < MAX_RETRIES:
                        print(f"RETRY {retries}/{MAX_RETRIES}: {order['order_id']}")
                        time.sleep(0.1 * retries)  # Backoff

            if not success:
                send_to_dlq(dlq_producer, msg, str(e), retries)
                stats['dlq'] += 1

            consumer.commit(msg)
            processed += 1

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()
        print(f"\nStats: {stats}")

if __name__ == '__main__':
    main()
```

</details>

---

## Exercise 6: Performance benchmarking

**Objective:** Measure and compare producer throughput with different configurations.

### Task

Create a benchmark that tests:
1. acks=0 vs acks=1 vs acks=all
2. Different batch sizes (16KB, 32KB, 64KB)
3. With and without compression

### Template

```python
# exercise_benchmark.py
from confluent_kafka import Producer
import time
import json

def benchmark_producer(config: dict, num_messages: int, message_size: int) -> dict:
    """
    Benchmark a producer configuration.
    Returns dict with metrics.
    """
    producer = Producer(config)

    # Create a message of specified size
    message = {'data': 'x' * message_size}
    message_bytes = json.dumps(message).encode()

    start_time = time.time()
    delivered = 0
    errors = 0

    def callback(err, msg):
        nonlocal delivered, errors
        if err:
            errors += 1
        else:
            delivered += 1

    for i in range(num_messages):
        producer.produce('benchmark-topic', value=message_bytes, callback=callback)
        producer.poll(0)

    producer.flush()
    end_time = time.time()

    duration = end_time - start_time
    throughput = num_messages / duration
    mb_per_sec = (num_messages * len(message_bytes)) / duration / 1024 / 1024

    return {
        'duration': duration,
        'messages': num_messages,
        'errors': errors,
        'throughput': throughput,
        'mb_per_sec': mb_per_sec
    }

def main():
    # TODO: Run benchmarks with different configurations
    # TODO: Print comparison table
    pass

if __name__ == '__main__':
    main()
```

---

## Verification checklist

After completing these exercises, you should be able to:

- [ ] Create producers with delivery callbacks
- [ ] Use message keys for partition affinity
- [ ] Configure consumers for manual offset commits
- [ ] Handle rebalancing gracefully
- [ ] Implement idempotent message processing
- [ ] Set up dead letter queues for failed messages
- [ ] Benchmark different producer configurations

---

**[← Back to Module 2](../README.md)** | **[Next: Module 2 Quiz →](../quiz_module_2.md)**
