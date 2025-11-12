import json
import uuid

import pika


def enqueue_jobs(channel) -> None:
    """Publish a batch of demo jobs to the tasks queue."""
    jobs = [
        {
            "job_id": str(uuid.uuid4()),
            "operation": "resize-image",
            "payload": {"image_id": 1},
        },
        {
            "job_id": str(uuid.uuid4()),
            "operation": "send-email",
            "payload": {"user_id": 42},
        },
        {
            "job_id": str(uuid.uuid4()),
            "operation": "generate-report",
            "payload": {"month": "2025-10"},
        },
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


def main() -> None:
    """Entry point for the enqueue script."""
    connection = pika.BlockingConnection(
        pika.URLParameters("amqp://devuser:devpassword@localhost:5672/")
    )
    channel = connection.channel()

    channel.queue_declare(queue="tasks", durable=True)

    try:
        enqueue_jobs(channel)
    finally:
        connection.close()


if __name__ == "__main__":
    main()
