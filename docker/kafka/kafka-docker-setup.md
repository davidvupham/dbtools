# Kafka Docker Setup Guide

This guide provides comprehensive step-by-step instructions for setting up Apache Kafka with Zookeeper in Docker, including persistent storage and integration with VS Code dev containers.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Directory Structure](#directory-structure)
- [Building the Docker Images](#building-the-docker-images)
- [Starting Kafka and Zookeeper](#starting-kafka-and-zookeeper)
- [Verifying the Setup](#verifying-the-setup)
- [Working with Kafka](#working-with-kafka)
  - [Creating Topics](#creating-topics)
  - [Producing Messages](#producing-messages)
  - [Consuming Messages](#consuming-messages)
  - [Listing Topics](#listing-topics)
  - [Describing Topics](#describing-topics)
- [Connecting from Applications](#connecting-from-applications)
- [Monitoring and Logs](#monitoring-and-logs)
- [Stopping and Managing Services](#stopping-and-managing-services)
- [Docker Commands Reference](#docker-commands-reference)
- [Troubleshooting](#troubleshooting)
- [Advanced Topics](#advanced-topics)

## Overview

This setup creates a complete Kafka environment with:

- **Apache Kafka 3.6.x** (via Confluent Platform 7.6.0)
- **Zookeeper 3.8.x** for cluster coordination
- **Persistent data storage** in `/data/kafka` and `/data/zookeeper`
- **Persistent logs** in `/logs/kafka`
- **Port 9092** exposed for Kafka client connections
- **Port 2181** exposed for Zookeeper connections
- **Integration** with VS Code dev containers
- **Health checks** for automatic service recovery

### What is Kafka?

Apache Kafka is a distributed event streaming platform used for:

- Building real-time data pipelines
- Streaming analytics
- Data integration
- Event-driven architectures
- Message queuing

### Kafka Key Concepts

- **Broker**: Kafka server that stores and serves messages
- **Topic**: Category or feed name to which messages are published
- **Partition**: Subdivision of a topic for parallelism
- **Producer**: Application that sends messages to topics
- **Consumer**: Application that reads messages from topics
- **Consumer Group**: Set of consumers that cooperate to consume a topic
- **Zookeeper**: Coordination service for Kafka metadata (being replaced by KRaft)

## Prerequisites

- Docker installed and running
- Docker Compose installed
- WSL2 (if on Windows)
- VS Code with Dev Containers extension (for dev container setup)
- At least 4GB RAM allocated to Docker
- `/data` and `/logs` directory structure on your host system

## Directory Structure

Before starting, ensure these directories exist on your host system (WSL host if using Windows):

```bash
# Create the directory structure on WSL/Linux host
sudo mkdir -p /data/kafka/logs
sudo mkdir -p /data/zookeeper/data
sudo mkdir -p /data/zookeeper/logs
sudo mkdir -p /logs/kafka

# Set ownership for Kafka and Zookeeper
# Kafka runs as UID 1000 (appuser)
# Zookeeper runs as UID 1000
sudo chown -R 1000:1000 /data/kafka
sudo chown -R 1000:1000 /data/zookeeper
sudo chown -R 1000:1000 /logs/kafka
```

The project structure looks like this:

```
/workspaces/dbtools/docker/kafka/
├── Dockerfile              # Defines the Kafka image
├── docker-compose.yml      # Orchestrates Kafka and Zookeeper containers
└── kafka-docker-setup.md   # This file
```

## Building the Docker Images

### Step 1: Navigate to the Kafka directory

```bash
cd /workspaces/dbtools/docker/kafka
```

### Step 2: Build the Docker images

```bash
docker-compose build
```

**What this does:**

- Builds the custom Kafka image from the Dockerfile
- Tags the image as `gds-kafka:latest`
- Pulls the Zookeeper image (if not already present)
- Uses build cache for faster subsequent builds

**Expected output:**

```
[+] Building 45.2s (8/8) FINISHED
 => [internal] load build definition from Dockerfile
 => => transferring dockerfile: 2.34kB
 => [internal] load .dockerignore
 => [1/3] FROM docker.io/confluentinc/cp-kafka:7.6.0
 => [2/3] RUN mkdir -p /data/kafka/logs /logs/kafka
 => [3/3] RUN chown -R appuser:appuser /data /logs
 => exporting to image
 => => naming to docker.io/library/gds-kafka:latest
```

### Step 3: Verify the images were created

```bash
docker images | grep -E "kafka|zookeeper"
```

**Expected output:**

```
gds-kafka                              latest    abc123def456    2 minutes ago    1.45GB
confluentinc/cp-kafka                  7.6.0     def456abc123    3 weeks ago      1.43GB
confluentinc/cp-zookeeper              7.6.0     789abc012def    3 weeks ago      801MB
```

## Starting Kafka and Zookeeper

### Method 1: Using Docker Compose (Recommended)

```bash
# From /workspaces/dbtools/docker/kafka directory
docker-compose up -d
```

**What this does:**

- Starts Zookeeper first (due to dependency)
- Waits for Zookeeper to start
- Starts Kafka broker
- Runs both services in detached mode (background)

**Expected output:**

```
[+] Running 3/3
 ✔ Network kafka_kafka-network  Created    0.1s
 ✔ Container zookeeper          Started    2.3s
 ✔ Container kafka1             Started    4.5s
```

### Step 2: Verify the containers are running

```bash
docker-compose ps
```

**Expected output:**

```
NAME         IMAGE               COMMAND                  SERVICE      STATUS         PORTS
kafka1       gds-kafka:latest    "/etc/confluent/dock…"   kafka        Up 30 seconds  0.0.0.0:9092->9092/tcp
zookeeper    cp-zookeeper:7.6.0  "/etc/confluent/dock…"   zookeeper    Up 32 seconds  0.0.0.0:2181->2181/tcp
```

### Step 3: Check container logs

**Zookeeper logs:**

```bash
docker-compose logs zookeeper
```

**Look for these success messages:**

```
zookeeper | [2024-01-01 12:00:00,123] INFO binding to port 0.0.0.0/0.0.0.0:2181
zookeeper | [2024-01-01 12:00:00,456] INFO Server environment:zookeeper.version=3.8.3
```

**Kafka logs:**

```bash
docker-compose logs kafka
```

**Look for these success messages:**

```
kafka1 | [2024-01-01 12:00:05,789] INFO [KafkaServer id=1] started (kafka.server.KafkaServer)
kafka1 | [2024-01-01 12:00:05,800] INFO Kafka version: 3.6.0
```

### Step 4: Wait for services to be healthy

```bash
# Watch the health status
watch -n 2 'docker-compose ps'
```

Wait until both services show "healthy" status (may take 30-60 seconds).

Press `Ctrl+C` to exit the watch command.

## Verifying the Setup

### Check Zookeeper Connection

```bash
# From dev container or host
echo ruok | nc localhost 2181
```

**Expected output:**

```
imok
```

### Check Kafka Broker

```bash
# List Kafka broker API versions (confirms Kafka is responding)
docker-compose exec kafka kafka-broker-api-versions --bootstrap-server localhost:9092
```

**Expected output (truncated):**

```
localhost:9092 (id: 1 rack: null) -> (
    Produce(0): 0 to 9 [usable: 9],
    Fetch(1): 0 to 15 [usable: 15],
    ...
)
```

## Working with Kafka

All commands below can be run from either:

- Inside the Kafka container: `docker-compose exec kafka <command>`
- From dev container (if Kafka tools installed)

### Creating Topics

Topics are like tables or categories for messages. Create topics before producing messages (though auto-creation is enabled).

```bash
# Create a topic with 3 partitions and replication factor 1
docker-compose exec kafka kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --replication-factor 1 \
  --partitions 3 \
  --topic test-topic
```

**Expected output:**

```
Created topic test-topic.
```

**Explanation:**

- `--bootstrap-server localhost:9092`: Kafka broker address
- `--replication-factor 1`: Number of copies (1 = no replication, single broker)
- `--partitions 3`: Number of partitions for parallelism
- `--topic test-topic`: Name of the topic

### Listing Topics

```bash
# List all topics
docker-compose exec kafka kafka-topics --list \
  --bootstrap-server localhost:9092
```

**Expected output:**

```
test-topic
__consumer_offsets
__transaction_state
```

### Describing Topics

```bash
# Get detailed information about a topic
docker-compose exec kafka kafka-topics --describe \
  --bootstrap-server localhost:9092 \
  --topic test-topic
```

**Expected output:**

```
Topic: test-topic TopicId: abc123def456 PartitionCount: 3 ReplicationFactor: 1 Configs:
 Topic: test-topic Partition: 0 Leader: 1 Replicas: 1 Isr: 1
 Topic: test-topic Partition: 1 Leader: 1 Replicas: 1 Isr: 1
 Topic: test-topic Partition: 2 Leader: 1 Replicas: 1 Isr: 1
```

**Explanation:**

- `Leader`: Broker ID handling reads/writes for this partition
- `Replicas`: Brokers that have a copy of this partition
- `Isr`: In-Sync Replicas (up-to-date copies)

### Producing Messages

Send test messages to a topic using the console producer.

```bash
# Start console producer (interactive mode)
docker-compose exec kafka kafka-console-producer \
  --bootstrap-server localhost:9092 \
  --topic test-topic
```

**You'll see a prompt:**

```
>
```

**Type messages and press Enter after each:**

```
>Hello Kafka!
>This is message 2
>Testing message 3
```

**Press `Ctrl+C` to exit the producer.**

**Producing with keys:**

```bash
# Producer with keys (key:value format)
docker-compose exec kafka kafka-console-producer \
  --bootstrap-server localhost:9092 \
  --topic test-topic \
  --property "parse.key=true" \
  --property "key.separator=:"
```

**Type messages with keys:**

```
>user1:Hello from user1
>user2:Hello from user2
>user1:Another message from user1
```

### Consuming Messages

Read messages from a topic using the console consumer.

```bash
# Consume from beginning
docker-compose exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic test-topic \
  --from-beginning
```

**Expected output:**

```
Hello Kafka!
This is message 2
Testing message 3
```

**Press `Ctrl+C` to stop consuming.**

**Consuming with keys:**

```bash
# Show keys and values
docker-compose exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic test-topic \
  --from-beginning \
  --property "print.key=true" \
  --property "key.separator=:"
```

**Expected output:**

```
user1:Hello from user1
user2:Hello from user2
user1:Another message from user1
```

**Consumer groups:**

```bash
# Consume as part of a consumer group
docker-compose exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic test-topic \
  --group my-consumer-group
```

**List consumer groups:**

```bash
docker-compose exec kafka kafka-consumer-groups --list \
  --bootstrap-server localhost:9092
```

**Describe consumer group:**

```bash
docker-compose exec kafka kafka-consumer-groups --describe \
  --bootstrap-server localhost:9092 \
  --group my-consumer-group
```

## Connecting from Applications

### Connection Properties

**From within Docker network:**

```properties
bootstrap.servers=kafka:29092
```

**From host machine (dev container or WSL):**

```properties
bootstrap.servers=localhost:9092
```

**From external machine:**

```properties
# Requires updating KAFKA_ADVERTISED_LISTENERS in docker-compose.yml
bootstrap.servers=<your-host-ip>:9092
```

### Python Example

```python
from kafka import KafkaProducer, KafkaConsumer
import json

# Producer example
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Send a message
producer.send('test-topic', {'key': 'value', 'message': 'Hello from Python!'})
producer.flush()

# Consumer example
consumer = KafkaConsumer(
    'test-topic',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

# Read messages
for message in consumer:
    print(f"Received: {message.value}")
```

### Java Example

```java
import org.apache.kafka.clients.producer.*;
import org.apache.kafka.clients.consumer.*;
import java.util.*;

// Producer example
Properties props = new Properties();
props.put("bootstrap.servers", "localhost:9092");
props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
props.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer");

Producer<String, String> producer = new KafkaProducer<>(props);
producer.send(new ProducerRecord<>("test-topic", "key", "Hello from Java!"));
producer.close();

// Consumer example
props.put("group.id", "java-consumer-group");
props.put("key.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
props.put("value.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");

Consumer<String, String> consumer = new KafkaConsumer<>(props);
consumer.subscribe(Arrays.asList("test-topic"));

while (true) {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
    for (ConsumerRecord<String, String> record : records) {
        System.out.printf("Received: %s%n", record.value());
    }
}
```

## Monitoring and Logs

### View Real-Time Logs

```bash
# All services
docker-compose logs -f

# Kafka only
docker-compose logs -f kafka

# Zookeeper only
docker-compose logs -f zookeeper

# Last 100 lines
docker-compose logs --tail=100 kafka
```

### Check Container Health

```bash
# View health status
docker-compose ps

# Detailed health check info
docker inspect kafka1 --format='{{json .State.Health}}' | jq

docker inspect zookeeper --format='{{json .State.Health}}' | jq
```

### Access Persistent Logs

```bash
# Kafka server logs
sudo ls -lh /logs/kafka/

# View specific log file
sudo tail -f /logs/kafka/server.log
```

### Monitor Resource Usage

```bash
# Resource usage stats
docker stats kafka1 zookeeper
```

## Stopping and Managing Services

### Stop Services (preserves data)

```bash
docker-compose stop
```

This stops the containers but keeps all data intact. Restart with `docker-compose start`.

### Start Stopped Services

```bash
docker-compose start
```

### Restart Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart kafka
```

### Stop and Remove Containers

```bash
docker-compose down
```

**What this does:**

- Stops all services
- Removes containers
- Removes network
- **Preserves volumes** (data persists)

### Remove Everything (including data)

```bash
docker-compose down -v
```

**⚠️ WARNING:** This deletes all Kafka and Zookeeper data! Use only for a fresh start.

### Rebuild After Changes

```bash
# Rebuild images
docker-compose build

# Restart with new images
docker-compose up -d
```

## Docker Commands Reference

### Essential Commands

| Command | Description |
|---------|-------------|
| `docker-compose up -d` | Build and start services in background |
| `docker-compose down` | Stop and remove containers |
| `docker-compose ps` | List running services |
| `docker-compose logs -f` | Follow logs for all services |
| `docker-compose exec kafka bash` | Access Kafka container shell |
| `docker-compose restart kafka` | Restart Kafka service |
| `docker-compose build` | Rebuild images from Dockerfile |

### Kafka-Specific Commands (inside container)

| Command | Description |
|---------|-------------|
| `kafka-topics --list` | List all topics |
| `kafka-topics --create` | Create a new topic |
| `kafka-topics --describe` | Show topic details |
| `kafka-console-producer` | Start console producer |
| `kafka-console-consumer` | Start console consumer |
| `kafka-consumer-groups --list` | List consumer groups |
| `kafka-configs --describe` | Show broker/topic configs |

## Troubleshooting

### Issue: Containers won't start

**Symptoms:**

```
Error response from daemon: driver failed programming external connectivity
```

**Solution:**

```bash
# Check if ports are in use
sudo lsof -i :9092
sudo lsof -i :2181

# Kill processes using the ports
sudo kill -9 <PID>

# Restart Docker
sudo systemctl restart docker

# Try again
docker-compose up -d
```

### Issue: Kafka won't connect to Zookeeper

**Symptoms:**

```
[2024-01-01 12:00:00,000] WARN [ZooKeeperClient] Unable to connect to Zookeeper
```

**Solution:**

```bash
# Check Zookeeper is healthy
docker-compose ps
echo ruok | nc localhost 2181

# Check network connectivity
docker-compose exec kafka ping zookeeper

# Restart in correct order
docker-compose down
docker-compose up -d
```

### Issue: "No space left on device"

**Solution:**

```bash
# Check disk space
df -h

# Clean up Docker resources
docker system prune -a --volumes

# Remove old logs
sudo rm -rf /data/kafka/logs/*
sudo rm -rf /data/zookeeper/*
```

### Issue: Permission denied errors

**Solution:**

```bash
# Fix ownership
sudo chown -R 1000:1000 /data/kafka
sudo chown -R 1000:1000 /data/zookeeper
sudo chown -R 1000:1000 /logs/kafka

# Restart services
docker-compose restart
```

### Issue: Cannot connect from application

**Symptoms:**

```
Connection to node -1 (localhost:9092) could not be established
```

**Solution:**

1. **Check if Kafka is running:**

   ```bash
   docker-compose ps
   ```

2. **Verify port mapping:**

   ```bash
   docker port kafka1
   ```

3. **Test connection:**

   ```bash
   nc -zv localhost 9092
   ```

4. **Check advertised listeners:**
   - If connecting from host: use `localhost:9092`
   - If connecting from another Docker container: use `kafka:29092`
   - Update `KAFKA_ADVERTISED_LISTENERS` in docker-compose.yml if needed

### Issue: Messages not persisting

**Symptoms:**
Messages disappear after container restart

**Solution:**

```bash
# Verify volumes are mounted
docker inspect kafka1 | grep -A 5 Mounts

# Check volume permissions
sudo ls -la /data/kafka/logs

# Verify retention settings
docker-compose exec kafka kafka-configs --describe \
  --bootstrap-server localhost:9092 \
  --entity-type brokers \
  --entity-name 1 \
  --all
```

## Advanced Topics

### Scaling to Multiple Brokers

To add more Kafka brokers, modify `docker-compose.yml`:

```yaml
services:
  kafka2:
    build: .
    image: gds-kafka:latest
    container_name: kafka2
    depends_on:
      - zookeeper
    environment:
      KAFKA_BROKER_ID: 2  # Must be unique
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_LISTENERS: INTERNAL://0.0.0.0:29093,EXTERNAL://0.0.0.0:9093
      KAFKA_ADVERTISED_LISTENERS: INTERNAL://kafka2:29093,EXTERNAL://localhost:9093
      # ... other configs
    ports:
      - "9093:9093"
    volumes:
      - /data/kafka2/logs:/data/kafka/logs
    networks:
      - kafka-network
```

### Using KRaft Mode (No Zookeeper)

Kafka 3.x+ supports KRaft mode, eliminating Zookeeper:

```yaml
# Modify docker-compose.yml
kafka:
  environment:
    KAFKA_PROCESS_ROLES: broker,controller
    KAFKA_NODE_ID: 1
    KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka:9093
    KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
    KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093
    # Remove KAFKA_ZOOKEEPER_CONNECT
```

### Enabling SSL/TLS

For production, enable SSL:

1. Generate SSL certificates
2. Mount certificates into container
3. Update listener configuration

See [Confluent SSL documentation](https://docs.confluent.io/platform/current/kafka/authentication_ssl.html) for details.

### Performance Tuning

```yaml
# Add to kafka environment in docker-compose.yml
environment:
  # Increase throughput
  KAFKA_NUM_NETWORK_THREADS: 8
  KAFKA_NUM_IO_THREADS: 8

  # Adjust buffer sizes
  KAFKA_SOCKET_SEND_BUFFER_BYTES: 102400
  KAFKA_SOCKET_RECEIVE_BUFFER_BYTES: 102400

  # Increase replica fetch size
  KAFKA_REPLICA_FETCH_MAX_BYTES: 1048576
```

## Additional Resources

- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Confluent Platform Documentation](https://docs.confluent.io/platform/current/overview.html)
- [Kafka: The Definitive Guide](https://www.confluent.io/resources/kafka-the-definitive-guide/)
- [Kafka Docker Quick Start](https://developer.confluent.io/quickstart/kafka-docker/)

## Support

For issues specific to this setup:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review container logs: `docker-compose logs`
3. Verify directory permissions
4. Ensure Docker has sufficient resources (4GB+ RAM)

For Kafka-specific questions, consult the official Apache Kafka documentation.
