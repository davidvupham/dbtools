# Kafka Quick Reference

**[← Back to Course Index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Apache_Kafka-blue)

> [!IMPORTANT]
> **Related Docs:** [Glossary](./glossary.md) | [Course Overview](./course_overview.md)

## Table of contents

- [Topic commands](#topic-commands)
- [Producer commands](#producer-commands)
- [Consumer commands](#consumer-commands)
- [Consumer group commands](#consumer-group-commands)
- [Configuration commands](#configuration-commands)
- [Kafka Connect commands](#kafka-connect-commands)
- [ksqlDB commands](#ksqldb-commands)
- [Docker commands](#docker-commands)
- [Python client examples](#python-client-examples)
- [Java client examples](#java-client-examples)

---

## Topic commands

### List topics

```bash
# List all topics
kafka-topics.sh --bootstrap-server localhost:9092 --list

# List topics with details
kafka-topics.sh --bootstrap-server localhost:9092 --describe
```

### Create topic

```bash
# Basic topic creation
kafka-topics.sh --bootstrap-server localhost:9092 \
  --create \
  --topic my-topic \
  --partitions 3 \
  --replication-factor 1

# With configuration
kafka-topics.sh --bootstrap-server localhost:9092 \
  --create \
  --topic my-topic \
  --partitions 6 \
  --replication-factor 3 \
  --config retention.ms=604800000 \
  --config cleanup.policy=compact
```

### Describe topic

```bash
# Get topic details
kafka-topics.sh --bootstrap-server localhost:9092 \
  --describe \
  --topic my-topic

# Show partition details
kafka-topics.sh --bootstrap-server localhost:9092 \
  --describe \
  --topic my-topic \
  --under-replicated-partitions
```

### Delete topic

```bash
kafka-topics.sh --bootstrap-server localhost:9092 \
  --delete \
  --topic my-topic
```

### Alter topic

```bash
# Increase partitions (cannot decrease)
kafka-topics.sh --bootstrap-server localhost:9092 \
  --alter \
  --topic my-topic \
  --partitions 6
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Producer commands

### Console producer

```bash
# Basic producer
kafka-console-producer.sh --bootstrap-server localhost:9092 \
  --topic my-topic

# With key
kafka-console-producer.sh --bootstrap-server localhost:9092 \
  --topic my-topic \
  --property parse.key=true \
  --property key.separator=:

# Type: key:value (e.g., user1:{"name":"Alice"})
```

### Producer with file

```bash
# Produce from file
kafka-console-producer.sh --bootstrap-server localhost:9092 \
  --topic my-topic < messages.txt
```

### Producer with acknowledgments

```bash
kafka-console-producer.sh --bootstrap-server localhost:9092 \
  --topic my-topic \
  --producer-property acks=all
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Consumer commands

### Console consumer

```bash
# Consume from latest
kafka-console-consumer.sh --bootstrap-server localhost:9092 \
  --topic my-topic

# Consume from beginning
kafka-console-consumer.sh --bootstrap-server localhost:9092 \
  --topic my-topic \
  --from-beginning

# With consumer group
kafka-console-consumer.sh --bootstrap-server localhost:9092 \
  --topic my-topic \
  --group my-group
```

### Consumer with key and timestamp

```bash
kafka-console-consumer.sh --bootstrap-server localhost:9092 \
  --topic my-topic \
  --from-beginning \
  --property print.key=true \
  --property print.timestamp=true \
  --property key.separator=": "
```

### Consumer with max messages

```bash
kafka-console-consumer.sh --bootstrap-server localhost:9092 \
  --topic my-topic \
  --from-beginning \
  --max-messages 10
```

### Consume specific partition

```bash
kafka-console-consumer.sh --bootstrap-server localhost:9092 \
  --topic my-topic \
  --partition 0 \
  --offset 5
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Consumer group commands

### List consumer groups

```bash
kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list
```

### Describe consumer group

```bash
# Show group details with lag
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --describe \
  --group my-group
```

### Reset offsets

```bash
# Reset to earliest
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --group my-group \
  --topic my-topic \
  --reset-offsets \
  --to-earliest \
  --execute

# Reset to latest
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --group my-group \
  --topic my-topic \
  --reset-offsets \
  --to-latest \
  --execute

# Reset to specific offset
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --group my-group \
  --topic my-topic \
  --reset-offsets \
  --to-offset 100 \
  --execute

# Reset by timestamp
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --group my-group \
  --topic my-topic \
  --reset-offsets \
  --to-datetime "2026-01-21T00:00:00.000" \
  --execute
```

### Delete consumer group

```bash
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --delete \
  --group my-group
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Configuration commands

### View topic configuration

```bash
kafka-configs.sh --bootstrap-server localhost:9092 \
  --entity-type topics \
  --entity-name my-topic \
  --describe
```

### Alter topic configuration

```bash
# Set retention to 7 days
kafka-configs.sh --bootstrap-server localhost:9092 \
  --entity-type topics \
  --entity-name my-topic \
  --alter \
  --add-config retention.ms=604800000

# Delete configuration (revert to default)
kafka-configs.sh --bootstrap-server localhost:9092 \
  --entity-type topics \
  --entity-name my-topic \
  --alter \
  --delete-config retention.ms
```

### View broker configuration

```bash
kafka-configs.sh --bootstrap-server localhost:9092 \
  --entity-type brokers \
  --entity-name 0 \
  --describe --all
```

### Common topic configurations

| Configuration | Description | Default |
|---------------|-------------|---------|
| `retention.ms` | Time to keep messages | 604800000 (7 days) |
| `retention.bytes` | Max size per partition | -1 (unlimited) |
| `cleanup.policy` | delete or compact | delete |
| `compression.type` | producer, gzip, snappy, lz4, zstd | producer |
| `max.message.bytes` | Max message size | 1048576 (1MB) |
| `min.insync.replicas` | Min ISR for acks=all | 1 |

[↑ Back to Table of Contents](#table-of-contents)

---

## Kafka Connect commands

### List connectors

```bash
curl -s http://localhost:8083/connectors | jq
```

### Get connector status

```bash
curl -s http://localhost:8083/connectors/my-connector/status | jq
```

### Create connector

```bash
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-connector",
    "config": {
      "connector.class": "org.apache.kafka.connect.file.FileStreamSourceConnector",
      "tasks.max": "1",
      "file": "/tmp/input.txt",
      "topic": "my-topic"
    }
  }'
```

### Delete connector

```bash
curl -X DELETE http://localhost:8083/connectors/my-connector
```

### Restart connector

```bash
curl -X POST http://localhost:8083/connectors/my-connector/restart
```

### List connector plugins

```bash
curl -s http://localhost:8083/connector-plugins | jq
```

[↑ Back to Table of Contents](#table-of-contents)

---

## ksqlDB commands

### Start ksqlDB CLI

```bash
docker exec -it ksqldb-cli ksql http://ksqldb-server:8088
```

### Create stream

```sql
CREATE STREAM orders (
  order_id VARCHAR KEY,
  customer_id VARCHAR,
  product VARCHAR,
  amount DECIMAL(10,2),
  order_time TIMESTAMP
) WITH (
  KAFKA_TOPIC = 'orders',
  VALUE_FORMAT = 'JSON',
  PARTITIONS = 3
);
```

### Create table

```sql
CREATE TABLE customers (
  customer_id VARCHAR PRIMARY KEY,
  name VARCHAR,
  email VARCHAR
) WITH (
  KAFKA_TOPIC = 'customers',
  VALUE_FORMAT = 'JSON'
);
```

### Query stream

```sql
-- Push query (continuous)
SELECT * FROM orders EMIT CHANGES;

-- Pull query (point-in-time)
SELECT * FROM customers WHERE customer_id = 'C001';
```

### Aggregations

```sql
CREATE TABLE order_totals AS
SELECT
  customer_id,
  COUNT(*) AS order_count,
  SUM(amount) AS total_amount
FROM orders
GROUP BY customer_id
EMIT CHANGES;
```

### Windowed aggregations

```sql
CREATE TABLE orders_per_hour AS
SELECT
  product,
  COUNT(*) AS order_count,
  WINDOWSTART AS window_start,
  WINDOWEND AS window_end
FROM orders
WINDOW TUMBLING (SIZE 1 HOUR)
GROUP BY product
EMIT CHANGES;
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Docker commands

### Start Kafka (Docker Compose)

```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f kafka

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Execute Kafka commands in Docker

```bash
# Enter Kafka container
docker exec -it kafka bash

# Run command directly
docker exec -it kafka kafka-topics.sh --bootstrap-server localhost:9092 --list
```

### Docker Compose (KRaft mode)

```yaml
version: '3.8'
services:
  kafka:
    image: confluentinc/cp-kafka:7.6.0
    hostname: kafka
    container_name: kafka
    ports:
      - "9092:9092"
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_PROCESS_ROLES: 'broker,controller'
      KAFKA_CONTROLLER_QUORUM_VOTERS: '1@kafka:29093'
      KAFKA_LISTENERS: 'PLAINTEXT://kafka:29092,CONTROLLER://kafka:29093,PLAINTEXT_HOST://0.0.0.0:9092'
      KAFKA_ADVERTISED_LISTENERS: 'PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092'
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: 'CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT'
      KAFKA_INTER_BROKER_LISTENER_NAME: 'PLAINTEXT'
      KAFKA_CONTROLLER_LISTENER_NAMES: 'CONTROLLER'
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      CLUSTER_ID: 'MkU3OEVBNTcwNTJENDM2Qk'
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Python client examples

### Installation

```bash
pip install confluent-kafka
# or
pip install kafka-python
```

### Producer (confluent-kafka)

```python
from confluent_kafka import Producer
import json

conf = {'bootstrap.servers': 'localhost:9092'}
producer = Producer(conf)

def delivery_report(err, msg):
    if err:
        print(f'Delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

# Produce message
data = {'user': 'alice', 'action': 'login'}
producer.produce(
    'my-topic',
    key='user1',
    value=json.dumps(data),
    callback=delivery_report
)
producer.flush()
```

### Consumer (confluent-kafka)

```python
from confluent_kafka import Consumer
import json

conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'my-group',
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(conf)
consumer.subscribe(['my-topic'])

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Error: {msg.error()}")
            continue

        print(f"Key: {msg.key()}, Value: {msg.value()}")
finally:
    consumer.close()
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Java client examples

### Maven dependency

```xml
<dependency>
    <groupId>org.apache.kafka</groupId>
    <artifactId>kafka-clients</artifactId>
    <version>3.7.0</version>
</dependency>
```

### Producer

```java
import org.apache.kafka.clients.producer.*;
import java.util.Properties;

Properties props = new Properties();
props.put("bootstrap.servers", "localhost:9092");
props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
props.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer");
props.put("acks", "all");

Producer<String, String> producer = new KafkaProducer<>(props);

ProducerRecord<String, String> record = new ProducerRecord<>(
    "my-topic", "key1", "Hello, Kafka!");

producer.send(record, (metadata, exception) -> {
    if (exception != null) {
        exception.printStackTrace();
    } else {
        System.out.printf("Sent to partition %d, offset %d%n",
            metadata.partition(), metadata.offset());
    }
});

producer.close();
```

### Consumer

```java
import org.apache.kafka.clients.consumer.*;
import java.time.Duration;
import java.util.Collections;
import java.util.Properties;

Properties props = new Properties();
props.put("bootstrap.servers", "localhost:9092");
props.put("group.id", "my-group");
props.put("key.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
props.put("value.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
props.put("auto.offset.reset", "earliest");

Consumer<String, String> consumer = new KafkaConsumer<>(props);
consumer.subscribe(Collections.singletonList("my-topic"));

try {
    while (true) {
        ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
        for (ConsumerRecord<String, String> record : records) {
            System.out.printf("key=%s, value=%s, partition=%d, offset=%d%n",
                record.key(), record.value(), record.partition(), record.offset());
        }
    }
} finally {
    consumer.close();
}
```

[↑ Back to Table of Contents](#table-of-contents)

---

**Next:** [Module 1: Introduction to Kafka →](./module_1_foundations/01_introduction.md)
