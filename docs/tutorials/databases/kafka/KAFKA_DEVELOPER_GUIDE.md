# Kafka Developer's Guide: From Zero to Production

**A Practical Guide for Beginners with Real-World Examples**

## Table of Contents

1. [What is Kafka? A Simple Explanation](#what-is-kafka-a-simple-explanation)
2. [Why Use Kafka?](#why-use-kafka)
3. [Core Concepts Explained Simply](#core-concepts-explained-simply)
4. [Setting Up Your Development Environment](#setting-up-your-development-environment)
5. [Your First Kafka Application](#your-first-kafka-application)
6. [Real-World Project: Server Metrics Pipeline](#real-world-project-server-metrics-pipeline)
7. [Best Practices for Developers](#best-practices-for-developers)
8. [Common Pitfalls and How to Avoid Them](#common-pitfalls-and-how-to-avoid-them)
9. [Testing Kafka Applications](#testing-kafka-applications)
10. [Deployment and Production Readiness](#deployment-and-production-readiness)

---

## What is Kafka? A Simple Explanation

### The Restaurant Analogy

Imagine a busy restaurant:

- **Customers** (Producers) place orders
- **Kitchen Display System** (Kafka) shows all orders in sequence
- **Chefs** (Consumers) pick up orders and prepare food

The display system (Kafka) ensures:

- No orders are lost
- Multiple chefs can work simultaneously
- Orders can be reviewed later if needed
- New chefs can join and see all pending orders

### Technical Definition

**Apache Kafka** is a distributed streaming platform that:

1. **Publishes and subscribes** to streams of records (like a message queue)
2. **Stores** streams of records durably and reliably
3. **Processes** streams of records as they occur

### Real-World Analogy

Think of Kafka as a **smart conveyor belt in a factory**:

```
[Machine 1] ─┐
[Machine 2] ─┼─→ [Kafka Conveyor Belt] ─┼─→ [Worker 1]
[Machine 3] ─┘                           ├─→ [Worker 2]
                                         └─→ [Worker 3]
```

- **Machines** produce items (data)
- **Conveyor belt** (Kafka) moves and stores items temporarily
- **Workers** process items at their own pace
- **Multiple workers** can process the same items independently

---

## Why Use Kafka?

### Traditional Approach Problems

**Scenario**: You have 10 applications that need to send data to 5 different systems.

**Without Kafka:**

```
App1 ──┬──→ Database
       ├──→ Analytics System
       ├──→ Cache
       ├──→ Search Index
       └──→ Backup System

App2 ──┬──→ Database
       ├──→ Analytics System
       └──→ ... (50 connections total!)
```

**Problems:**

- 50 point-to-point connections to maintain
- If one system is slow, it affects the producer
- Difficult to add new consumers
- No replay capability
- Complex error handling

**With Kafka:**

```
App1 ──┐
App2 ──┼──→ [KAFKA] ──┼──→ Database
App3 ──┘              ├──→ Analytics
                      ├──→ Cache
                      ├──→ Search
                      └──→ Backup
```

**Benefits:**

- Only 3 producer connections + 5 consumer connections = 8 total
- Systems are decoupled (one slow consumer doesn't affect others)
- Easy to add new consumers
- Data can be replayed
- Built-in fault tolerance

### When to Use Kafka

✅ **Perfect For:**

1. **Real-time data pipelines**: Moving data between systems
2. **Event-driven architecture**: Microservices communication
3. **Activity tracking**: User clicks, page views, searches
4. **Metrics and logging**: Collecting system metrics
5. **Stream processing**: Real-time analytics and transformations
6. **Change Data Capture**: Database replication

❌ **Not Ideal For:**

1. **Simple request-response**: Use REST APIs instead
2. **Small data volumes**: Kafka has overhead
3. **Immediate consistency required**: Kafka is eventually consistent
4. **Complex transactions**: Use traditional databases

---

## Core Concepts Explained Simply

### 1. Topics: Channels for Your Data

A **topic** is like a folder or category where messages are stored.

**Example:**

```
Topic: "server-metrics"
  - Contains: CPU, memory, disk usage data

Topic: "user-clicks"
  - Contains: User interaction events

Topic: "orders"
  - Contains: E-commerce orders
```

**Naming Convention:**

```
<domain>.<entity>.<event-type>

Examples:
- monitoring.server.cpu-metrics
- ecommerce.orders.created
- analytics.user.pageviews
```

### 2. Partitions: Parallel Processing

A **partition** is a subset of a topic that allows parallel processing.

**Analogy**: Imagine a highway with multiple lanes. Each lane (partition) allows cars (messages) to move independently.

```
Topic: "server-metrics" (3 partitions)

Partition 0: [msg1] [msg2] [msg3] [msg4]
Partition 1: [msg5] [msg6] [msg7] [msg8]
Partition 2: [msg9] [msg10] [msg11] [msg12]
```

**Key Points:**

- Messages with the same key always go to the same partition
- Order is guaranteed within a partition, not across partitions
- More partitions = more parallelism

### 3. Producers: Data Writers

A **producer** sends (produces) messages to Kafka topics.

**Example:**

```python
# Your application collecting server metrics
producer.send('server-metrics', {
    'hostname': 'web-server-01',
    'cpu_percent': 45.2,
    'memory_percent': 67.8,
    'timestamp': '2024-11-12T10:30:00Z'
})
```

### 4. Consumers: Data Readers

A **consumer** reads (consumes) messages from Kafka topics.

**Example:**

```python
# Your application processing metrics
for message in consumer:
    metrics = message.value
    save_to_database(metrics)
```

### 5. Consumer Groups: Team Work

A **consumer group** is a team of consumers working together to process messages.

**Analogy**: A restaurant with multiple chefs (consumers) working from the same order queue.

```
Topic with 4 partitions:

Consumer Group "metrics-processors":
  Consumer 1 → reads from Partitions 0, 1
  Consumer 2 → reads from Partitions 2, 3

Each partition is assigned to exactly ONE consumer in a group.
```

**Benefits:**

- Load balancing: Work is distributed
- Fault tolerance: If one consumer dies, others take over
- Scalability: Add more consumers to process faster

### 6. Offsets: Bookmarks

An **offset** is like a bookmark that tracks your reading position.

```
Partition 0: [msg1] [msg2] [msg3] [msg4] [msg5]
                            ↑
                    Current offset: 3
                    (processed up to msg3)
```

**Key Points:**

- Each consumer tracks its own offset
- Offsets allow resuming after a crash
- You can reset offsets to replay messages

### 7. Brokers: Kafka Servers

A **broker** is a Kafka server that stores data and serves clients.

```
Kafka Cluster:
  Broker 1 (leader for some partitions)
  Broker 2 (leader for other partitions)
  Broker 3 (replica for fault tolerance)
```

---

## Setting Up Your Development Environment

### Prerequisites

1. **Docker and Docker Compose** (easiest way)
2. **Python 3.7+**
3. **Text editor or IDE** (VS Code, PyCharm)

### Step 1: Start Kafka with Docker

If you've set up Kafka using the docker setup in this repository:

```bash
# Navigate to kafka directory
cd /workspaces/dbtools/docker/kafka

# Start Kafka and Zookeeper
docker-compose up -d

# Verify services are running
docker-compose ps

# Expected output:
# kafka-kafka-1      running
# kafka-zookeeper-1  running

# Check logs
docker-compose logs -f kafka
```

### Step 2: Install Python Client

```bash
# Install kafka-python library
pip install kafka-python

# For our metrics project, also install:
pip install psutil  # For system metrics
pip install pyodbc  # For SQL Server connection
```

### Step 3: Verify Connection

Create a test script `test_connection.py`:

```python
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import json

def test_kafka_connection():
    """Test connection to Kafka broker"""
    try:
        # Try to create a producer
        producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            api_version=(2, 0, 2)
        )

        print("✓ Successfully connected to Kafka!")

        # Send a test message
        future = producer.send('test-topic', {'message': 'Hello Kafka!'})
        result = future.get(timeout=10)

        print(f"✓ Test message sent to partition {result.partition}")

        producer.close()
        return True

    except KafkaError as e:
        print(f"✗ Failed to connect to Kafka: {e}")
        return False

if __name__ == "__main__":
    test_kafka_connection()
```

Run the test:

```bash
python test_connection.py
```

---

## Your First Kafka Application

### Simple Producer Example

Create `simple_producer.py`:

```python
"""
Simple Kafka Producer Example
Sends messages to a Kafka topic
"""

from kafka import KafkaProducer
import json
import time
from datetime import datetime

def create_producer():
    """Create and configure a Kafka producer"""
    producer = KafkaProducer(
        # Kafka broker address
        bootstrap_servers=['localhost:9092'],

        # Serialize message values to JSON
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),

        # Wait for all replicas to acknowledge (safest)
        acks='all',

        # Retry failed sends
        retries=3,

        # API version (use 2.0.2 for compatibility)
        api_version=(2, 0, 2)
    )
    return producer

def send_messages():
    """Send sample messages to Kafka"""
    producer = create_producer()
    topic = 'my-first-topic'

    try:
        # Send 10 messages
        for i in range(10):
            message = {
                'message_id': i,
                'text': f'Hello Kafka! Message #{i}',
                'timestamp': datetime.now().isoformat()
            }

            print(f"Sending: {message}")

            # Send message to Kafka
            future = producer.send(topic, message)

            # Wait for confirmation
            record_metadata = future.get(timeout=10)

            print(f"  ✓ Sent to partition {record_metadata.partition}, "
                  f"offset {record_metadata.offset}")

            time.sleep(1)  # Wait 1 second between messages

    except Exception as e:
        print(f"Error sending message: {e}")
    finally:
        # Always close the producer
        producer.close()
        print("\nProducer closed.")

if __name__ == "__main__":
    print("Starting Simple Producer...")
    send_messages()
```

**Run it:**

```bash
python simple_producer.py
```

### Simple Consumer Example

Create `simple_consumer.py`:

```python
"""
Simple Kafka Consumer Example
Reads messages from a Kafka topic
"""

from kafka import KafkaConsumer
import json

def create_consumer():
    """Create and configure a Kafka consumer"""
    consumer = KafkaConsumer(
        'my-first-topic',  # Topic to subscribe to

        # Kafka broker address
        bootstrap_servers=['localhost:9092'],

        # Consumer group ID (consumers with same ID share the work)
        group_id='my-first-consumer-group',

        # Start reading from the beginning if no offset exists
        auto_offset_reset='earliest',

        # Automatically commit offsets
        enable_auto_commit=True,

        # Deserialize message values from JSON
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),

        # API version
        api_version=(2, 0, 2)
    )
    return consumer

def consume_messages():
    """Consume and print messages from Kafka"""
    consumer = create_consumer()

    print("Starting Simple Consumer...")
    print("Waiting for messages... (Press Ctrl+C to stop)\n")

    try:
        # Continuously read messages
        for message in consumer:
            print(f"Received message:")
            print(f"  Topic: {message.topic}")
            print(f"  Partition: {message.partition}")
            print(f"  Offset: {message.offset}")
            print(f"  Key: {message.key}")
            print(f"  Value: {message.value}")
            print(f"  Timestamp: {message.timestamp}")
            print("-" * 50)

    except KeyboardInterrupt:
        print("\nShutting down consumer...")
    finally:
        consumer.close()
        print("Consumer closed.")

if __name__ == "__main__":
    consume_messages()
```

**Run it (in a new terminal):**

```bash
python simple_consumer.py
```

### Understanding What Just Happened

1. **Producer** sent 10 messages to topic `my-first-topic`
2. **Kafka** stored the messages in partitions
3. **Consumer** read the messages from the beginning
4. **Offsets** were automatically tracked

**Try this:**

- Stop the consumer (Ctrl+C)
- Run the producer again to send more messages
- Start the consumer again
- **Result**: Consumer picks up where it left off (thanks to offset tracking!)

---

## Real-World Project: Server Metrics Pipeline

Now let's build a complete real-world application:

**Goal**: Monitor Linux server metrics and store them in SQL Server

**Architecture:**

```
[Linux Server] → [Metrics Collector] → [Kafka] → [Database Writer] → [SQL Server]
     (psutil)        (Producer)       (Topic)      (Consumer)         (Storage)
```

### Project Structure

```
server-metrics-pipeline/
├── config.py                 # Configuration
├── metrics_collector.py      # Producer: Collects and sends metrics
├── metrics_consumer.py       # Consumer: Reads and stores metrics
├── database_setup.sql        # SQL Server table schema
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

### Step 1: Configuration

Create `config.py`:

```python
"""
Configuration for Server Metrics Pipeline
"""

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092']
KAFKA_TOPIC = 'server-metrics'
KAFKA_CONSUMER_GROUP = 'metrics-to-database'

# Metrics Collection Configuration
COLLECTION_INTERVAL_SECONDS = 5  # Collect metrics every 5 seconds

# SQL Server Configuration
SQL_SERVER_CONFIG = {
    'server': 'localhost,1433',
    'database': 'monitoring',
    'username': 'sa',
    'password': 'YourStrong@Password',
    'driver': '{ODBC Driver 17 for SQL Server}'
}

# Batch Insert Configuration
BATCH_SIZE = 100  # Insert 100 records at a time
BATCH_TIMEOUT_SECONDS = 30  # Or insert after 30 seconds
```

### Step 2: Database Setup

Create `database_setup.sql`:

```sql
-- Create database
CREATE DATABASE monitoring;
GO

USE monitoring;
GO

-- Create table for server metrics
CREATE TABLE server_metrics (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    hostname NVARCHAR(255) NOT NULL,
    timestamp DATETIME2 NOT NULL,
    cpu_percent DECIMAL(5,2) NOT NULL,
    memory_percent DECIMAL(5,2) NOT NULL,
    memory_used_mb DECIMAL(10,2) NOT NULL,
    memory_total_mb DECIMAL(10,2) NOT NULL,
    disk_percent DECIMAL(5,2) NOT NULL,
    disk_used_gb DECIMAL(10,2) NOT NULL,
    disk_total_gb DECIMAL(10,2) NOT NULL,
    network_bytes_sent BIGINT NOT NULL,
    network_bytes_recv BIGINT NOT NULL,
    created_at DATETIME2 DEFAULT GETDATE()
);
GO

-- Create index for faster queries
CREATE INDEX idx_hostname_timestamp
ON server_metrics(hostname, timestamp DESC);
GO

-- Create a view for latest metrics
CREATE VIEW vw_latest_metrics AS
SELECT
    hostname,
    timestamp,
    cpu_percent,
    memory_percent,
    disk_percent,
    ROW_NUMBER() OVER (PARTITION BY hostname ORDER BY timestamp DESC) as rn
FROM server_metrics;
GO

-- Query to get latest metrics per server
-- SELECT * FROM vw_latest_metrics WHERE rn = 1;
```

**Run the SQL:**

```bash
# If using Docker SQL Server
docker exec -it mssql1 /opt/mssql-tools18/bin/sqlcmd \
    -S localhost -U SA -P "YourStrong@Password" \
    -C -i /path/to/database_setup.sql
```

### Step 3: Metrics Collector (Producer)

Create `metrics_collector.py`:

```python
"""
Server Metrics Collector - Kafka Producer
Collects system metrics and sends them to Kafka
"""

from kafka import KafkaProducer
from kafka.errors import KafkaError
import psutil
import json
import time
import socket
from datetime import datetime
import logging
from config import (
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_TOPIC,
    COLLECTION_INTERVAL_SECONDS
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collects system metrics and sends to Kafka"""

    def __init__(self):
        """Initialize the metrics collector"""
        self.hostname = socket.gethostname()
        self.producer = self._create_producer()
        self.metrics_sent = 0
        self.errors = 0

    def _create_producer(self):
        """Create and configure Kafka producer"""
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,

                # Serialize values to JSON
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),

                # Reliability settings
                acks='all',  # Wait for all replicas
                retries=3,   # Retry failed sends
                max_in_flight_requests_per_connection=1,  # Preserve order

                # Performance settings
                compression_type='snappy',  # Compress messages
                linger_ms=10,  # Wait 10ms to batch messages
                batch_size=32768,  # 32KB batches

                # Timeout settings
                request_timeout_ms=30000,  # 30 second timeout

                api_version=(2, 0, 2)
            )

            logger.info("Kafka producer created successfully")
            return producer

        except KafkaError as e:
            logger.error(f"Failed to create Kafka producer: {e}")
            raise

    def collect_metrics(self):
        """Collect current system metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_mb = memory.used / (1024 * 1024)
            memory_total_mb = memory.total / (1024 * 1024)

            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_used_gb = disk.used / (1024 * 1024 * 1024)
            disk_total_gb = disk.total / (1024 * 1024 * 1024)

            # Network metrics
            network = psutil.net_io_counters()
            network_bytes_sent = network.bytes_sent
            network_bytes_recv = network.bytes_recv

            # Create metrics dictionary
            metrics = {
                'hostname': self.hostname,
                'timestamp': datetime.utcnow().isoformat(),
                'cpu_percent': round(cpu_percent, 2),
                'memory_percent': round(memory_percent, 2),
                'memory_used_mb': round(memory_used_mb, 2),
                'memory_total_mb': round(memory_total_mb, 2),
                'disk_percent': round(disk_percent, 2),
                'disk_used_gb': round(disk_used_gb, 2),
                'disk_total_gb': round(disk_total_gb, 2),
                'network_bytes_sent': network_bytes_sent,
                'network_bytes_recv': network_bytes_recv
            }

            return metrics

        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            return None

    def send_metrics(self, metrics):
        """Send metrics to Kafka"""
        try:
            # Use hostname as key to ensure same server goes to same partition
            key = self.hostname.encode('utf-8')

            # Send to Kafka
            future = self.producer.send(
                KAFKA_TOPIC,
                key=key,
                value=metrics
            )

            # Wait for confirmation (with timeout)
            record_metadata = future.get(timeout=10)

            self.metrics_sent += 1

            logger.info(
                f"Sent metrics for {self.hostname} to partition "
                f"{record_metadata.partition}, offset {record_metadata.offset}"
            )

            return True

        except KafkaError as e:
            self.errors += 1
            logger.error(f"Failed to send metrics: {e}")
            return False

    def run(self):
        """Main loop: collect and send metrics continuously"""
        logger.info(f"Starting metrics collection for {self.hostname}")
        logger.info(f"Sending metrics every {COLLECTION_INTERVAL_SECONDS} seconds")
        logger.info(f"Press Ctrl+C to stop\n")

        try:
            while True:
                # Collect metrics
                metrics = self.collect_metrics()

                if metrics:
                    # Log collected metrics
                    logger.info(
                        f"Collected: CPU={metrics['cpu_percent']}%, "
                        f"Memory={metrics['memory_percent']}%, "
                        f"Disk={metrics['disk_percent']}%"
                    )

                    # Send to Kafka
                    self.send_metrics(metrics)

                # Wait before next collection
                time.sleep(COLLECTION_INTERVAL_SECONDS)

        except KeyboardInterrupt:
            logger.info("\nShutting down metrics collector...")
            self.shutdown()
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            self.shutdown()
            raise

    def shutdown(self):
        """Clean shutdown"""
        logger.info(f"Total metrics sent: {self.metrics_sent}")
        logger.info(f"Total errors: {self.errors}")

        if self.producer:
            self.producer.flush()  # Send any pending messages
            self.producer.close()
            logger.info("Producer closed")


def main():
    """Main entry point"""
    collector = MetricsCollector()
    collector.run()


if __name__ == "__main__":
    main()
```

### Step 4: Database Writer (Consumer)

Create `metrics_consumer.py`:

```python
"""
Metrics Database Writer - Kafka Consumer
Reads metrics from Kafka and bulk inserts to SQL Server
"""

from kafka import KafkaConsumer
from kafka.errors import KafkaError
import pyodbc
import json
import logging
import time
from datetime import datetime
from config import (
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_TOPIC,
    KAFKA_CONSUMER_GROUP,
    SQL_SERVER_CONFIG,
    BATCH_SIZE,
    BATCH_TIMEOUT_SECONDS
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MetricsConsumer:
    """Consumes metrics from Kafka and writes to SQL Server"""

    def __init__(self):
        """Initialize the consumer"""
        self.consumer = self._create_consumer()
        self.db_connection = self._create_db_connection()
        self.batch = []
        self.last_insert_time = time.time()
        self.total_inserted = 0
        self.errors = 0

    def _create_consumer(self):
        """Create and configure Kafka consumer"""
        try:
            consumer = KafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,

                # Consumer group configuration
                group_id=KAFKA_CONSUMER_GROUP,

                # Offset management
                auto_offset_reset='earliest',  # Start from beginning
                enable_auto_commit=False,  # Manual commit for reliability

                # Deserialize JSON messages
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),

                # Consumer settings
                max_poll_records=500,  # Get up to 500 records per poll
                max_poll_interval_ms=300000,  # 5 minutes max processing time
                session_timeout_ms=45000,  # 45 second session timeout

                api_version=(2, 0, 2)
            )

            logger.info("Kafka consumer created successfully")
            return consumer

        except KafkaError as e:
            logger.error(f"Failed to create Kafka consumer: {e}")
            raise

    def _create_db_connection(self):
        """Create SQL Server database connection"""
        try:
            connection_string = (
                f"DRIVER={SQL_SERVER_CONFIG['driver']};"
                f"SERVER={SQL_SERVER_CONFIG['server']};"
                f"DATABASE={SQL_SERVER_CONFIG['database']};"
                f"UID={SQL_SERVER_CONFIG['username']};"
                f"PWD={SQL_SERVER_CONFIG['password']};"
                "TrustServerCertificate=yes;"
            )

            connection = pyodbc.connect(connection_string, autocommit=False)
            logger.info("Database connection established")
            return connection

        except pyodbc.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    def add_to_batch(self, metrics):
        """Add metrics to the batch for bulk insert"""
        self.batch.append(metrics)

    def should_flush_batch(self):
        """Check if batch should be flushed"""
        # Flush if batch is full
        if len(self.batch) >= BATCH_SIZE:
            return True

        # Flush if timeout reached
        time_since_last_insert = time.time() - self.last_insert_time
        if len(self.batch) > 0 and time_since_last_insert >= BATCH_TIMEOUT_SECONDS:
            return True

        return False

    def flush_batch(self):
        """Bulk insert batch to database"""
        if not self.batch:
            return

        try:
            cursor = self.db_connection.cursor()

            # Prepare bulk insert query
            insert_query = """
                INSERT INTO server_metrics (
                    hostname, timestamp, cpu_percent, memory_percent,
                    memory_used_mb, memory_total_mb, disk_percent,
                    disk_used_gb, disk_total_gb, network_bytes_sent,
                    network_bytes_recv
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            # Prepare batch data
            batch_data = []
            for metrics in self.batch:
                row = (
                    metrics['hostname'],
                    datetime.fromisoformat(metrics['timestamp']),
                    metrics['cpu_percent'],
                    metrics['memory_percent'],
                    metrics['memory_used_mb'],
                    metrics['memory_total_mb'],
                    metrics['disk_percent'],
                    metrics['disk_used_gb'],
                    metrics['disk_total_gb'],
                    metrics['network_bytes_sent'],
                    metrics['network_bytes_recv']
                )
                batch_data.append(row)

            # Execute bulk insert
            cursor.executemany(insert_query, batch_data)
            self.db_connection.commit()

            batch_size = len(self.batch)
            self.total_inserted += batch_size

            logger.info(f"Inserted {batch_size} records to database "
                       f"(Total: {self.total_inserted})")

            # Clear batch
            self.batch = []
            self.last_insert_time = time.time()

            cursor.close()

        except pyodbc.Error as e:
            self.errors += 1
            logger.error(f"Database insert failed: {e}")
            self.db_connection.rollback()

            # Clear batch to avoid reprocessing bad data
            self.batch = []

    def run(self):
        """Main loop: consume messages and write to database"""
        logger.info(f"Starting metrics consumer (Group: {KAFKA_CONSUMER_GROUP})")
        logger.info(f"Batch size: {BATCH_SIZE}, Timeout: {BATCH_TIMEOUT_SECONDS}s")
        logger.info(f"Press Ctrl+C to stop\n")

        try:
            for message in self.consumer:
                try:
                    # Extract metrics from message
                    metrics = message.value

                    logger.debug(
                        f"Received metrics from {metrics['hostname']} "
                        f"at {metrics['timestamp']}"
                    )

                    # Add to batch
                    self.add_to_batch(metrics)

                    # Check if we should flush the batch
                    if self.should_flush_batch():
                        self.flush_batch()

                        # Commit Kafka offset after successful database insert
                        self.consumer.commit()
                        logger.debug("Kafka offset committed")

                except Exception as e:
                    self.errors += 1
                    logger.error(f"Error processing message: {e}")
                    continue

        except KeyboardInterrupt:
            logger.info("\nShutting down consumer...")

            # Flush any remaining messages
            self.flush_batch()
            self.consumer.commit()

            self.shutdown()

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            self.shutdown()
            raise

    def shutdown(self):
        """Clean shutdown"""
        logger.info(f"Total records inserted: {self.total_inserted}")
        logger.info(f"Total errors: {self.errors}")

        if self.consumer:
            self.consumer.close()
            logger.info("Consumer closed")

        if self.db_connection:
            self.db_connection.close()
            logger.info("Database connection closed")


def main():
    """Main entry point"""
    consumer = MetricsConsumer()
    consumer.run()


if __name__ == "__main__":
    main()
```

### Step 5: Dependencies

Create `requirements.txt`:

```txt
kafka-python==2.0.2
psutil==5.9.6
pyodbc==5.0.1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Step 6: Running the Pipeline

**Terminal 1: Start the Producer (Metrics Collector)**

```bash
python metrics_collector.py
```

Output:

```
2024-11-12 10:30:00 - INFO - Starting metrics collection for web-server-01
2024-11-12 10:30:00 - INFO - Sending metrics every 5 seconds
2024-11-12 10:30:01 - INFO - Collected: CPU=45.2%, Memory=67.8%, Disk=42.1%
2024-11-12 10:30:01 - INFO - Sent metrics for web-server-01 to partition 0, offset 0
```

**Terminal 2: Start the Consumer (Database Writer)**

```bash
python metrics_consumer.py
```

Output:

```
2024-11-12 10:30:05 - INFO - Starting metrics consumer (Group: metrics-to-database)
2024-11-12 10:30:05 - INFO - Batch size: 100, Timeout: 30s
2024-11-12 10:30:35 - INFO - Inserted 6 records to database (Total: 6)
```

**Terminal 3: Query the Database**

```bash
# Connect to SQL Server
docker exec -it mssql1 /opt/mssql-tools18/bin/sqlcmd \
    -S localhost -U SA -P "YourStrong@Password" -C

# Query recent metrics
SELECT TOP 10
    hostname,
    timestamp,
    cpu_percent,
    memory_percent,
    disk_percent
FROM server_metrics
ORDER BY timestamp DESC;
GO
```

### Step 7: Monitoring Your Pipeline

**Check Kafka Topics:**

```bash
# List topics
docker exec -it kafka-kafka-1 kafka-topics --bootstrap-server localhost:9092 --list

# Describe topic
docker exec -it kafka-kafka-1 kafka-topics \
    --bootstrap-server localhost:9092 \
    --describe --topic server-metrics
```

**Check Consumer Group:**

```bash
# Check consumer lag
docker exec -it kafka-kafka-1 kafka-consumer-groups \
    --bootstrap-server localhost:9092 \
    --describe --group metrics-to-database
```

Output:

```
GROUP               TOPIC           PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG
metrics-to-database server-metrics  0          1250            1250            0
```

**LAG = 0** means consumer is caught up (good!)
**LAG > 0** means consumer is falling behind

---

## Best Practices for Developers

### 1. Error Handling

**Always handle errors gracefully:**

```python
from kafka.errors import KafkaError, KafkaTimeoutError
import logging

def send_with_error_handling(producer, topic, message):
    """Send message with proper error handling"""
    try:
        future = producer.send(topic, message)
        record_metadata = future.get(timeout=10)
        logging.info(f"Message sent successfully to partition {record_metadata.partition}")
        return True

    except KafkaTimeoutError:
        logging.error("Timeout while sending message")
        # Consider: Add to retry queue or dead letter queue
        return False

    except KafkaError as e:
        logging.error(f"Kafka error: {e}")
        # Consider: Alert monitoring system
        return False

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return False
```

### 2. Graceful Shutdown

**Always clean up resources:**

```python
import signal
import sys

class GracefulShutdown:
    """Handle graceful shutdown on signals"""

    def __init__(self, producer, consumer):
        self.producer = producer
        self.consumer = consumer
        self.shutdown_requested = False

        # Register signal handlers
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)

    def handle_signal(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\nReceived signal {signum}, shutting down gracefully...")
        self.shutdown_requested = True

        # Flush producer
        if self.producer:
            self.producer.flush()
            self.producer.close()

        # Commit consumer offsets
        if self.consumer:
            self.consumer.commit()
            self.consumer.close()

        sys.exit(0)
```

### 3. Configuration Management

**Use environment variables for configuration:**

```python
import os

class Config:
    """Application configuration"""

    # Kafka configuration
    KAFKA_BOOTSTRAP_SERVERS = os.getenv(
        'KAFKA_BOOTSTRAP_SERVERS',
        'localhost:9092'
    ).split(',')

    KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'server-metrics')

    # Database configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '1433')
    DB_NAME = os.getenv('DB_NAME', 'monitoring')
    DB_USER = os.getenv('DB_USER', 'sa')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')

    # Application configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', '100'))

# Usage
config = Config()
producer = KafkaProducer(bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS)
```

### 4. Logging Best Practices

**Use structured logging:**

```python
import logging
import json

class JsonFormatter(logging.Formatter):
    """Format logs as JSON for better parsing"""

    def format(self, record):
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_data)

# Configure logging
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

### 5. Message Serialization

**Use appropriate serializers:**

```python
from kafka import KafkaProducer
import json
import pickle
import avro.io
import io

# Option 1: JSON (human-readable, widely compatible)
json_producer = KafkaProducer(
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Option 2: String (simple text messages)
string_producer = KafkaProducer(
    value_serializer=lambda v: v.encode('utf-8')
)

# Option 3: Binary/Pickle (Python objects, not recommended for production)
pickle_producer = KafkaProducer(
    value_serializer=lambda v: pickle.dumps(v)
)

# Option 4: Avro (schema-based, efficient, best for production)
def avro_serializer(schema):
    """Create Avro serializer"""
    def serialize(value):
        writer = avro.io.DatumWriter(schema)
        bytes_writer = io.BytesIO()
        encoder = avro.io.BinaryEncoder(bytes_writer)
        writer.write(value, encoder)
        return bytes_writer.getvalue()
    return serialize
```

**Recommendation**: Use JSON for development, Avro for production

### 6. Partitioning Strategy

**Choose keys wisely:**

```python
# Good: Use entity ID as key for ordering
producer.send(
    'user-events',
    key=user_id.encode('utf-8'),  # All events for user go to same partition
    value=event_data
)

# Good: Use composite key for distribution
composite_key = f"{user_id}:{shard_id}".encode('utf-8')
producer.send('events', key=composite_key, value=data)

# Bad: Using timestamp as key (hot partitions)
producer.send('events', key=str(timestamp).encode('utf-8'), value=data)

# Bad: Random key (defeats ordering purpose)
producer.send('events', key=str(random.random()).encode('utf-8'), value=data)
```

### 7. Consumer Offset Management

**Manual commit for reliability:**

```python
consumer = KafkaConsumer(
    'my-topic',
    enable_auto_commit=False  # Manual control
)

for message in consumer:
    try:
        # Process message
        process_message(message)

        # Save to database
        save_to_database(message)

        # Commit only after successful processing
        consumer.commit()

    except Exception as e:
        logging.error(f"Processing failed: {e}")
        # Don't commit - message will be reprocessed
        continue
```

### 8. Idempotent Processing

**Design consumers to handle duplicate messages:**

```python
def process_message_idempotent(message):
    """Process message idempotently"""

    # Option 1: Check if already processed
    if is_already_processed(message.key):
        logging.info(f"Message {message.key} already processed, skipping")
        return

    # Process message
    result = do_processing(message)

    # Store with unique constraint or check
    save_with_deduplication(message.key, result)

# Database: Use unique constraints
# CREATE UNIQUE INDEX idx_message_id ON processed_messages(message_id);

def save_with_deduplication(message_id, data):
    """Save with duplicate detection"""
    try:
        cursor.execute(
            "INSERT INTO processed_messages (message_id, data) VALUES (?, ?)",
            (message_id, data)
        )
        connection.commit()
    except IntegrityError:
        # Duplicate - already processed
        logging.info(f"Duplicate message {message_id} detected")
```

### 9. Monitoring and Metrics

**Track application metrics:**

```python
from collections import defaultdict
import time

class MetricsTracker:
    """Track application metrics"""

    def __init__(self):
        self.messages_sent = 0
        self.messages_received = 0
        self.errors = 0
        self.latencies = []
        self.start_time = time.time()

    def record_send(self, latency_ms):
        """Record message sent"""
        self.messages_sent += 1
        self.latencies.append(latency_ms)

    def record_receive(self):
        """Record message received"""
        self.messages_received += 1

    def record_error(self):
        """Record error"""
        self.errors += 1

    def get_stats(self):
        """Get statistics"""
        uptime = time.time() - self.start_time
        avg_latency = sum(self.latencies) / len(self.latencies) if self.latencies else 0

        return {
            'uptime_seconds': uptime,
            'messages_sent': self.messages_sent,
            'messages_received': self.messages_received,
            'errors': self.errors,
            'send_rate': self.messages_sent / uptime,
            'receive_rate': self.messages_received / uptime,
            'avg_latency_ms': avg_latency,
            'error_rate': self.errors / max(self.messages_sent, 1)
        }

# Usage
metrics = MetricsTracker()

# In producer
start = time.time()
producer.send('topic', message)
latency = (time.time() - start) * 1000
metrics.record_send(latency)

# Periodic stats logging
def log_stats():
    stats = metrics.get_stats()
    logging.info(f"Stats: {stats}")
```

### 10. Testing Kafka Applications

**Use embedded Kafka for testing:**

```python
import unittest
from kafka import KafkaProducer, KafkaConsumer
import time

class TestKafkaApplication(unittest.TestCase):
    """Test Kafka application"""

    @classmethod
    def setUpClass(cls):
        """Setup test environment"""
        # In production tests, use testcontainers-python
        # or Docker Compose with test configuration
        cls.bootstrap_servers = ['localhost:9092']
        cls.test_topic = 'test-topic-' + str(int(time.time()))

    def test_send_and_receive(self):
        """Test sending and receiving messages"""
        # Create producer
        producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: v.encode('utf-8')
        )

        # Send message
        test_message = "Hello Kafka Test"
        producer.send(self.test_topic, test_message)
        producer.flush()
        producer.close()

        # Create consumer
        consumer = KafkaConsumer(
            self.test_topic,
            bootstrap_servers=self.bootstrap_servers,
            auto_offset_reset='earliest',
            value_deserializer=lambda m: m.decode('utf-8'),
            consumer_timeout_ms=5000  # Timeout after 5 seconds
        )

        # Receive message
        messages = []
        for message in consumer:
            messages.append(message.value)
            break  # Get first message only

        consumer.close()

        # Assert
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0], test_message)

    def test_batch_processing(self):
        """Test batch processing"""
        # Send multiple messages
        producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers)

        for i in range(10):
            producer.send(self.test_topic, f"Message {i}".encode('utf-8'))

        producer.flush()
        producer.close()

        # Consume and count
        consumer = KafkaConsumer(
            self.test_topic,
            bootstrap_servers=self.bootstrap_servers,
            auto_offset_reset='earliest',
            consumer_timeout_ms=5000
        )

        count = sum(1 for _ in consumer)
        consumer.close()

        self.assertGreaterEqual(count, 10)

if __name__ == '__main__':
    unittest.main()
```

---

## Common Pitfalls and How to Avoid Them

### Pitfall 1: Not Closing Producers/Consumers

**Problem:**

```python
# Bad - connection leak
def send_message():
    producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
    producer.send('topic', b'message')
    # Producer not closed - connection leak!
```

**Solution:**

```python
# Good - use context manager or try/finally
def send_message():
    producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
    try:
        producer.send('topic', b'message')
        producer.flush()
    finally:
        producer.close()

# Better - reuse producer
class MessageSender:
    def __init__(self):
        self.producer = KafkaProducer(bootstrap_servers=['localhost:9092'])

    def send(self, topic, message):
        self.producer.send(topic, message)

    def close(self):
        self.producer.close()
```

### Pitfall 2: Ignoring Serialization Errors

**Problem:**

```python
# Bad - will crash on non-JSON-serializable data
producer = KafkaProducer(
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# This will fail with datetime objects
producer.send('topic', {'timestamp': datetime.now()})
```

**Solution:**

```python
# Good - custom JSON encoder
import json
from datetime import datetime

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

producer = KafkaProducer(
    value_serializer=lambda v: json.dumps(v, cls=DateTimeEncoder).encode('utf-8')
)

# Now this works
producer.send('topic', {'timestamp': datetime.now()})
```

### Pitfall 3: Not Handling Rebalances

**Problem:**

```python
# Bad - state lost during rebalance
current_batch = []

for message in consumer:
    current_batch.append(message)
    if len(current_batch) >= 100:
        process_batch(current_batch)
        current_batch = []
    # If rebalance happens, current_batch is lost!
```

**Solution:**

```python
# Good - use rebalance listeners
from kafka import TopicPartition

def on_revoke(consumer, partitions):
    """Called before rebalance"""
    print(f"Rebalance: losing partitions {partitions}")
    # Flush any pending work
    process_batch(current_batch)
    current_batch.clear()
    # Commit offsets
    consumer.commit()

def on_assign(consumer, partitions):
    """Called after rebalance"""
    print(f"Rebalance: assigned partitions {partitions}")
    # Reset state for new partitions

consumer = KafkaConsumer(
    'topic',
    on_revoke=on_revoke,
    on_assign=on_assign
)
```

### Pitfall 4: Wrong Offset Reset Strategy

**Problem:**

```python
# Bad - may miss messages in production
consumer = KafkaConsumer(
    'critical-orders',
    auto_offset_reset='latest'  # Skips all existing messages!
)
```

**Solution:**

```python
# Good - explicit strategy based on use case
consumer = KafkaConsumer(
    'critical-orders',
    auto_offset_reset='earliest',  # Process all messages from start
    group_id='order-processor'  # Will remember position
)

# Or for truly new consumers only
consumer = KafkaConsumer(
    'real-time-only',
    auto_offset_reset='latest',  # Only new messages
    group_id='real-time-monitor'
)
```

### Pitfall 5: Not Monitoring Consumer Lag

**Problem:** Consumer falls behind without anyone noticing until it's too late.

**Solution:**

```python
# Monitor lag programmatically
def check_consumer_lag(consumer):
    """Check consumer lag"""
    partitions = consumer.assignment()

    for partition in partitions:
        # Get current position
        current_offset = consumer.position(partition)

        # Get end offset (latest)
        end_offsets = consumer.end_offsets([partition])
        end_offset = end_offsets[partition]

        # Calculate lag
        lag = end_offset - current_offset

        if lag > 1000:  # Threshold
            logging.warning(
                f"High lag detected: {lag} messages behind "
                f"on partition {partition.partition}"
            )
            # Alert monitoring system
            send_alert(f"Consumer lag: {lag}")

# Check lag periodically
import threading

def monitor_lag():
    while True:
        check_consumer_lag(consumer)
        time.sleep(60)  # Check every minute

monitor_thread = threading.Thread(target=monitor_lag, daemon=True)
monitor_thread.start()
```

### Pitfall 6: Hardcoding Configuration

**Problem:**

```python
# Bad - hardcoded values
producer = KafkaProducer(
    bootstrap_servers=['kafka-prod-1:9092'],
    api_version=(2, 0, 2)
)
```

**Solution:**

```python
# Good - use configuration file
import yaml

with open('config.yaml') as f:
    config = yaml.safe_load(f)

producer = KafkaProducer(
    bootstrap_servers=config['kafka']['bootstrap_servers'],
    api_version=tuple(config['kafka']['api_version'])
)
```

---

## Testing Kafka Applications

### Unit Testing with Mock

```python
import unittest
from unittest.mock import Mock, patch, MagicMock
from metrics_collector import MetricsCollector

class TestMetricsCollector(unittest.TestCase):
    """Unit tests for MetricsCollector"""

    @patch('metrics_collector.KafkaProducer')
    def test_send_metrics(self, mock_producer_class):
        """Test sending metrics"""
        # Setup mock
        mock_producer = Mock()
        mock_producer_class.return_value = mock_producer

        mock_future = Mock()
        mock_future.get.return_value = Mock(partition=0, offset=100)
        mock_producer.send.return_value = mock_future

        # Create collector
        collector = MetricsCollector()

        # Test
        metrics = {
            'hostname': 'test-server',
            'cpu_percent': 50.0
        }
        result = collector.send_metrics(metrics)

        # Assertions
        self.assertTrue(result)
        mock_producer.send.assert_called_once()
        self.assertEqual(collector.metrics_sent, 1)
```

### Integration Testing with Test Container

```python
import unittest
from testcontainers.kafka import KafkaContainer
from kafka import KafkaProducer, KafkaConsumer

class TestKafkaIntegration(unittest.TestCase):
    """Integration tests with real Kafka"""

    @classmethod
    def setUpClass(cls):
        """Start Kafka container"""
        cls.kafka = KafkaContainer()
        cls.kafka.start()
        cls.bootstrap_servers = cls.kafka.get_bootstrap_server()

    @classmethod
    def tearDownClass(cls):
        """Stop Kafka container"""
        cls.kafka.stop()

    def test_end_to_end(self):
        """Test end-to-end message flow"""
        topic = 'test-topic'

        # Producer
        producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: v.encode('utf-8')
        )
        producer.send(topic, 'test message')
        producer.flush()
        producer.close()

        # Consumer
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=self.bootstrap_servers,
            auto_offset_reset='earliest',
            consumer_timeout_ms=5000
        )

        messages = [msg.value.decode('utf-8') for msg in consumer]
        consumer.close()

        self.assertIn('test message', messages)
```

---

## Deployment and Production Readiness

### Docker Deployment

Create `Dockerfile` for your application:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Environment variables
ENV KAFKA_BOOTSTRAP_SERVERS=kafka:9092
ENV KAFKA_TOPIC=server-metrics

# Run application
CMD ["python", "metrics_collector.py"]
```

Create `docker-compose.yml` for full stack:

```yaml
version: '3.8'

services:
  # Metrics Collector (Producer)
  metrics-collector:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
      - KAFKA_TOPIC=server-metrics
      - COLLECTION_INTERVAL_SECONDS=5
    depends_on:
      - kafka
    restart: unless-stopped

  # Database Writer (Consumer)
  metrics-consumer:
    build:
      context: .
      dockerfile: Dockerfile
    command: python metrics_consumer.py
    environment:
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
      - KAFKA_TOPIC=server-metrics
      - SQL_SERVER=sqlserver:1433
      - SQL_DATABASE=monitoring
    depends_on:
      - kafka
      - sqlserver
    restart: unless-stopped

  # Kafka (from existing docker-compose.yml)
  kafka:
    image: confluentinc/cp-kafka:7.6.0
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092

  zookeeper:
    image: confluentinc/cp-zookeeper:7.6.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181

  # SQL Server
  sqlserver:
    image: mcr.microsoft.com/mssql/server:2022-latest
    environment:
      - ACCEPT_EULA=Y
      - SA_PASSWORD=YourStrong@Password
    ports:
      - "1433:1433"
```

### Health Checks

Add health check endpoints:

```python
from flask import Flask, jsonify
import threading

app = Flask(__name__)

class HealthCheck:
    """Health check for monitoring"""

    def __init__(self):
        self.healthy = True
        self.last_success = time.time()
        self.error_count = 0

    def record_success(self):
        self.healthy = True
        self.last_success = time.time()
        self.error_count = 0

    def record_failure(self):
        self.error_count += 1
        if self.error_count > 5:
            self.healthy = False

    def is_healthy(self):
        # Unhealthy if no success in 60 seconds
        if time.time() - self.last_success > 60:
            return False
        return self.healthy

health = HealthCheck()

@app.route('/health')
def health_check():
    """Health check endpoint"""
    if health.is_healthy():
        return jsonify({'status': 'healthy'}), 200
    else:
        return jsonify({'status': 'unhealthy'}), 503

@app.route('/metrics')
def metrics():
    """Metrics endpoint for Prometheus"""
    stats = metrics_tracker.get_stats()
    # Return Prometheus format
    return f"""
# HELP messages_sent Total messages sent
# TYPE messages_sent counter
messages_sent {stats['messages_sent']}

# HELP messages_received Total messages received
# TYPE messages_received counter
messages_received {stats['messages_received']}

# HELP errors_total Total errors
# TYPE errors_total counter
errors_total {stats['errors']}
    """, 200, {'Content-Type': 'text/plain'}

# Run Flask in background thread
def run_health_server():
    app.run(host='0.0.0.0', port=8080)

health_thread = threading.Thread(target=run_health_server, daemon=True)
health_thread.start()
```

### Production Checklist

- [ ] **Configuration**: All values from environment variables
- [ ] **Logging**: Structured logging (JSON) with appropriate levels
- [ ] **Error Handling**: All exceptions caught and logged
- [ ] **Graceful Shutdown**: SIGTERM/SIGINT handlers implemented
- [ ] **Health Checks**: HTTP endpoints for liveness/readiness
- [ ] **Metrics**: Expose application metrics (Prometheus format)
- [ ] **Monitoring**: Consumer lag alerts configured
- [ ] **Testing**: Unit tests, integration tests passing
- [ ] **Documentation**: README with setup/deployment instructions
- [ ] **Security**: No hardcoded credentials, SSL/TLS enabled
- [ ] **Resource Limits**: Memory/CPU limits set in Docker
- [ ] **Retry Logic**: Exponential backoff for failures
- [ ] **Idempotency**: Consumer can handle duplicate messages
- [ ] **Backpressure**: Producer handles slow consumers

---

## Summary

This guide covered:

1. **Kafka Basics**: What it is and when to use it
2. **Core Concepts**: Topics, partitions, producers, consumers, offsets
3. **Development Environment**: Docker setup and Python client
4. **First Application**: Simple producer and consumer
5. **Real-World Project**: Complete metrics pipeline with SQL Server
6. **Best Practices**: Error handling, configuration, monitoring
7. **Common Pitfalls**: What to avoid and how
8. **Testing**: Unit and integration testing strategies
9. **Production Deployment**: Docker, health checks, monitoring

### Next Steps

1. **Experiment**: Modify the metrics collector to track different data
2. **Scale**: Add more partitions and consumers
3. **Monitor**: Set up Prometheus and Grafana dashboards
4. **Secure**: Enable SSL/TLS and SASL authentication
5. **Advanced**: Explore Kafka Streams for real-time processing

### Additional Resources

- **Apache Kafka Documentation**: <https://kafka.apache.org/documentation/>
- **kafka-python Documentation**: <https://kafka-python.readthedocs.io/>
- **Confluent Developer Guides**: <https://developer.confluent.io/>
- **This Repository**: Check other files in `docker/kafka/` for more examples

---

*Happy Streaming! 🚀*

**Last Updated**: November 2025
