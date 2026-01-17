import pika


def main() -> None:
    """Consume messages from the hello queue."""
    connection = pika.BlockingConnection(pika.URLParameters("amqp://devuser:devpassword@localhost:5672/"))
    channel = connection.channel()

    channel.queue_declare(queue="hello", durable=True)

    def callback(ch, method, properties, body):
        print(f" [x] Received {body.decode()}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue="hello", on_message_callback=callback)

    print(" [*] Waiting for messages. To exit press CTRL+C")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\n [!] Stopping consumer...")
    finally:
        channel.stop_consuming()
        connection.close()


if __name__ == "__main__":
    main()
