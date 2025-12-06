# gds_kafka

Kafka integration package for GDS services, providing:

- **KafkaProducerClient** - Send messages to Kafka topics
- **KafkaConsumerClient** - Consume messages from Kafka topics
- **KafkaMetrics** - Stream metrics to Kafka (implements `gds_metrics.MetricsCollector`)
- **KafkaLoggingHandler** - Stream Python logs to Kafka

## Installation

```bash
pip install gds-kafka
```

## Quick Start

### Producer

```python
from gds_kafka import KafkaProducerClient

with KafkaProducerClient("localhost:9092") as producer:
    producer.send("my-topic", {"event": "user_signup", "user_id": 123})
    producer.flush()
```

### Consumer

```python
from gds_kafka import KafkaConsumerClient

with KafkaConsumerClient("my-topic", "localhost:9092", group_id="my-group") as consumer:
    for message in consumer.messages():
        print(f"Received: {message['value']}")
```

### Metrics

```python
from gds_kafka import KafkaProducerClient, KafkaMetrics

producer = KafkaProducerClient("localhost:9092")
metrics = KafkaMetrics(producer, topic="app-metrics")

metrics.increment("requests_total", labels={"endpoint": "/api"})
metrics.gauge("active_connections", 42)
metrics.timing("db_query_ms", 15.5)
```

### Logging Handler

```python
import logging
from gds_kafka import KafkaProducerClient, KafkaLoggingHandler

producer = KafkaProducerClient("localhost:9092")
handler = KafkaLoggingHandler(producer, topic="app-logs")

logger = logging.getLogger("my_app")
logger.addHandler(handler)
logger.setLevel(logging.INFO)

logger.info("Application started")
```

## Error Handling

The package provides custom exceptions for proper error handling:

```python
from gds_kafka import (
    KafkaProducerClient,
    GdsKafkaError,
    KafkaConnectionError,
    KafkaMessageError,
    KafkaSerializationError,
    KafkaTimeoutError,
)

try:
    producer = KafkaProducerClient("localhost:9092")
    producer.send("topic", {"data": "value"})
except KafkaConnectionError as e:
    print(f"Failed to connect: {e}")
except KafkaSerializationError as e:
    print(f"Failed to serialize message: {e}")
except KafkaTimeoutError as e:
    print(f"Operation timed out: {e}")
except GdsKafkaError as e:
    print(f"Kafka error: {e}")
```

## Configuration

Both producer and consumer accept additional configuration via `**kwargs`:

```python
producer = KafkaProducerClient(
    "localhost:9092",
    acks="all",
    retries=3,
    max_block_ms=5000,
)

consumer = KafkaConsumerClient(
    "my-topic",
    "localhost:9092",
    group_id="my-group",
    auto_offset_reset="latest",
    enable_auto_commit=False,
)
```

## Dependencies

- `kafka-python>=2.0.2`
- `gds-metrics`

## Related Tutorials

For learning about Kafka in observability pipelines, see the [Observability Tutorial](../docs/tutorials/observability/):

- [Data Pipeline Architecture](../docs/tutorials/observability/03_DATA_PIPELINE_ARCHITECTURE.md) - Kafka as telemetry backbone
- [Kafka Streaming](../docs/tutorials/observability/07_KAFKA_STREAMING.md) - Producer/consumer patterns, DLQ, exactly-once semantics
- [Quick Reference](../docs/tutorials/observability/QUICK_REFERENCE.md) - Kafka commands and snippets
