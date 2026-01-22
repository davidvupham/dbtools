# Lesson 09: Kafka Connect

**[← Back to Module 3](./README.md)** | **[Next: Schema Registry →](./10_schema_registry.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Kafka_Connect-blue)

## Overview

Kafka Connect is a framework for streaming data between Kafka and external systems. This lesson covers Connect architecture, connectors, and how to build reliable data pipelines.

**Learning objectives:**
- Understand Kafka Connect architecture and concepts
- Deploy source and sink connectors
- Configure connectors for reliability and performance
- Implement CDC (Change Data Capture) pipelines

**Prerequisites:** Module 2 completed

**Estimated time:** 60 minutes

---

## Table of contents

- [What is Kafka Connect](#what-is-kafka-connect)
- [Architecture](#architecture)
- [Connectors](#connectors)
- [Deploying connectors](#deploying-connectors)
- [Configuration deep dive](#configuration-deep-dive)
- [CDC with Debezium](#cdc-with-debezium)
- [Monitoring and operations](#monitoring-and-operations)
- [Hands-on exercises](#hands-on-exercises)
- [Key takeaways](#key-takeaways)

---

## What is Kafka Connect

### The integration problem

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    THE INTEGRATION CHALLENGE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  WITHOUT KAFKA CONNECT (Spaghetti Architecture):                            │
│                                                                             │
│     Database A ──┐          ┌── Database B                                  │
│     Database C ──┼── APP ───┼── S3                                          │
│     API X      ──┤    1     ├── Elasticsearch                               │
│     API Y      ──┘          └── Data Warehouse                              │
│                                                                             │
│     Database A ──┐          ┌── Database B                                  │
│     Database C ──┼── APP ───┼── S3                                          │
│     API X      ──┤    2     ├── Elasticsearch                               │
│     API Y      ──┘          └── Data Warehouse                              │
│                                                                             │
│     (Every app writes custom integration code)                              │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  WITH KAFKA CONNECT (Hub and Spoke):                                        │
│                                                                             │
│     Database A ─┐                           ┌─ Database B                   │
│     Database C ─┼─► SOURCE ──► KAFKA ──► SINK ─┼─ S3                        │
│     API X      ─┤  CONNECTORS    │    CONNECTORS ├─ Elasticsearch           │
│     API Y      ─┘                │               └─ Data Warehouse          │
│                                  │                                          │
│                            (Single pipeline)                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key benefits

| Benefit | Description |
|---------|-------------|
| **No code required** | Declarative JSON configuration |
| **Scalable** | Distributed across worker nodes |
| **Fault tolerant** | Automatic task redistribution |
| **Exactly-once** | Supports exactly-once semantics |
| **Ecosystem** | 200+ pre-built connectors available |

---

## Architecture

### Connect workers and tasks

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    KAFKA CONNECT ARCHITECTURE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  CONNECT CLUSTER (3 Workers)                                                │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                                                                     │    │
│  │  Worker 1              Worker 2              Worker 3               │    │
│  │  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐        │    │
│  │  │ Task A-1     │     │ Task A-2     │     │ Task B-1     │        │    │
│  │  │ Task A-3     │     │ Task B-2     │     │ Task C-1     │        │    │
│  │  └──────────────┘     └──────────────┘     └──────────────┘        │    │
│  │                                                                     │    │
│  │  REST API :8083        REST API :8083       REST API :8083          │    │
│  │                                                                     │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                           │                                                 │
│                           ▼                                                 │
│           ┌─────────────────────────────────────┐                          │
│           │            KAFKA CLUSTER             │                          │
│           │  ┌──────────────────────────────┐   │                          │
│           │  │ connect-configs (offsets,    │   │                          │
│           │  │ status, connector configs)   │   │                          │
│           │  └──────────────────────────────┘   │                          │
│           │  ┌──────────────────────────────┐   │                          │
│           │  │ Your data topics             │   │                          │
│           │  └──────────────────────────────┘   │                          │
│           └─────────────────────────────────────┘                          │
│                                                                             │
│  TERMINOLOGY:                                                               │
│  • Worker: JVM process running Connect framework                            │
│  • Connector: Logical job (e.g., "read from PostgreSQL")                    │
│  • Task: Unit of work (parallelism unit)                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Standalone vs distributed mode

| Mode | Use Case | High Availability |
|------|----------|-------------------|
| **Standalone** | Development, testing | No |
| **Distributed** | Production | Yes |

```bash
# Standalone mode (single worker)
connect-standalone.sh connect-standalone.properties connector.properties

# Distributed mode (cluster of workers)
connect-distributed.sh connect-distributed.properties
# Connectors configured via REST API
```

---

## Connectors

### Types of connectors

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SOURCE vs SINK CONNECTORS                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  SOURCE CONNECTORS                    SINK CONNECTORS                       │
│  ──────────────────                   ───────────────                       │
│  External → Kafka                     Kafka → External                      │
│                                                                             │
│  ┌───────────┐      ┌──────┐         ┌──────┐      ┌───────────┐          │
│  │ Database  │─────►│      │         │      │─────►│ Database  │          │
│  └───────────┘      │      │         │      │      └───────────┘          │
│  ┌───────────┐      │      │         │      │      ┌───────────┐          │
│  │   Files   │─────►│KAFKA │         │KAFKA │─────►│    S3     │          │
│  └───────────┘      │      │         │      │      └───────────┘          │
│  ┌───────────┐      │      │         │      │      ┌───────────┐          │
│  │   APIs    │─────►│      │         │      │─────►│  Elastic  │          │
│  └───────────┘      └──────┘         └──────┘      └───────────┘          │
│                                                                             │
│  Examples:                            Examples:                             │
│  • JDBC Source                        • JDBC Sink                           │
│  • Debezium (CDC)                     • Elasticsearch Sink                  │
│  • File Source                        • S3 Sink                             │
│  • HTTP Source                        • BigQuery Sink                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Popular connectors

| Category | Connector | Description |
|----------|-----------|-------------|
| **Databases** | JDBC Source/Sink | Poll-based database sync |
| **Databases** | Debezium | CDC for MySQL, PostgreSQL, MongoDB |
| **Cloud Storage** | S3 Sink | Stream to AWS S3 |
| **Search** | Elasticsearch Sink | Index to Elasticsearch |
| **Data Warehouse** | BigQuery Sink | Load to Google BigQuery |
| **Messaging** | JMS Source/Sink | ActiveMQ, IBM MQ |
| **Files** | FileStream | Read/write local files |

---

## Deploying connectors

### REST API operations

```bash
# List installed connector plugins
curl http://localhost:8083/connector-plugins | jq

# List running connectors
curl http://localhost:8083/connectors

# Get connector configuration
curl http://localhost:8083/connectors/my-connector/config | jq

# Get connector status
curl http://localhost:8083/connectors/my-connector/status | jq

# Create a new connector
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  -d @connector-config.json

# Update connector configuration
curl -X PUT http://localhost:8083/connectors/my-connector/config \
  -H "Content-Type: application/json" \
  -d @new-config.json

# Pause connector
curl -X PUT http://localhost:8083/connectors/my-connector/pause

# Resume connector
curl -X PUT http://localhost:8083/connectors/my-connector/resume

# Restart connector
curl -X POST http://localhost:8083/connectors/my-connector/restart

# Delete connector
curl -X DELETE http://localhost:8083/connectors/my-connector
```

### Example: JDBC source connector

```json
{
  "name": "postgres-source",
  "config": {
    "connector.class": "io.confluent.connect.jdbc.JdbcSourceConnector",
    "connection.url": "jdbc:postgresql://postgres:5432/mydb",
    "connection.user": "postgres",
    "connection.password": "postgres",
    "table.whitelist": "customers,orders",
    "mode": "incrementing",
    "incrementing.column.name": "id",
    "topic.prefix": "db-",
    "poll.interval.ms": "1000",
    "tasks.max": "2"
  }
}
```

### Example: Elasticsearch sink connector

```json
{
  "name": "elasticsearch-sink",
  "config": {
    "connector.class": "io.confluent.connect.elasticsearch.ElasticsearchSinkConnector",
    "connection.url": "http://elasticsearch:9200",
    "topics": "orders,customers",
    "type.name": "_doc",
    "key.ignore": "false",
    "schema.ignore": "true",
    "tasks.max": "2"
  }
}
```

---

## Configuration deep dive

### Common configuration options

| Setting | Description | Default |
|---------|-------------|---------|
| `connector.class` | Connector implementation class | Required |
| `tasks.max` | Maximum parallel tasks | 1 |
| `topics` | Topics to consume (sink) | Required for sink |
| `errors.tolerance` | Error handling mode | none |
| `errors.deadletterqueue.topic.name` | DLQ topic | - |

### Error handling strategies

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ERROR HANDLING OPTIONS                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  errors.tolerance: none (default)                                           │
│  ─────────────────────────────────                                          │
│  First error → Task fails → Connector stops                                 │
│  Use for: Critical data where any error is unacceptable                     │
│                                                                             │
│  errors.tolerance: all                                                      │
│  ─────────────────────                                                      │
│  Errors logged → Processing continues → Bad records skipped                 │
│  Use for: Tolerating occasional bad records                                 │
│                                                                             │
│  errors.tolerance: all + DLQ                                                │
│  ───────────────────────────                                                │
│  Bad records → Written to dead letter queue → Processing continues          │
│  Use for: Production systems needing to handle bad data                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Dead letter queue configuration

```json
{
  "name": "orders-sink",
  "config": {
    "connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
    "connection.url": "jdbc:postgresql://postgres:5432/warehouse",
    "topics": "orders",
    "tasks.max": "2",

    "errors.tolerance": "all",
    "errors.deadletterqueue.topic.name": "orders-dlq",
    "errors.deadletterqueue.topic.replication.factor": "3",
    "errors.deadletterqueue.context.headers.enable": "true",
    "errors.log.enable": "true",
    "errors.log.include.messages": "true"
  }
}
```

### Transforms (Single Message Transforms)

SMTs allow you to modify messages as they flow through Connect:

```json
{
  "name": "orders-source",
  "config": {
    "connector.class": "io.confluent.connect.jdbc.JdbcSourceConnector",
    "connection.url": "jdbc:postgresql://postgres:5432/mydb",
    "table.whitelist": "orders",

    "transforms": "addTimestamp,maskSSN,route",

    "transforms.addTimestamp.type": "org.apache.kafka.connect.transforms.InsertField$Value",
    "transforms.addTimestamp.timestamp.field": "ingested_at",

    "transforms.maskSSN.type": "org.apache.kafka.connect.transforms.MaskField$Value",
    "transforms.maskSSN.fields": "ssn",

    "transforms.route.type": "org.apache.kafka.connect.transforms.RegexRouter",
    "transforms.route.regex": "(.*)",
    "transforms.route.replacement": "prod-$1"
  }
}
```

Common transforms:

| Transform | Purpose |
|-----------|---------|
| `InsertField` | Add fields (timestamp, topic name) |
| `MaskField` | Mask sensitive data |
| `ReplaceField` | Rename or drop fields |
| `ValueToKey` | Extract key from value |
| `RegexRouter` | Route to different topics |
| `TimestampConverter` | Convert timestamp formats |
| `Filter` | Drop messages conditionally |

---

## CDC with Debezium

### What is CDC?

Change Data Capture captures every INSERT, UPDATE, and DELETE from your database and streams them to Kafka.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CHANGE DATA CAPTURE (CDC)                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  DATABASE                                                                   │
│  ┌───────────────────────────────────────────────────────────────────┐     │
│  │  Transaction Log (WAL/Binlog)                                      │     │
│  │                                                                     │     │
│  │  [INSERT id=1] [UPDATE id=1] [DELETE id=2] [INSERT id=3] ...      │     │
│  │        │              │             │             │                │     │
│  └────────┼──────────────┼─────────────┼─────────────┼────────────────┘     │
│           │              │             │             │                      │
│           ▼              ▼             ▼             ▼                      │
│  ┌───────────────────────────────────────────────────────────────────┐     │
│  │                      DEBEZIUM CONNECTOR                            │     │
│  │  (Reads transaction log in near real-time)                         │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│           │              │             │             │                      │
│           ▼              ▼             ▼             ▼                      │
│  ┌───────────────────────────────────────────────────────────────────┐     │
│  │                         KAFKA TOPIC                                │     │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐                      │     │
│  │  │CREATE  │ │UPDATE  │ │DELETE  │ │CREATE  │                      │     │
│  │  │before:n│ │before:v│ │before:v│ │before:n│                      │     │
│  │  │after:v │ │after:v │ │after:n │ │after:v │                      │     │
│  │  └────────┘ └────────┘ └────────┘ └────────┘                      │     │
│  └───────────────────────────────────────────────────────────────────┘     │
│                                                                             │
│  BENEFITS:                                                                  │
│  • Real-time (sub-second latency)                                           │
│  • Complete history (all changes, not just current state)                   │
│  • No polling (efficient, no database load)                                 │
│  • Reliable (based on transaction log)                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Debezium PostgreSQL connector

```json
{
  "name": "postgres-cdc",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "postgres",
    "database.port": "5432",
    "database.user": "postgres",
    "database.password": "postgres",
    "database.dbname": "inventory",
    "database.server.name": "dbserver1",
    "table.include.list": "public.customers,public.orders",
    "plugin.name": "pgoutput",
    "publication.name": "dbz_publication",
    "slot.name": "debezium",
    "tasks.max": "1"
  }
}
```

### Debezium message format

```json
{
  "schema": { ... },
  "payload": {
    "before": {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com"
    },
    "after": {
      "id": 1,
      "name": "John Smith",
      "email": "john.smith@example.com"
    },
    "source": {
      "version": "2.3.0",
      "connector": "postgresql",
      "name": "dbserver1",
      "ts_ms": 1705891200000,
      "db": "inventory",
      "table": "customers",
      "txId": 12345,
      "lsn": 123456789
    },
    "op": "u",
    "ts_ms": 1705891200123,
    "transaction": null
  }
}
```

| Field | Description |
|-------|-------------|
| `before` | Record state before change (null for INSERT) |
| `after` | Record state after change (null for DELETE) |
| `op` | Operation: c=create, u=update, d=delete, r=read (snapshot) |
| `source` | Metadata about the source database |
| `ts_ms` | Timestamp when change occurred |

---

## Monitoring and operations

### Key metrics to monitor

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CONNECT METRICS                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  CONNECTOR STATUS                                                           │
│  ────────────────                                                           │
│  RUNNING    - Connector and all tasks running normally                      │
│  PAUSED     - Connector paused via API                                      │
│  FAILED     - Connector or tasks have failed                                │
│  UNASSIGNED - Tasks not yet assigned to workers                             │
│                                                                             │
│  KEY METRICS                          ALERT THRESHOLD                       │
│  ──────────────────────────────────────────────────────────────────────    │
│                                                                             │
│  connector-status                     != RUNNING                            │
│  task-count                           < expected tasks                      │
│  source-record-poll-rate              Sudden drop                           │
│  sink-record-send-rate                Sudden drop                           │
│  offset-commit-completion-rate        Low rate                              │
│  batch-size-avg                       Too small/large                       │
│  error-total                          > 0                                   │
│  deadletterqueue-produce-requests     > 0 (check DLQ)                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Checking connector health

```bash
# Get connector status
curl -s http://localhost:8083/connectors/my-connector/status | jq

# Response example:
{
  "name": "my-connector",
  "connector": {
    "state": "RUNNING",
    "worker_id": "connect-1:8083"
  },
  "tasks": [
    {
      "id": 0,
      "state": "RUNNING",
      "worker_id": "connect-1:8083"
    },
    {
      "id": 1,
      "state": "FAILED",
      "worker_id": "connect-2:8083",
      "trace": "org.apache.kafka.connect.errors.ConnectException: ..."
    }
  ],
  "type": "source"
}

# Restart failed task
curl -X POST http://localhost:8083/connectors/my-connector/tasks/1/restart
```

### Common issues and solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Task in FAILED state | Various | Check trace, fix root cause, restart |
| No data flowing | Connection issue | Verify source/sink connectivity |
| Consumer lag growing | Slow sink | Increase tasks.max, optimize sink |
| OOM errors | Large messages | Adjust memory, batch size |
| Duplicate data | Task restart | Enable exactly-once, idempotent sinks |

---

## Hands-on exercises

### Exercise 1: Deploy a JDBC source connector

```bash
# Start the Docker environment
cd docker && docker compose up -d kafka kafka-connect postgres

# Wait for Connect to be ready
curl -s http://localhost:8083/connectors

# Create a test table in PostgreSQL
docker exec -it postgres psql -U postgres -c "
CREATE TABLE IF NOT EXISTS products (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100),
  price DECIMAL(10,2),
  created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO products (name, price) VALUES
  ('Laptop', 999.99),
  ('Phone', 599.99),
  ('Tablet', 399.99);
"
```

Create `jdbc-source.json`:
```json
{
  "name": "postgres-products-source",
  "config": {
    "connector.class": "io.confluent.connect.jdbc.JdbcSourceConnector",
    "connection.url": "jdbc:postgresql://postgres:5432/postgres",
    "connection.user": "postgres",
    "connection.password": "postgres",
    "table.whitelist": "products",
    "mode": "incrementing",
    "incrementing.column.name": "id",
    "topic.prefix": "pg-",
    "tasks.max": "1"
  }
}
```

```bash
# Deploy the connector
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  -d @jdbc-source.json

# Check status
curl http://localhost:8083/connectors/postgres-products-source/status | jq

# Consume from the topic
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic pg-products --from-beginning

# Add more data and watch it flow
docker exec -it postgres psql -U postgres -c "
INSERT INTO products (name, price) VALUES ('Headphones', 149.99);
"
```

### Exercise 2: Add a sink connector

Create `elasticsearch-sink.json`:
```json
{
  "name": "products-elasticsearch-sink",
  "config": {
    "connector.class": "io.confluent.connect.elasticsearch.ElasticsearchSinkConnector",
    "connection.url": "http://elasticsearch:9200",
    "topics": "pg-products",
    "type.name": "_doc",
    "key.ignore": "true",
    "schema.ignore": "true",
    "tasks.max": "1"
  }
}
```

### Exercise 3: Configure error handling

Add DLQ configuration to a connector that processes unreliable data.

---

## Key takeaways

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    KAFKA CONNECT KEY TAKEAWAYS                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ✓ Kafka Connect provides scalable, fault-tolerant data integration        │
│                                                                             │
│  ✓ Source connectors import data TO Kafka, Sink connectors export FROM it  │
│                                                                             │
│  ✓ Use distributed mode in production for high availability                │
│                                                                             │
│  ✓ Configure error handling and DLQs for production reliability            │
│                                                                             │
│  ✓ Use Debezium for real-time CDC from databases                           │
│                                                                             │
│  ✓ SMTs can transform messages without custom code                         │
│                                                                             │
│  ✓ Monitor connector status and task health continuously                   │
│                                                                             │
│  ✓ Set tasks.max based on partition count and throughput needs             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

**[← Back to Module 3](./README.md)** | **[Next: Schema Registry →](./10_schema_registry.md)**

[↑ Back to Top](#lesson-09-kafka-connect)
