# Apache Kafka Comprehensive Tutorial: Best Practices, Use Cases, and Operations

## Table of Contents

1. [Introduction to Apache Kafka](#introduction-to-apache-kafka)
2. [Core Kafka Concepts](#core-kafka-concepts)
3. [Kafka Use Cases](#kafka-use-cases)
4. [Best Practices for Topics and Partitions](#best-practices-for-topics-and-partitions)
5. [Producer Best Practices](#producer-best-practices)
6. [Consumer Best Practices](#consumer-best-practices)
7. [Performance Tuning](#performance-tuning)
8. [Monitoring and Observability](#monitoring-and-observability)
9. [Troubleshooting Common Issues](#troubleshooting-common-issues)
10. [Security Best Practices](#security-best-practices)
11. [Operational Management](#operational-management)
12. [Advanced Topics](#advanced-topics)

---

## Introduction to Apache Kafka

### What is Apache Kafka?

Apache Kafka is a distributed event streaming platform designed to handle high-throughput, real-time data streams. Originally developed by LinkedIn and now maintained by the Apache Software Foundation, Kafka has become the de facto standard for building real-time data pipelines and streaming applications.

### Key Characteristics

- **High Throughput**: Handles millions of messages per second
- **Scalability**: Horizontally scalable across multiple servers
- **Durability**: Messages are persisted to disk and replicated
- **Low Latency**: Sub-millisecond latency for real-time processing
- **Fault Tolerance**: Automatic failover and replication

### When to Use Kafka

✅ **Good Fit:**

- Real-time data pipelines
- Event-driven architectures
- Log aggregation
- Stream processing
- Metrics collection
- Microservices communication
- Change Data Capture (CDC)

❌ **Not Ideal For:**

- Simple request-response patterns (use REST APIs)
- Small-scale messaging (use RabbitMQ or SQS)
- Complex transactional queries (use traditional databases)
- File storage (use S3 or HDFS)

---

## Core Kafka Concepts

### 1. **Brokers**

Kafka brokers are servers that store and serve data. A Kafka cluster consists of multiple brokers for redundancy and scalability.

**Key Points:**

- Each broker handles read/write requests from clients
- Brokers manage partition replicas
- One broker acts as the controller for cluster metadata

### 2. **Topics**

Topics are logical channels or categories where messages are published. Think of them as database tables or message queues.

**Naming Conventions:**

```
# Hierarchical naming
<organization>.<team>.<dataset>.<event-type>

# Examples
acme.payments.transactions.created
acme.inventory.products.updated
acme.analytics.clickstream.pageviews
```

### 3. **Partitions**

Partitions are the unit of parallelism in Kafka. A topic is split into partitions, distributed across brokers.

**Key Characteristics:**

- Ordered, immutable sequence of messages
- Each message has a unique offset
- Messages with the same key go to the same partition
- Enables parallel processing

**Partition Diagram:**

```
Topic: orders
├── Partition 0: [msg1, msg2, msg3] → Broker 1
├── Partition 1: [msg4, msg5, msg6] → Broker 2
└── Partition 2: [msg7, msg8, msg9] → Broker 3
```

### 4. **Replication**

Replication provides fault tolerance by maintaining multiple copies of data.

**Replication Factor:**

- **RF=1**: No redundancy (single point of failure)
- **RF=2**: Can tolerate 1 broker failure
- **RF=3**: Can tolerate 2 broker failures (recommended for production)

**In-Sync Replicas (ISR):**

- Replicas that are up-to-date with the leader
- Only ISR members can become the leader
- Kafka commits writes only after ISR acknowledgment

### 5. **Producers**

Producers publish messages to topics.

**Producer Workflow:**

```
Producer → Serialization → Partitioner → Compression → Broker
```

### 6. **Consumers**

Consumers read messages from topics, organized into consumer groups for parallel processing.

**Consumer Group Benefits:**

- Load balancing across multiple consumers
- Automatic rebalancing on consumer join/leave
- At-most-once or at-least-once processing semantics

### 7. **Offsets**

Offsets track the position of a consumer in a partition.

**Offset Management:**

- Kafka stores consumer offsets in `__consumer_offsets` topic
- Enables resume from last committed position after failure
- Consumers can reset offsets to replay messages

---

## Kafka Use Cases

### 1. **Messaging System**

Replace traditional message brokers with Kafka for higher throughput and durability.

**Example:**

```python
# Order processing system
# Producer: E-commerce application
# Consumer: Order fulfillment service

producer.send('orders.created', {
    'order_id': '12345',
    'customer_id': 'CUST001',
    'items': [...],
    'total': 99.99
})
```

**Benefits:**

- Built-in partitioning for scalability
- Message persistence for reliability
- Multiple consumers can process independently

### 2. **Activity Tracking**

Track user activities across websites and applications.

**Example:**

```python
# Clickstream tracking
producer.send('clickstream.pageviews', {
    'user_id': 'USER123',
    'page': '/products/laptop',
    'timestamp': 1699876543,
    'session_id': 'SESSION456'
})
```

**Use Cases:**

- Real-time analytics dashboards
- User behavior analysis
- Personalization engines
- A/B testing

### 3. **Log Aggregation**

Centralize logs from multiple services for analysis and monitoring.

**Architecture:**

```
App Server 1 → Kafka Producer → orders.logs
App Server 2 → Kafka Producer → orders.logs
App Server 3 → Kafka Producer → orders.logs
                                    ↓
                              Consumer Group
                                    ↓
                        [ELK Stack / Splunk / Datadog]
```

**Benefits:**

- Low-latency log collection
- Decoupling log producers from consumers
- Easy to add new log consumers

### 4. **Stream Processing**

Transform, aggregate, and enrich data in real-time.

**Example: Real-time Fraud Detection**

```python
# Using Kafka Streams
stream = builder.stream('transactions')

fraud_alerts = stream.filter(
    lambda key, value: value['amount'] > 10000 and
                      value['country'] != value['user_country']
).to('fraud.alerts')
```

**Use Cases:**

- Real-time recommendations
- Anomaly detection
- ETL pipelines
- Aggregations and windowing

### 5. **Event Sourcing**

Store application state as a sequence of events.

**Example:**

```python
# Banking application
events = [
    {'type': 'AccountCreated', 'account_id': 'ACC001', 'balance': 0},
    {'type': 'MoneyDeposited', 'account_id': 'ACC001', 'amount': 1000},
    {'type': 'MoneyWithdrawn', 'account_id': 'ACC001', 'amount': 200}
]

# Current state = replay all events
current_balance = sum(e['amount'] for e in events if e['type'] == 'MoneyDeposited')
               - sum(e['amount'] for e in events if e['type'] == 'MoneyWithdrawn')
```

**Benefits:**

- Complete audit trail
- Time travel (replay to any point)
- Easy debugging and troubleshooting
- Support for CQRS pattern

### 6. **Metrics and Monitoring**

Collect metrics from distributed systems.

**Architecture:**

```
Microservice 1 → metrics.cpu
Microservice 2 → metrics.memory
Microservice 3 → metrics.requests
                      ↓
              Kafka Streams Aggregation
                      ↓
            [Prometheus / Grafana]
```

### 7. **Change Data Capture (CDC)**

Capture database changes and stream them to Kafka.

**Example:**

```
PostgreSQL → Debezium Connector → Kafka Topic → Consumers
                                      ↓
                            [Search Index / Cache /
                             Analytics DB / Microservices]
```

**Use Cases:**

- Database replication
- Cache invalidation
- Search index synchronization
- Microservices data sharing

### 8. **IoT Data Collection**

Collect and process data from IoT devices.

**Example:**

```python
# Smart home sensor data
producer.send('iot.temperature', {
    'device_id': 'SENSOR123',
    'temperature': 22.5,
    'humidity': 45,
    'timestamp': 1699876543,
    'location': 'Living Room'
})
```

**Benefits:**

- Handle millions of devices
- Low latency for real-time alerts
- Store historical data for analytics

---

## Best Practices for Topics and Partitions

### Topic Design Best Practices

#### 1. **Topic Naming Conventions**

Use a hierarchical, descriptive naming scheme:

```
# Pattern: <domain>.<entity>.<event-type>
payments.transactions.created
payments.transactions.validated
payments.transactions.completed

inventory.products.updated
inventory.products.deleted

analytics.events.pageviews
analytics.events.clicks
```

**Benefits:**

- Easy to understand and discover
- Groups related topics
- Supports wildcards in security policies
- Enables logical organization

#### 2. **Topic Configuration**

**Retention Settings:**

```bash
# Time-based retention (7 days)
retention.ms=604800000

# Size-based retention (10 GB per partition)
retention.bytes=10737418240

# Delete vs. Compact
cleanup.policy=delete  # Remove old messages
cleanup.policy=compact # Keep latest value per key
```

**When to use compaction:**

- User profiles (keep latest state)
- Configuration data
- Reference data (product catalogs)

**When to use deletion:**

- Event logs
- Clickstream data
- Sensor readings

#### 3. **Choose the Right Number of Partitions**

**General Guidelines:**

```
Number of Partitions = max(
    Target Throughput / Producer Throughput per Partition,
    Target Throughput / Consumer Throughput per Partition,
    Number of Consumers in Largest Consumer Group
)
```

**Example Calculation:**

```
Target Throughput: 1000 MB/s
Producer Throughput per Partition: 10 MB/s
Consumer Throughput per Partition: 20 MB/s
Max Consumers: 50

Partitions = max(1000/10, 1000/20, 50) = max(100, 50, 50) = 100
```

**Recommendations:**

- **Small topics** (< 1 MB/s): 1-3 partitions
- **Medium topics** (1-10 MB/s): 3-10 partitions
- **Large topics** (> 10 MB/s): 10-100+ partitions

**Important Considerations:**

- More partitions = more parallelism BUT more overhead
- Each partition = separate file handles, memory
- Partition count CANNOT be decreased (only increased)
- Start with fewer partitions, scale up as needed

#### 4. **Partition Key Selection**

The partition key determines which partition a message goes to:

```python
# Example: User ID as key
producer.send('user.events',
              key=user_id,  # All events for same user → same partition
              value=event_data)
```

**Best Practices:**

✅ **Good Partition Keys:**

- User ID (events for same user stay ordered)
- Device ID (IoT data from same device)
- Order ID (all order events together)
- Session ID (user session events)

❌ **Bad Partition Keys:**

- Timestamp (hot partitions, imbalanced load)
- Random UUID (defeats ordering purpose)
- Status field with few values (skewed distribution)

**Partition Key Impact:**

```
Key = user_id → Partition = hash(user_id) % num_partitions

# Example with 3 partitions
user_123 → Partition 0
user_456 → Partition 1
user_789 → Partition 2
user_123 → Partition 0 (always same partition!)
```

#### 5. **Handle Hot Partitions**

Hot partitions occur when one partition receives much more traffic than others.

**Symptoms:**

- Uneven broker load
- One consumer lags behind others
- Slow message processing

**Solutions:**

```python
# Option 1: Add sub-key for distribution
key = f"{user_id}:{random.randint(0, 9)}"  # Spreads across 10 sub-partitions

# Option 2: Use custom partitioner
class CustomPartitioner(Partitioner):
    def partition(self, key, all_partitions, available):
        if is_hot_key(key):
            # Distribute hot keys across multiple partitions
            return hash(key + random.random()) % len(all_partitions)
        return hash(key) % len(all_partitions)
```

#### 6. **Replication Factor Best Practices**

**Production Recommendations:**

```bash
# Minimum for production
replication.factor=3

# Critical data
replication.factor=5

# Development/testing
replication.factor=1
```

**Why 3?**

- Survives 2 broker failures
- Balances durability and overhead
- Industry standard

**Configuration:**

```bash
# Broker default
default.replication.factor=3

# Topic-specific override
bin/kafka-topics.sh --create \
    --topic critical.transactions \
    --replication-factor 5 \
    --partitions 10
```

---

## Producer Best Practices

### 1. **Acknowledgment Settings (acks)**

Controls when producer considers write successful:

```python
# acks=0: Fire and forget (no acknowledgment)
producer = KafkaProducer(acks=0)  # Fastest, least safe
# Use for: Non-critical logs, metrics

# acks=1: Leader acknowledgment
producer = KafkaProducer(acks=1)  # Balanced
# Use for: Most applications

# acks=all: All ISR acknowledgment
producer = KafkaProducer(acks='all')  # Safest, slowest
# Use for: Financial transactions, critical data
```

**Production Recommendation:**

```python
producer = KafkaProducer(
    acks='all',  # Wait for all ISR replicas
    retries=2147483647,  # Max retries
    max_in_flight_requests_per_connection=5,
    enable_idempotence=True  # Exactly-once semantics
)
```

### 2. **Idempotent Producer**

Prevents duplicate messages even with retries:

```python
producer = KafkaProducer(
    enable_idempotence=True,  # Enables exactly-once
    acks='all',
    retries=2147483647
)
```

**How it works:**

- Producer assigns sequence number to each message
- Broker detects and rejects duplicates
- No application code changes needed

**When to enable:**

- Always (for production)
- Minimal overhead
- Prevents duplicates from network retries

### 3. **Batching and Compression**

Increase throughput by batching messages:

```python
producer = KafkaProducer(
    # Batching
    batch_size=32768,  # 32 KB batches
    linger_ms=10,  # Wait up to 10ms to fill batch

    # Compression
    compression_type='snappy',  # or 'gzip', 'lz4', 'zstd'

    # Buffer
    buffer_memory=67108864  # 64 MB buffer
)
```

**Compression Comparison:**

| Type   | Ratio | CPU  | Speed | Use Case |
|--------|-------|------|-------|----------|
| none   | 1x    | Low  | Fast  | Low latency required |
| snappy | 2x    | Low  | Fast  | Good default choice |
| lz4    | 2x    | Low  | Fast  | Similar to snappy |
| gzip   | 3x    | High | Slow  | High compression needed |
| zstd   | 3x    | Med  | Med   | Best balance (Kafka 2.1+) |

**Recommendation:** Use `snappy` or `lz4` for most cases

### 4. **Error Handling and Retries**

```python
from kafka import KafkaProducer
from kafka.errors import KafkaError
import logging

producer = KafkaProducer(
    retries=3,
    retry_backoff_ms=100,  # Wait 100ms between retries
    request_timeout_ms=30000  # 30 second timeout
)

def send_message_safely(topic, key, value):
    try:
        future = producer.send(topic, key=key, value=value)
        record_metadata = future.get(timeout=10)  # Block for result

        logging.info(f"Sent to {record_metadata.topic} partition {record_metadata.partition}")
        return True

    except KafkaError as e:
        logging.error(f"Failed to send message: {e}")
        # Handle error: retry, dead letter queue, alert, etc.
        return False
```

### 5. **Partitioning Strategy**

```python
# Option 1: Key-based partitioning (default)
producer.send('orders',
              key=order_id.encode(),  # Same order → same partition
              value=order_data)

# Option 2: Round-robin (no key)
producer.send('logs', value=log_entry)  # Distributes evenly

# Option 3: Custom partitioner
class CustomPartitioner(Partitioner):
    def partition(self, key, all_partitions, available):
        # Custom logic
        if key.startswith(b'premium'):
            return all_partitions[0]  # Premium customers to first partition
        return hash(key) % len(all_partitions)

producer = KafkaProducer(partitioner=CustomPartitioner())
```

### 6. **Monitoring Producer Metrics**

Key metrics to track:

```python
# Producer metrics
metrics = producer.metrics()

# Important metrics:
# - record-send-rate: Messages sent per second
# - record-error-rate: Failed sends per second
# - request-latency-avg: Average request latency
# - outgoing-byte-rate: Throughput in bytes/sec
# - batch-size-avg: Average batch size
# - compression-rate-avg: Compression ratio
```

---

## Consumer Best Practices

### 1. **Consumer Groups**

Use consumer groups for parallel processing:

```python
# All consumers with same group_id share the work
consumer1 = KafkaConsumer(
    'orders',
    group_id='order-processing-group',
    bootstrap_servers=['localhost:9092']
)

consumer2 = KafkaConsumer(
    'orders',
    group_id='order-processing-group',  # Same group
    bootstrap_servers=['localhost:9092']
)

# Kafka automatically assigns partitions to consumers
# If topic has 6 partitions and 3 consumers:
# Consumer 1: Partitions 0, 1
# Consumer 2: Partitions 2, 3
# Consumer 3: Partitions 4, 5
```

**Group Sizing:**

```
Optimal Consumers = Number of Partitions

# More consumers than partitions = some idle
# Fewer consumers = some process multiple partitions
```

### 2. **Offset Management**

```python
consumer = KafkaConsumer(
    'orders',
    group_id='processors',

    # Offset reset behavior
    auto_offset_reset='earliest',  # or 'latest' or 'none'

    # Commit strategy
    enable_auto_commit=False,  # Manual commit recommended

    # Session timeout
    session_timeout_ms=30000,  # 30 seconds
    heartbeat_interval_ms=3000  # 3 seconds
)

# Manual offset commit
for message in consumer:
    try:
        process_message(message)

        # Commit after successful processing
        consumer.commit()  # Synchronous
        # OR
        consumer.commit_async()  # Asynchronous

    except Exception as e:
        logging.error(f"Processing failed: {e}")
        # Don't commit - message will be reprocessed
```

**Commit Strategies:**

| Strategy | Pros | Cons | Use Case |
|----------|------|------|----------|
| Auto-commit | Simple | May lose/duplicate data | Non-critical logs |
| Sync commit | Safe, precise | Slower | Critical data |
| Async commit | Fast | May miss on crash | High throughput needed |

### 3. **Rebalancing**

Rebalancing occurs when consumers join or leave the group:

```python
from kafka import KafkaConsumer
from kafka import TopicPartition

def on_assign(consumer, partitions):
    print(f"Assigned partitions: {partitions}")
    # Initialize resources for these partitions

def on_revoke(consumer, partitions):
    print(f"Revoked partitions: {partitions}")
    # Clean up resources
    # Commit offsets before losing partitions

consumer = KafkaConsumer(
    'orders',
    group_id='processors',
    on_assign=on_assign,
    on_revoke=on_revoke,

    # Rebalance configuration
    max_poll_interval_ms=300000,  # 5 minutes max between polls
    session_timeout_ms=45000,  # 45 second session timeout
    heartbeat_interval_ms=3000  # 3 second heartbeat
)
```

**Minimize Rebalancing:**

- Keep consumers stable (avoid crashes)
- Tune `max_poll_interval_ms` for your processing time
- Process messages quickly
- Use incremental cooperative rebalancing (Kafka 2.4+)

### 4. **At-Least-Once vs. Exactly-Once Semantics**

**At-Least-Once (Default):**

```python
consumer = KafkaConsumer(
    'orders',
    enable_auto_commit=False
)

for message in consumer:
    process_message(message)  # Process first
    consumer.commit()  # Then commit

# If crash before commit → message reprocessed (duplicate)
```

**Exactly-Once:**

```python
# Requires idempotent consumers or transactional reads
consumer = KafkaConsumer(
    'orders',
    isolation_level='read_committed',  # Only read committed transactions
    group_id='exactly-once-processors'
)

# Combine with idempotent processing:
# - Deduplicate based on message key/id
# - Use database constraints (unique keys)
# - Store offsets in same transaction as processing
```

### 5. **Parallel Processing Within Consumer**

Process messages concurrently while maintaining order per partition:

```python
from concurrent.futures import ThreadPoolExecutor
import threading

consumer = KafkaConsumer('orders', group_id='processors')
executor = ThreadPoolExecutor(max_workers=10)

# Track futures per partition
partition_futures = {}

for message in consumer:
    partition = message.partition

    # Wait for previous message from same partition to complete
    if partition in partition_futures:
        partition_futures[partition].result()  # Wait for completion

    # Submit new processing task
    future = executor.submit(process_message, message)
    partition_futures[partition] = future

    # Commit after all partitions processed
    if len(partition_futures) >= consumer.assignment():
        for f in partition_futures.values():
            f.result()  # Wait for all
        consumer.commit()
        partition_futures.clear()
```

### 6. **Consumer Monitoring**

```python
# Key metrics to monitor:
metrics = consumer.metrics()

# Important metrics:
# - records-consumed-rate: Messages/second
# - fetch-latency-avg: Time to fetch messages
# - records-lag-max: How far behind consumer is
# - commit-latency-avg: Time to commit offsets
# - fetch-size-avg: Average fetch size
```

---

## Performance Tuning

### Broker-Level Tuning

```properties
# config/server.properties

# 1. Network Threads (handle client requests)
num.network.threads=8  # Set to # of CPUs

# 2. I/O Threads (handle disk operations)
num.io.threads=16  # Set to # of disks × 2

# 3. Socket Buffer Sizes
socket.send.buffer.bytes=1048576  # 1 MB
socket.receive.buffer.bytes=1048576  # 1 MB
socket.request.max.bytes=104857600  # 100 MB

# 4. Log Configuration
log.segment.bytes=1073741824  # 1 GB segments
log.roll.hours=168  # Roll every 7 days
log.retention.hours=168  # Keep for 7 days

# 5. Replication
num.replica.fetchers=4  # Parallel replica fetching
replica.fetch.max.bytes=1048576  # 1 MB

# 6. Compression
compression.type=snappy

# 7. JVM Settings (in kafka-server-start.sh)
export KAFKA_HEAP_OPTS="-Xmx6G -Xms6G"  # 6 GB heap
export KAFKA_JVM_PERFORMANCE_OPTS="-XX:+UseG1GC -XX:MaxGCPauseMillis=20"
```

### Producer Tuning

```python
producer = KafkaProducer(
    # Batching
    batch_size=65536,  # 64 KB (larger = higher throughput)
    linger_ms=10,  # Wait 10ms to accumulate batch

    # Compression
    compression_type='snappy',

    # Buffer
    buffer_memory=134217728,  # 128 MB

    # Request Size
    max_request_size=1048576,  # 1 MB

    # Pipelining
    max_in_flight_requests_per_connection=5,

    # Timeout
    request_timeout_ms=30000  # 30 seconds
)
```

### Consumer Tuning

```python
consumer = KafkaConsumer(
    # Fetch Size
    fetch_min_bytes=1024,  # 1 KB minimum
    fetch_max_bytes=52428800,  # 50 MB maximum
    fetch_max_wait_ms=500,  # Wait up to 500ms

    # Per-partition fetch size
    max_partition_fetch_bytes=1048576,  # 1 MB

    # Poll
    max_poll_records=500,  # Process 500 records per poll
    max_poll_interval_ms=300000,  # 5 minutes max processing time

    # Session
    session_timeout_ms=45000,  # 45 seconds
    heartbeat_interval_ms=3000  # 3 seconds
)
```

### OS-Level Tuning

```bash
# 1. File Descriptors
ulimit -n 100000

# 2. Swap
# Disable swap or set swappiness low
sudo sysctl vm.swappiness=1

# 3. File System
# Use XFS or ext4
# Mount with noatime to reduce writes

# 4. Network
# Increase socket buffer sizes
sudo sysctl -w net.core.rmem_max=134217728
sudo sysctl -w net.core.wmem_max=134217728
sudo sysctl -w net.ipv4.tcp_rmem="4096 87380 134217728"
sudo sysctl -w net.ipv4.tcp_wmem="4096 65536 134217728"
```

---

## Monitoring and Observability

### Key Metrics to Monitor

#### Broker Metrics

```bash
# 1. Throughput
kafka.server:type=BrokerTopicMetrics,name=MessagesInPerSec
kafka.server:type=BrokerTopicMetrics,name=BytesInPerSec
kafka.server:type=BrokerTopicMetrics,name=BytesOutPerSec

# 2. Request Latency
kafka.network:type=RequestMetrics,name=TotalTimeMs,request=Produce
kafka.network:type=RequestMetrics,name=TotalTimeMs,request=Fetch

# 3. Under-Replicated Partitions (CRITICAL)
kafka.server:type=ReplicaManager,name=UnderReplicatedPartitions
# Should always be 0

# 4. Offline Partitions (CRITICAL)
kafka.controller:type=KafkaController,name=OfflinePartitionsCount
# Should always be 0

# 5. Active Controller Count (CRITICAL)
kafka.controller:type=KafkaController,name=ActiveControllerCount
# Should always be 1

# 6. Request Handler Utilization
kafka.server:type=KafkaRequestHandlerPool,name=RequestHandlerAvgIdlePercent
# Should be > 0.3 (30% idle)
```

#### Producer Metrics

```python
# Monitor these in application metrics
metrics = producer.metrics()

# Key metrics:
record_send_rate = metrics['record-send-rate'].value
record_error_rate = metrics['record-error-rate'].value
request_latency_avg = metrics['request-latency-avg'].value
buffer_available_bytes = metrics['buffer-available-bytes'].value
```

#### Consumer Metrics

```python
metrics = consumer.metrics()

# Key metrics:
records_consumed_rate = metrics['records-consumed-rate'].value
records_lag_max = metrics['records-lag-max'].value  # CRITICAL
fetch_latency_avg = metrics['fetch-latency-avg'].value
commit_latency_avg = metrics['commit-latency-avg'].value
```

### Consumer Lag Monitoring

Consumer lag is the most important metric for consumers:

```bash
# Check consumer lag
bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
    --describe --group my-consumer-group

# Output:
# GROUP           TOPIC       PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG
# my-group        orders      0          100             150             50
# my-group        orders      1          200             200             0
```

**Lag Thresholds:**

- **< 1000**: Healthy
- **1000-10000**: Warning (investigate)
- **> 10000**: Critical (consumers can't keep up)

**Solutions for High Lag:**

1. Add more consumers
2. Optimize processing logic
3. Increase `max_poll_records`
4. Scale horizontally

### Monitoring Tools

#### 1. **JMX Metrics**

```bash
# Enable JMX in Kafka
export JMX_PORT=9999

# Query JMX using jmxterm
java -jar jmxterm.jar -l localhost:9999
> get -b kafka.server:type=BrokerTopicMetrics,name=MessagesInPerSec *
```

#### 2. **Kafka Manager / CMAK**

Web UI for managing Kafka clusters:

```bash
# https://github.com/yahoo/CMAK
docker run -p 9000:9000 -e ZK_HOSTS="zookeeper:2181" hlebalbau/kafka-manager
```

#### 3. **Confluent Control Center**

Enterprise monitoring solution (requires Confluent Platform):

- Real-time monitoring
- Consumer lag tracking
- Schema registry integration
- Performance metrics

#### 4. **Prometheus + Grafana**

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'kafka'
    static_configs:
      - targets: ['kafka1:9999', 'kafka2:9999', 'kafka3:9999']
    metrics_path: '/metrics'
```

**Popular Grafana Dashboards:**

- Kafka Overview (ID: 721)
- Kafka Exporter (ID: 7589)

#### 5. **Burrow (LinkedIn)**

Consumer lag monitoring tool:

```bash
# https://github.com/linkedin/Burrow
docker run -p 8000:8000 linkedin/burrow
```

### Alerting Rules

```yaml
# Example Prometheus alerts

# Alert if under-replicated partitions exist
- alert: UnderReplicatedPartitions
  expr: kafka_server_replicamanager_underreplicatedpartitions > 0
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "Kafka has under-replicated partitions"

# Alert if consumer lag is high
- alert: ConsumerLagHigh
  expr: kafka_consumergroup_lag > 10000
  for: 10m
  labels:
    severity: warning
  annotations:
    summary: "Consumer {{ $labels.group }} has high lag"

# Alert if no active controller
- alert: NoActiveController
  expr: kafka_controller_kafkacontroller_activecontrollercount != 1
  for: 1m
  labels:
    severity: critical
  annotations:
    summary: "No active Kafka controller"
```

---

## Troubleshooting Common Issues

### Issue 1: High Consumer Lag

**Symptoms:**

- Consumer falling behind
- `records-lag-max` metric increasing
- Processing delays

**Diagnosis:**

```bash
# Check consumer lag
bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
    --describe --group my-group

# Check consumer metrics
# Look for slow fetch times, low consumption rate
```

**Solutions:**

1. **Add more consumers:**

```bash
# Increase consumer instances to match partition count
# Each consumer will handle fewer partitions
```

2. **Optimize processing:**

```python
# Profile and optimize message processing
import cProfile

def process_messages():
    for message in consumer:
        process_message(message)

cProfile.run('process_messages()')
```

3. **Increase fetch size:**

```python
consumer = KafkaConsumer(
    fetch_max_bytes=52428800,  # 50 MB
    max_partition_fetch_bytes=5242880  # 5 MB per partition
)
```

4. **Parallel processing:**

```python
# Process messages in parallel (maintain partition order)
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=10)
futures = []

for message in consumer:
    future = executor.submit(process_message, message)
    futures.append(future)

    if len(futures) >= 100:
        for f in futures:
            f.result()
        consumer.commit()
        futures.clear()
```

### Issue 2: Under-Replicated Partitions

**Symptoms:**

- `UnderReplicatedPartitions` metric > 0
- Replicas not in sync
- Potential data loss risk

**Diagnosis:**

```bash
# Check under-replicated partitions
bin/kafka-topics.sh --bootstrap-server localhost:9092 \
    --describe --under-replicated-partitions

# Check broker logs
tail -f /var/log/kafka/server.log | grep -i "replica"
```

**Root Causes:**

1. Network issues between brokers
2. Broker overload (CPU, disk I/O)
3. Slow disk performance
4. Insufficient memory

**Solutions:**

1. **Check network connectivity:**

```bash
# Test network between brokers
ping kafka-broker-2
telnet kafka-broker-2 9092
```

2. **Check disk I/O:**

```bash
# Monitor disk I/O
iostat -x 1

# Check disk usage
df -h
```

3. **Increase replica fetch threads:**

```properties
# server.properties
num.replica.fetchers=8
```

4. **Adjust ISR timeout:**

```properties
# Increase if replicas are temporarily slow
replica.lag.time.max.ms=30000  # 30 seconds
```

### Issue 3: Broker Running Out of Disk Space

**Symptoms:**

- Disk usage at 100%
- Write failures
- Broker crashes

**Diagnosis:**

```bash
# Check disk usage
df -h /var/lib/kafka

# Check topic retention
bin/kafka-configs.sh --bootstrap-server localhost:9092 \
    --describe --entity-type topics
```

**Solutions:**

1. **Reduce retention:**

```bash
# Set retention to 3 days
bin/kafka-configs.sh --bootstrap-server localhost:9092 \
    --alter --entity-type topics --entity-name my-topic \
    --add-config retention.ms=259200000

# Set size-based retention
bin/kafka-configs.sh --bootstrap-server localhost:9092 \
    --alter --entity-type topics --entity-name my-topic \
    --add-config retention.bytes=10737418240  # 10 GB
```

2. **Enable log compaction:**

```bash
bin/kafka-configs.sh --bootstrap-server localhost:9092 \
    --alter --entity-type topics --entity-name my-topic \
    --add-config cleanup.policy=compact
```

3. **Delete old topics:**

```bash
bin/kafka-topics.sh --bootstrap-server localhost:9092 \
    --delete --topic obsolete-topic
```

4. **Add more disk space or brokers:**

```bash
# Add new broker and rebalance partitions
bin/kafka-reassign-partitions.sh --bootstrap-server localhost:9092 \
    --generate --broker-list "1,2,3,4" \
    --topics-to-move-json-file topics.json
```

### Issue 4: Producer Timeouts

**Symptoms:**

- `TimeoutException` in producer
- Messages fail to send
- High `request-latency-avg`

**Diagnosis:**

```python
# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Check producer metrics
metrics = producer.metrics()
print(f"Request latency: {metrics['request-latency-avg'].value}")
print(f"Buffer available: {metrics['buffer-available-bytes'].value}")
```

**Solutions:**

1. **Increase timeouts:**

```python
producer = KafkaProducer(
    request_timeout_ms=60000,  # 60 seconds
    delivery_timeout_ms=120000  # 2 minutes total
)
```

2. **Check network connectivity:**

```bash
# Test connection to broker
telnet kafka-broker-1 9092

# Check DNS resolution
nslookup kafka-broker-1
```

3. **Increase buffer memory:**

```python
producer = KafkaProducer(
    buffer_memory=134217728  # 128 MB
)
```

4. **Reduce batch size:**

```python
producer = KafkaProducer(
    batch_size=16384,  # 16 KB
    linger_ms=0  # Send immediately
)
```

### Issue 5: Consumer Rebalancing Too Frequently

**Symptoms:**

- Frequent rebalance logs
- Processing interrupted
- High latency

**Diagnosis:**

```bash
# Check consumer logs
tail -f consumer.log | grep -i "rebalance"

# Common causes:
# - Consumer taking too long to process
# - Heartbeat missed
# - Consumer crash/restart
```

**Solutions:**

1. **Increase max poll interval:**

```python
consumer = KafkaConsumer(
    max_poll_interval_ms=600000,  # 10 minutes
    max_poll_records=100  # Process fewer records per poll
)
```

2. **Tune heartbeat settings:**

```python
consumer = KafkaConsumer(
    session_timeout_ms=60000,  # 60 seconds
    heartbeat_interval_ms=5000  # 5 seconds
)
```

3. **Process messages faster:**

```python
# Optimize message processing
# Use async processing
# Batch database operations
```

4. **Use static membership (Kafka 2.3+):**

```python
consumer = KafkaConsumer(
    group_instance_id='consumer-1'  # Stable member ID
)
```

### Issue 6: Connection Refused / Broker Not Available

**Symptoms:**

- `Connection refused` errors
- `Broker not available` exceptions
- Clients can't connect

**Diagnosis:**

```bash
# Check if Kafka is running
ps aux | grep kafka

# Check if port is open
netstat -tuln | grep 9092

# Check broker logs
tail -f /var/log/kafka/server.log
```

**Solutions:**

1. **Verify listeners configuration:**

```properties
# server.properties
listeners=PLAINTEXT://0.0.0.0:9092
advertised.listeners=PLAINTEXT://kafka-broker-1:9092
```

2. **Check firewall rules:**

```bash
# Allow Kafka port
sudo ufw allow 9092
sudo iptables -A INPUT -p tcp --dport 9092 -j ACCEPT
```

3. **Verify DNS/hostname:**

```bash
# Ensure hostname resolves correctly
ping kafka-broker-1

# Update /etc/hosts if needed
echo "192.168.1.10 kafka-broker-1" | sudo tee -a /etc/hosts
```

---

## Security Best Practices

### 1. **Enable SSL/TLS Encryption**

```properties
# server.properties
listeners=SSL://0.0.0.0:9093
advertised.listeners=SSL://kafka-broker-1:9093

# SSL Configuration
ssl.keystore.location=/var/private/ssl/kafka.server.keystore.jks
ssl.keystore.password=keystore-password
ssl.key.password=key-password
ssl.truststore.location=/var/private/ssl/kafka.server.truststore.jks
ssl.truststore.password=truststore-password

# Client authentication (optional)
ssl.client.auth=required
```

**Client Configuration:**

```python
producer = KafkaProducer(
    bootstrap_servers=['kafka-broker-1:9093'],
    security_protocol='SSL',
    ssl_cafile='/path/to/ca-cert',
    ssl_certfile='/path/to/client-cert',
    ssl_keyfile='/path/to/client-key'
)
```

### 2. **Enable SASL Authentication**

```properties
# server.properties
listeners=SASL_SSL://0.0.0.0:9093
security.inter.broker.protocol=SASL_SSL
sasl.mechanism.inter.broker.protocol=PLAIN
sasl.enabled.mechanisms=PLAIN

# JAAS configuration
listener.name.sasl_ssl.plain.sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required \
   username="admin" \
   password="admin-secret" \
   user_admin="admin-secret" \
   user_alice="alice-secret";
```

**Client Configuration:**

```python
producer = KafkaProducer(
    bootstrap_servers=['kafka-broker-1:9093'],
    security_protocol='SASL_SSL',
    sasl_mechanism='PLAIN',
    sasl_plain_username='alice',
    sasl_plain_password='alice-secret'
)
```

### 3. **Configure ACLs (Access Control Lists)**

```bash
# Grant produce permission
bin/kafka-acls.sh --bootstrap-server localhost:9092 \
    --add --allow-principal User:alice \
    --operation Write --topic orders

# Grant consume permission
bin/kafka-acls.sh --bootstrap-server localhost:9092 \
    --add --allow-principal User:bob \
    --operation Read --topic orders \
    --group order-processors

# Grant wildcard permissions
bin/kafka-acls.sh --bootstrap-server localhost:9092 \
    --add --allow-principal User:admin \
    --operation All --topic '*' --cluster

# List ACLs
bin/kafka-acls.sh --bootstrap-server localhost:9092 \
    --list --topic orders
```

### 4. **Encryption at Rest**

```bash
# Use LUKS or dm-crypt for disk encryption
cryptsetup luksFormat /dev/sdb
cryptsetup open /dev/sdb kafka_encrypted

# Mount encrypted volume
mkfs.ext4 /dev/mapper/kafka_encrypted
mount /dev/mapper/kafka_encrypted /var/lib/kafka
```

### 5. **Network Segmentation**

```
Internet
    ↓
[Load Balancer]
    ↓
[Application Layer] (Public Network)
    ↓
[Kafka Brokers] (Private Network)
    ↓
[Zookeeper] (Isolated Network)
```

### 6. **Audit Logging**

```properties
# Enable audit logs
authorizer.class.name=kafka.security.authorizer.AclAuthorizer
log4j.logger.kafka.authorizer.logger=INFO, authorizerAppender
```

---

## Operational Management

### 1. **Adding Brokers**

```bash
# 1. Install Kafka on new server

# 2. Configure broker with unique ID
# server.properties
broker.id=4  # New unique ID

# 3. Start broker
bin/kafka-server-start.sh config/server.properties

# 4. Reassign partitions to new broker
cat topics-to-move.json
{
  "topics": [{"topic": "orders"}, {"topic": "users"}],
  "version": 1
}

bin/kafka-reassign-partitions.sh --bootstrap-server localhost:9092 \
    --topics-to-move-json-file topics-to-move.json \
    --broker-list "1,2,3,4" --generate

# 5. Execute reassignment
bin/kafka-reassign-partitions.sh --bootstrap-server localhost:9092 \
    --reassignment-json-file reassignment.json --execute

# 6. Verify completion
bin/kafka-reassign-partitions.sh --bootstrap-server localhost:9092 \
    --reassignment-json-file reassignment.json --verify
```

### 2. **Decommissioning Brokers**

```bash
# 1. Move partitions off broker
bin/kafka-reassign-partitions.sh --bootstrap-server localhost:9092 \
    --topics-to-move-json-file topics.json \
    --broker-list "1,2,3" --generate  # Exclude broker 4

# 2. Execute reassignment
bin/kafka-reassign-partitions.sh --bootstrap-server localhost:9092 \
    --reassignment-json-file reassignment.json --execute

# 3. Verify all partitions moved
bin/kafka-topics.sh --bootstrap-server localhost:9092 \
    --describe

# 4. Stop broker
bin/kafka-server-stop.sh
```

### 3. **Increasing Partitions**

```bash
# Add partitions to existing topic
bin/kafka-topics.sh --bootstrap-server localhost:9092 \
    --alter --topic orders \
    --partitions 20

# WARNING: Cannot decrease partitions!
# WARNING: Existing key-based routing may change!
```

### 4. **Changing Replication Factor**

```bash
# 1. Create reassignment plan
cat increase-replication.json
{
  "version": 1,
  "partitions": [
    {"topic": "orders", "partition": 0, "replicas": [1,2,3]},
    {"topic": "orders", "partition": 1, "replicas": [2,3,4]}
  ]
}

# 2. Execute reassignment
bin/kafka-reassign-partitions.sh --bootstrap-server localhost:9092 \
    --reassignment-json-file increase-replication.json --execute

# 3. Verify
bin/kafka-reassign-partitions.sh --bootstrap-server localhost:9092 \
    --reassignment-json-file increase-replication.json --verify
```

### 5. **Topic Management**

```bash
# List topics
bin/kafka-topics.sh --bootstrap-server localhost:9092 --list

# Describe topic
bin/kafka-topics.sh --bootstrap-server localhost:9092 \
    --describe --topic orders

# Delete topic
bin/kafka-topics.sh --bootstrap-server localhost:9092 \
    --delete --topic obsolete-topic

# Purge topic (delete and recreate)
bin/kafka-topics.sh --bootstrap-server localhost:9092 \
    --delete --topic temp-topic
bin/kafka-topics.sh --bootstrap-server localhost:9092 \
    --create --topic temp-topic --partitions 3 --replication-factor 2
```

### 6. **Consumer Group Management**

```bash
# List consumer groups
bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list

# Describe consumer group
bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
    --describe --group my-group

# Reset offsets to earliest
bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
    --group my-group --topic orders --reset-offsets --to-earliest --execute

# Reset offsets to specific timestamp
bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
    --group my-group --topic orders \
    --reset-offsets --to-datetime 2024-01-01T00:00:00.000 --execute

# Delete consumer group (must have no active members)
bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
    --delete --group my-group
```

### 7. **Backup and Recovery**

**Backup Strategies:**

1. **Mirror Maker for Replication:**

```bash
# Replicate to backup cluster
bin/connect-mirror-maker.sh connect-mirror-maker.properties
```

2. **Snapshot Log Segments:**

```bash
# Backup data directory
tar -czf kafka-backup-$(date +%Y%m%d).tar.gz /var/lib/kafka/data
```

3. **Export to Object Storage:**

```bash
# Use Kafka Connect S3 Sink
{
  "name": "s3-sink",
  "config": {
    "connector.class": "io.confluent.connect.s3.S3SinkConnector",
    "tasks.max": "1",
    "topics": "orders,users",
    "s3.bucket.name": "kafka-backups",
    "flush.size": "1000"
  }
}
```

**Recovery:**

```bash
# Stop Kafka
bin/kafka-server-stop.sh

# Restore data directory
tar -xzf kafka-backup-20240101.tar.gz -C /

# Start Kafka
bin/kafka-server-start.sh config/server.properties
```

---

## Advanced Topics

### 1. **Kafka Transactions**

For exactly-once semantics:

```python
from kafka import KafkaProducer

producer = KafkaProducer(
    transactional_id='my-transactional-producer',
    enable_idempotence=True,
    acks='all'
)

# Initialize transactions
producer.init_transactions()

try:
    # Begin transaction
    producer.begin_transaction()

    # Send messages
    producer.send('orders', value=b'order1')
    producer.send('orders', value=b'order2')
    producer.send('inventory', value=b'update1')

    # Commit transaction (all or nothing)
    producer.commit_transaction()

except Exception as e:
    # Abort transaction on error
    producer.abort_transaction()
```

### 2. **Log Compaction**

Keep only the latest value for each key:

```properties
# Topic configuration
cleanup.policy=compact
min.cleanable.dirty.ratio=0.5
segment.ms=100
```

**Use Cases:**

- User profiles
- Configuration data
- Application state

### 3. **Tiered Storage**

Store old data in cheaper storage (S3, etc.):

```properties
# Enable tiered storage (Kafka 3.6+)
remote.storage.enable=true
local.retention.ms=86400000  # Keep 1 day locally
retention.ms=2592000000  # Keep 30 days total in remote storage
```

### 4. **KRaft Mode (No Zookeeper)**

```properties
# KRaft mode configuration (Kafka 3.x+)
process.roles=broker,controller
node.id=1
controller.quorum.voters=1@kafka1:9093,2@kafka2:9093,3@kafka3:9093
listeners=PLAINTEXT://:9092,CONTROLLER://:9093
```

### 5. **Schema Registry**

Manage message schemas with Confluent Schema Registry:

```python
from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer

value_schema_str = """
{
   "namespace": "my.company",
   "name": "Order",
   "type": "record",
   "fields" : [
     {"name": "order_id", "type": "string"},
     {"name": "amount", "type": "double"}
   ]
}
"""

producer = AvroProducer({
    'bootstrap.servers': 'localhost:9092',
    'schema.registry.url': 'http://localhost:8081'
}, default_value_schema=avro.loads(value_schema_str))

producer.produce(topic='orders', value={'order_id': '123', 'amount': 99.99})
```

### 6. **Kafka Streams**

Build stream processing applications:

```java
StreamsBuilder builder = new StreamsBuilder();

KStream<String, String> orders = builder.stream("orders");

// Filter, transform, aggregate
KTable<String, Long> orderCounts = orders
    .groupByKey()
    .count();

orderCounts.toStream().to("order-counts");

KafkaStreams streams = new KafkaStreams(builder.build(), config);
streams.start();
```

---

## Conclusion

This comprehensive tutorial covered Kafka from fundamentals to advanced operations. Key takeaways:

**Design Principles:**

- Choose partition count based on throughput requirements
- Use meaningful partition keys for ordering
- Set replication factor to 3 for production
- Design topic naming conventions early

**Operational Excellence:**

- Monitor consumer lag continuously
- Set up alerting for under-replicated partitions
- Implement proper backup and recovery procedures
- Use security features (SSL, SASL, ACLs)

**Performance:**

- Tune batching and compression for throughput
- Balance parallelism with resource usage
- Monitor and optimize based on metrics
- Scale horizontally when needed

**Reliability:**

- Enable idempotence for exactly-once semantics
- Use transactions for multi-topic atomicity
- Implement proper error handling
- Test failure scenarios

## Additional Resources

- **Official Documentation**: <https://kafka.apache.org/documentation/>
- **Confluent Documentation**: <https://docs.confluent.io/>
- **Kafka Improvement Proposals (KIPs)**: <https://cwiki.apache.org/confluence/x/Ri3VAQ>
- **Kafka Summit**: <https://www.kafka-summit.org/>
- **Community Forum**: <https://forum.confluent.io/>

---

*Last Updated: November 2025*
*Based on Apache Kafka 3.6+ and industry best practices*
