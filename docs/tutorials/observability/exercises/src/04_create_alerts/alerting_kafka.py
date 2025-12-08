"""
Alert Evaluation with Kafka Consumer
"""

import json

from alerting import AlertEvaluator, AlertRule, ConsoleNotifier, Operator, Severity
from confluent_kafka import Consumer, KafkaError


def main():
    # Define rules
    rules = [
        AlertRule(
            id="cpu_high",
            name="High CPU Usage",
            description="CPU exceeds 80%",
            metric_name="cpu_usage_percent",
            operator=Operator.GT,
            threshold=80,
            severity=Severity.HIGH,
            duration=60,
            cooldown=300,
        ),
    ]

    evaluator = AlertEvaluator(rules)
    notifier = ConsoleNotifier()

    # Kafka consumer
    consumer = Consumer(
        {
            "bootstrap.servers": "localhost:9092",
            "group.id": "alert-evaluator",
            "auto.offset.reset": "latest",
        }
    )
    consumer.subscribe(["gds.metrics.production"])

    print("Listening for metrics...")

    try:
        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue
            if msg.error():
                if msg.error().code() != KafkaError._PARTITION_EOF:
                    print(f"Error: {msg.error()}")
                continue

            try:
                metric = json.loads(msg.value().decode("utf-8"))
                alert = evaluator.evaluate(metric)

                if alert:
                    notifier.notify(alert)

            except json.JSONDecodeError as e:
                print(f"Invalid JSON: {e}")

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()


if __name__ == "__main__":
    main()
