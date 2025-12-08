import pika


def main() -> None:
    """Send a single hello message to the RabbitMQ queue."""
    connection = pika.BlockingConnection(pika.URLParameters("amqp://devuser:devpassword@localhost:5672/"))
    channel = connection.channel()

    # Ensure the queue exists and survives broker restarts
    channel.queue_declare(queue="hello", durable=True)

    channel.basic_publish(
        exchange="",
        routing_key="hello",
        body="Hello RabbitMQ!",
        properties=pika.BasicProperties(delivery_mode=2),  # Persist message
    )
    print(" [x] Sent 'Hello RabbitMQ!'")
    connection.close()


if __name__ == "__main__":
    main()
