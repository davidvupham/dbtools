import json
import time

import pika


OPERATIONS = {
    "resize-image": lambda payload: time.sleep(2),
    "send-email": lambda payload: time.sleep(1),
    "generate-report": lambda payload: time.sleep(3),
}


def process_job(job: dict) -> None:
    """Perform a fake workload based on the job operation."""
    operation = job.get("operation")
    handler = OPERATIONS.get(operation, lambda payload: time.sleep(0.5))
    handler(job.get("payload", {}))


def main() -> None:
    """Start a blocking worker that consumes tasks."""
    connection = pika.BlockingConnection(
        pika.URLParameters("amqp://devuser:devpassword@localhost:5672/")
    )
    channel = connection.channel()

    channel.queue_declare(queue="tasks", durable=True)
    channel.basic_qos(prefetch_count=1)

    def on_message(ch, method, properties, body):
        job = json.loads(body)
        job_id = job.get("job_id")

        print(f" [*] Worker picked up job {job_id}")
        try:
            process_job(job)
            print(f" [✓] Completed job {job_id}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as exc:
            print(f" [!] Failed job {job_id}: {exc}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    channel.basic_consume(queue="tasks", on_message_callback=on_message)
    print(" [*] Waiting for tasks. Press CTRL+C to exit.")

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\n [!] Worker interrupted. Cleaning up.")
    finally:
        channel.stop_consuming()
        connection.close()


if __name__ == "__main__":
    main()
