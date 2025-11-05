#!/usr/bin/env python3
"""
Generate synthetic metric events compatible with the GDS monitoring architecture.

Usage examples:

1) Print 10 CPU metrics at 2 events/sec to stdout:
   ./generate_synthetic_metrics.py \
       --metric-name cpu_usage_percent --database-type postgresql \
       --instance-id prod-db-01 --value 72 --jitter 8 \
       --rate 2 --count 10

2) Generate high error_rate to trigger burn-rate rules:
   ./generate_synthetic_metrics.py \
       --metric-name request_error_rate --value 0.05 --jitter 0.02 \
       --instance-id prod-db-01 --database-type postgresql \
       --rate 1 --count 100

3) Pipe to Kafka using kcat (recommended for quick tests):
   ./generate_synthetic_metrics.py --metric-name cpu_usage_percent --count 100 \
     | kcat -b localhost:9092 -t gds.metrics.postgresql.production -K:

4) Write directly to Kafka if confluent-kafka is installed:
   ./generate_synthetic_metrics.py --metric-name cpu_usage_percent \
       --count 100 --kafka-bootstrap localhost:9092 \
       --kafka-topic gds.metrics.postgresql.production

Notes:
- By default, logs to stdout as newline-delimited JSON.
- If --kafka-bootstrap and --kafka-topic are provided and confluent_kafka is
  available, messages are produced to Kafka with key=instance_id or
  f"{instance_id}:{metric_name}" when --key-include-metric is set.
"""

import argparse
import json
import random
import sys
import time
import uuid
from datetime import datetime, timezone

try:
    from confluent_kafka import Producer  # type: ignore
except ImportError:  # pragma: no cover
    Producer = None  # type: ignore


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_event(args, value):
    return {
        "timestamp": now_iso(),
        "database_type": args.database_type,
        "instance_id": args.instance_id,
        "metric_name": args.metric_name,
        "value": value,
        "tags": {
            "environment": args.environment,
            "region": args.region,
        },
        "metadata": {
            "collection_duration_ms": random.randint(50, 200),
            "version": "1.0",
            "correlation_id": str(uuid.uuid4()),
        },
    }


def parse_args():
    p = argparse.ArgumentParser(description="Generate synthetic metrics")
    p.add_argument(
        "--metric-name",
        required=True,
        help=("Metric name (e.g., cpu_usage_percent, request_error_rate)"),
    )
    p.add_argument("--database-type", default="postgresql")
    p.add_argument("--instance-id", default="prod-db-01")
    p.add_argument("--environment", default="production")
    p.add_argument("--region", default="us-east-1")

    p.add_argument(
        "--value",
        type=float,
        default=None,
        help=("Base value; if omitted, sensible defaults are used"),
    )
    p.add_argument(
        "--jitter",
        type=float,
        default=None,
        help="Random jitter applied (+/-)",
    )

    p.add_argument("--rate", type=float, default=1.0, help="Events per second")
    p.add_argument(
        "--count",
        type=int,
        default=10,
        help="Total events to generate",
    )

    # Kafka (optional)
    p.add_argument(
        "--kafka-bootstrap",
        default=None,
        help="Kafka bootstrap servers",
    )
    p.add_argument(
        "--kafka-topic",
        default=None,
        help="Kafka topic to produce to",
    )
    p.add_argument(
        "--key-include-metric",
        action="store_true",
        help="Include metric name in message key",
    )

    return p.parse_args()


def pick_defaults(metric_name: str):
    # Default values and jitter per metric type
    if metric_name == "cpu_usage_percent":
        return 70.0, 10.0
    if metric_name == "request_error_rate":  # fraction 0..1
        return 0.02, 0.01
    if metric_name == "availability":  # fraction 0..1
        return 0.999, 0.001
    return 1.0, 0.1


def compute_value(base, jitter):
    if jitter is None or jitter == 0:
        return base
    return max(0.0, base + random.uniform(-jitter, jitter))


def produce_stdout(evt):
    sys.stdout.write(json.dumps(evt) + "\n")
    sys.stdout.flush()


def produce_kafka(producer, topic, key, evt):
    producer.produce(topic=topic, key=key, value=json.dumps(evt))


def main():
    args = parse_args()

    base, default_jitter = pick_defaults(args.metric_name)
    base_value = args.value if args.value is not None else base
    jitter = args.jitter if args.jitter is not None else default_jitter

    interval = 1.0 / max(0.0001, args.rate)

    use_kafka = bool(args.kafka_bootstrap and args.kafka_topic and Producer)
    producer = None
    if use_kafka:
        producer = Producer({"bootstrap.servers": args.kafka_bootstrap})

    for _ in range(args.count):
        value = compute_value(base_value, jitter)
        evt = build_event(args, value)
        if args.key_include_metric:
            key = f"{args.instance_id}:{args.metric_name}"
        else:
            key = args.instance_id
        if use_kafka and producer is not None:
            produce_kafka(producer, args.kafka_topic, key, evt)
        else:
            produce_stdout(evt)
        time.sleep(interval)

    if use_kafka and producer is not None:
        producer.flush()


if __name__ == "__main__":
    main()
