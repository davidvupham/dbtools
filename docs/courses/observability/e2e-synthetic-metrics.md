# End-to-end (E2E) test with synthetic metrics

This tutorial shows how to exercise the monitoring → Kafka → alerting →
notification path using synthetic metrics. You can test with or without Kafka.

## Prerequisites

- Python 3.9+
- Optional: Kafka broker and `kcat` (or `confluent-kafka` Python package)

## Option A: No Kafka (stdout only)

Generate a burst of CPU metrics and inspect the JSON lines:

```bash
./examples/monitoring/generate_synthetic_metrics.py \
  --metric-name cpu_usage_percent \
  --database-type postgresql \
  --instance-id prod-db-01 \
  --value 72 --jitter 8 \
  --rate 2 --count 10
```

Use the output to validate your evaluator logic locally (e.g., unit tests).

## Option B: Kafka via kcat

1) Create a topic (example):

```bash
kafka-topics --bootstrap-server localhost:9092 \
  --create --topic gds.metrics.postgresql.production \
  --partitions 6 --replication-factor 1
```

2) Produce synthetic metrics into Kafka:

```bash
./examples/monitoring/generate_synthetic_metrics.py \
  --metric-name cpu_usage_percent --count 100 \
  | kcat -b localhost:9092 -t gds.metrics.postgresql.production -K:
```

3) Consume to verify:

```bash
kcat -b localhost:9092 -t gds.metrics.postgresql.production -C -o -5 -q
```

## Option C: Python direct Kafka (confluent-kafka)

```bash
pip install confluent-kafka
./examples/monitoring/generate_synthetic_metrics.py \
  --metric-name cpu_usage_percent \
  --count 100 \
  --kafka-bootstrap localhost:9092 \
  --kafka-topic gds.metrics.postgresql.production
```

## Triggering burn-rate alerts

Send elevated error rates to simulate SLO burn:

```bash
./examples/monitoring/generate_synthetic_metrics.py \
  --metric-name request_error_rate \
  --instance-id prod-db-01 \
  --value 0.05 --jitter 0.02 \
  --rate 1 --count 300 \
  | kcat -b localhost:9092 -t gds.metrics.postgresql.production -K:
```

With the example rules in `examples/monitoring/rules.yaml`, your alerting
engine should page for the fast-burn rule and warn for the slow-burn rule
once both short and long windows are breached.

## Using the schema stub

Optionally register the schema in `schemas/metrics-value.avsc` to enforce
compatibility and enable typed consumers. See `schemas/README.md`.

## Cleanup tips

- Drop or compact test topics when done
- Reset consumer groups used for testing if needed

## Troubleshooting

- If no messages are consumed, check topic name, bootstrap servers, and that
  the JSON is newline-delimited
- Verify keys: use `--key-include-metric` to route by instance+metric
- Watch Kafka lag when testing continuously; it’s a great signal the pipeline
  is healthy
