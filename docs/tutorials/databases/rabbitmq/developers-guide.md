# RabbitMQ Developer Guide: Task Queues and Work Distribution

Welcome to RabbitMQ! This guide is written for developers who are brand new to message brokers. You will learn what RabbitMQ is, why teams use it, how it works, and how to build a task queue in Python that safely distributes work across workers.

---

## 1. Why Message Brokers Matter

- **Problem:** Applications often need to run background jobs, spread work across multiple services, or communicate asynchronously. Hard‑coding these workflows with direct HTTP calls quickly becomes fragile and hard to scale.
- **Solution:** Use a message broker—a middleman that stores, routes, and delivers messages between producers (senders) and consumers (workers).
- **RabbitMQ:** An open-source broker that implements the AMQP protocol. It is lightweight, reliable, and supports flexible messaging patterns (queues, pub/sub, routing, etc.).

### Key Benefits
- Decouple services so they can evolve independently.
- Smooth out traffic spikes by buffering work in queues.
- Scale horizontally by adding more workers.
- Gain reliability through acknowledgements and message durability.

---

## 2. Core Concepts (AMQP 101)

| Term | Meaning |
| ---- | ------- |
| **Producer** | Application that sends messages (work items). |
| **Consumer** | Application that receives and processes messages. |
| **Queue** | A buffer that stores messages until a consumer is ready. |
| **Exchange** | Router: receives messages from producers and delivers them to queues. |
| **Binding** | A rule that connects an exchange to a queue. |
| **Routing Key** | Metadata used by exchanges to decide which queue(s) get a message. |
| **Acknowledgement (ACK)** | Confirmation from consumer to RabbitMQ that work is finished. |
| **Prefetch** | Limit on how many unacked messages a worker receives at once. |

Visual mental model:

```
Producer --> Exchange -(binding)-> Queue --> Consumer
```

---

## 3. Architecture Overview

1. A producer publishes a message to an **exchange**.
2. The exchange applies **bindings** to route the message into one or more **queues**.
3. Consumers connect to queues, fetch messages, process them, and send back ACKs.
4. RabbitMQ deletes ACKed messages or redelivers unacked messages if a consumer dies.

RabbitMQ’s management plugin (enabled by default in our Docker image) provides a web UI at `http://localhost:15672` where you can inspect queues, bindings, and message rates.

---

## 4. Local Environment Setup

Use the prebuilt Docker assets in this repository (see `docker/rabbitmq`):

```bash
cd /home/dpham/src/dbtools/docker/rabbitmq
docker compose up -d --wait
```

- Username: `devuser`
- Password: `devpassword`
- AMQP connection string: `amqp://devuser:devpassword@localhost:5672/`
- Management UI: `http://localhost:15672`

Stop the stack when finished:

```bash
docker compose down
```

---

## 5. Python Quick Start (Hello Queue)

Install prerequisites:

```bash
python -m venv .venv
source .venv/bin/activate
pip install pika
```

### File layout for the examples

All code snippets in this section live in `docs/tutorials/rabbitmq/examples/`.

Create a file named `docs/tutorials/rabbitmq/examples/send.py`:

```python
import pika

connection = pika.BlockingConnection(
    pika.URLParameters("amqp://devuser:devpassword@localhost:5672/")
)
channel = connection.channel()

channel.queue_declare(queue="hello", durable=True)
channel.basic_publish(
    exchange="",
    routing_key="hello",
    body="Hello RabbitMQ!",
    properties=pika.BasicProperties(delivery_mode=2),  # Persist to disk
)
print(" [x] Sent 'Hello RabbitMQ!'")
connection.close()
```

Create a file named `docs/tutorials/rabbitmq/examples/receive.py`:

```python
import pika

connection = pika.BlockingConnection(
    pika.URLParameters("amqp://devuser:devpassword@localhost:5672/")
)
channel = connection.channel()

channel.queue_declare(queue="hello", durable=True)

def callback(ch, method, properties, body):
    print(f" [x] Received {body.decode()}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue="hello", on_message_callback=callback)

print(" [*] Waiting for messages. To exit press CTRL+C")
channel.start_consuming()
```

Run the consumer in one terminal (`python receive.py`), then the producer (`python send.py`). The consumer prints the message and sends an ACK.

---

## 6. Task Queue Example (Work Distribution)

We will build a simple background job system where producers enqueue tasks and multiple worker processes share the load.

### 6.1 Design Goals

- Avoid losing tasks if workers crash (use durable queues + persistent messages).
- Prevent one worker from being overloaded (use `prefetch` to limit concurrency).
- Ensure tasks are acknowledged only after successful completion.

### 6.2 Producer: Enqueue Tasks

```python
# file: docs/tutorials/rabbitmq/examples/enqueue_tasks.py
import json
import pika
import uuid

def main():
    connection = pika.BlockingConnection(
        pika.URLParameters("amqp://devuser:devpassword@localhost:5672/")
    )
    channel = connection.channel()

    channel.queue_declare(queue="tasks", durable=True)

    jobs = [
        {"job_id": str(uuid.uuid4()), "operation": "resize-image", "payload": {"image_id": 1}},
        {"job_id": str(uuid.uuid4()), "operation": "send-email", "payload": {"user_id": 42}},
        {"job_id": str(uuid.uuid4()), "operation": "generate-report", "payload": {"month": "2025-10"}},
    ]

    for job in jobs:
        channel.basic_publish(
            exchange="",
            routing_key="tasks",
            body=json.dumps(job),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Persist message
                content_type="application/json",
            ),
        )
        print(f" [>] Enqueued job {job['job_id']} ({job['operation']})")

    connection.close()

if __name__ == "__main__":
    main()
```

### 6.3 Worker: Consume and Process Tasks

```python
# file: docs/tutorials/rabbitmq/examples/worker.py
import json
import random
import time

import pika

OPERATIONS = {
    "resize-image": lambda payload: time.sleep(2),
    "send-email": lambda payload: time.sleep(1),
    "generate-report": lambda payload: time.sleep(3),
}

def process_job(job):
    operation = job.get("operation")
    handler = OPERATIONS.get(operation, lambda payload: time.sleep(0.5))
    handler(job.get("payload", {}))

def main():
    connection = pika.BlockingConnection(
        pika.URLParameters("amqp://devuser:devpassword@localhost:5672/")
    )
    channel = connection.channel()

    channel.queue_declare(queue="tasks", durable=True)
    channel.basic_qos(prefetch_count=1)

    def on_message(ch, method, properties, body):
        job = json.loads(body)
        job_id = job.get("job_id")

        print(f" [*] Worker {id(ch)%1000} picked up job {job_id}")
        try:
            process_job(job)
            print(f" [✓] Completed job {job_id}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as exc:
            print(f" [!] Failed job {job_id}: {exc}")
            # Negative acknowledgement requeues the message for another worker.
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    channel.basic_consume(queue="tasks", on_message_callback=on_message)
    print(" [*] Waiting for tasks. Press CTRL+C to exit.")
    channel.start_consuming()

if __name__ == "__main__":
    main()
```

### 6.4 Running the Workflow

1. Start one or more workers (each in its own terminal tab):

   ```bash
   python docs/tutorials/rabbitmq/examples/worker.py
   ```

2. Enqueue tasks:

   ```bash
   python docs/tutorials/rabbitmq/examples/enqueue_tasks.py
   ```

3. Watch the workers share the load. Add more workers to handle more tasks.

4. View queue depth and rates at `http://localhost:15672/#/queues`.

---

## 7. Best Practices

**Durability**
- Declare queues with `durable=True` and publish messages with `delivery_mode=2` to survive broker restarts.
- For critical workflows, mirror queues or deploy a RabbitMQ cluster.

**Acknowledgements**
- Always ACK after successful processing; use `basic_nack` or `basic_reject` on failure.
- Turn on `manual_ack` (default in `BlockingConnection`) so you control ACK timing.

**Prefetch / Flow Control**
- Use `basic_qos(prefetch_count=N)` to limit the number of unacked messages per worker. Start with 1 to distribute evenly.

**Error Handling & Retries**
- Use dead-letter exchanges or dedicated retry queues to avoid message loss or infinite retry loops.
- Add logging and dashboards for monitoring processing failures.

**Security**
- Change default credentials in production.
- Enable TLS (`amqps://`) for encrypted traffic.
- Use separate virtual hosts per application or team.

**Observability**
- Enable Prometheus metrics (`15692` in our image) and collect them with Grafana/Prometheus.
- Set up alerts for queue length, consumer counts, and error rates.

**Connection Management**
- Reuse connections when possible; open a new channel per unit of work if needed.
- Use heartbeats (default 60s) to detect dead connections.

---

## 8. Common Use Cases

- **Background job processing:** Resize images, send emails, crunch analytics without blocking user requests.
- **Microservice communication:** Event-driven systems where services publish events others react to.
- **IoT telemetry:** Buffer device messages before downstream processing.
- **Workflow orchestration:** Sequence tasks with routing logic (e.g., topic exchanges).
- **RPC-style requests:** Implement request-response patterns with temporary queues.

---

## 9. Next Steps and Resources

- Explore [RabbitMQ Tutorials](https://www.rabbitmq.com/tutorials/tutorial-one-python.html).
- Read the `rabbitmq-docker-setup.md` file in `docker/rabbitmq` for environment details.
- Experiment with advanced exchanges (direct, fanout, topic) and confirm routing logic via the management UI.
- Consider using higher-level task libraries (Celery, RQ) once you are comfortable with the fundamentals.

Happy queueing!
