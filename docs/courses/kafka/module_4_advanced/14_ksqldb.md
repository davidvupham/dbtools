# Lesson 14: ksqlDB

**[← Back to Kafka Streams](./13_kafka_streams.md)** | **[Next: Security →](./15_security.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-ksqlDB-blue)

## Overview

ksqlDB is a streaming database that enables real-time data processing using SQL. It provides the power of Kafka Streams with the simplicity of SQL syntax.

**Learning objectives:**
- Understand ksqlDB architecture and deployment
- Create streams and tables from Kafka topics
- Write streaming queries for real-time processing
- Build materialized views for serving layer

**Prerequisites:** Lesson 13 (Kafka Streams concepts)

**Estimated time:** 50 minutes

---

## Table of contents

- [What is ksqlDB](#what-is-ksqldb)
- [Architecture](#architecture)
- [Getting started](#getting-started)
- [Streams and tables](#streams-and-tables)
- [Queries](#queries)
- [Windowed aggregations](#windowed-aggregations)
- [Joins](#joins)
- [Pull queries](#pull-queries)
- [Connectors](#connectors)
- [Hands-on exercises](#hands-on-exercises)
- [Key takeaways](#key-takeaways)

---

## What is ksqlDB

### SQL for streaming data

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ksqlDB OVERVIEW                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Traditional SQL (Request/Response)                                         │
│  ──────────────────────────────────                                         │
│                                                                             │
│  SELECT * FROM orders WHERE status = 'pending'                              │
│                     │                                                       │
│                     ▼                                                       │
│              ┌──────────────┐                                              │
│              │   Result     │  ← Returns once, query completes             │
│              │   (10 rows)  │                                              │
│              └──────────────┘                                              │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  ksqlDB (Continuous/Push Queries)                                           │
│  ────────────────────────────────                                           │
│                                                                             │
│  SELECT * FROM orders WHERE status = 'pending' EMIT CHANGES;               │
│                     │                                                       │
│                     ▼                                                       │
│              ┌──────────────┐                                              │
│              │   Stream     │  ← Continuously emits new matching rows      │
│              │   Row 1...   │                                              │
│              │   Row 2...   │  (Query runs forever until stopped)          │
│              │   Row 3...   │                                              │
│              └──────────────┘                                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### When to use ksqlDB vs Kafka Streams

| Factor | ksqlDB | Kafka Streams |
|--------|--------|---------------|
| **Language** | SQL | Java/Scala |
| **Deployment** | Separate server | Embedded in app |
| **Learning curve** | Lower | Higher |
| **Flexibility** | Limited to SQL | Full programming |
| **Complex logic** | Harder | Easier |
| **UDFs** | Supported | Native code |
| **Best for** | Analysts, simple pipelines | Developers, complex logic |

---

## Architecture

### ksqlDB cluster

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ksqlDB ARCHITECTURE                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         ksqlDB CLUSTER                               │   │
│  │                                                                      │   │
│  │  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐            │   │
│  │  │  ksqlDB      │   │  ksqlDB      │   │  ksqlDB      │            │   │
│  │  │  Server 1    │   │  Server 2    │   │  Server 3    │            │   │
│  │  │              │   │              │   │              │            │   │
│  │  │ ┌──────────┐ │   │ ┌──────────┐ │   │ ┌──────────┐ │            │   │
│  │  │ │ Query 1  │ │   │ │ Query 1  │ │   │ │ Query 2  │ │            │   │
│  │  │ │ (tasks)  │ │   │ │ (tasks)  │ │   │ │ (tasks)  │ │            │   │
│  │  │ └──────────┘ │   │ └──────────┘ │   │ └──────────┘ │            │   │
│  │  │ ┌──────────┐ │   │              │   │ ┌──────────┐ │            │   │
│  │  │ │ Query 2  │ │   │              │   │ │ Query 3  │ │            │   │
│  │  │ │ (tasks)  │ │   │              │   │ │ (tasks)  │ │            │   │
│  │  │ └──────────┘ │   │              │   │ └──────────┘ │            │   │
│  │  └──────────────┘   └──────────────┘   └──────────────┘            │   │
│  │         │                  │                  │                     │   │
│  │         └──────────────────┼──────────────────┘                     │   │
│  │                            │                                        │   │
│  └────────────────────────────┼────────────────────────────────────────┘   │
│                               │                                             │
│                               ▼                                             │
│                    ┌─────────────────────┐                                 │
│                    │    KAFKA CLUSTER    │                                 │
│                    │                     │                                 │
│                    │  - Input topics     │                                 │
│                    │  - Output topics    │                                 │
│                    │  - Command topic    │                                 │
│                    │  - Processing logs  │                                 │
│                    └─────────────────────┘                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Query types

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ksqlDB QUERY TYPES                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PERSISTENT QUERIES                                                         │
│  ──────────────────                                                         │
│  CREATE STREAM ... AS SELECT ...                                            │
│  CREATE TABLE ... AS SELECT ...                                             │
│                                                                             │
│  • Run continuously until terminated                                        │
│  • Write results to Kafka topics                                            │
│  • Survive server restarts                                                  │
│  • Main workhorse for stream processing                                     │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  PUSH QUERIES                                                               │
│  ────────────                                                               │
│  SELECT ... FROM stream EMIT CHANGES;                                       │
│                                                                             │
│  • Stream results to client                                                 │
│  • Client connection required                                               │
│  • Good for debugging and exploration                                       │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  PULL QUERIES                                                               │
│  ────────────                                                               │
│  SELECT ... FROM table WHERE key = 'value';                                 │
│                                                                             │
│  • Point-in-time lookup                                                     │
│  • Like traditional SQL                                                     │
│  • Requires materialized table                                              │
│  • Great for serving layer                                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Getting started

### Connect to ksqlDB CLI

```bash
# Using Docker
docker exec -it ksqldb-cli ksql http://ksqldb-server:8088

# Or connect to remote server
ksql http://localhost:8088
```

### Basic commands

```sql
-- Show ksqlDB server info
SHOW PROPERTIES;

-- List topics
SHOW TOPICS;

-- List streams
SHOW STREAMS;

-- List tables
SHOW TABLES;

-- List queries
SHOW QUERIES;

-- Describe a stream/table
DESCRIBE orders;
DESCRIBE EXTENDED orders;

-- Terminate a query
TERMINATE query_id;

-- Drop a stream/table
DROP STREAM orders;
DROP TABLE customers;
```

---

## Streams and tables

### Creating a stream

```sql
-- Create stream from existing topic (schema inference)
CREATE STREAM orders (
    order_id VARCHAR KEY,
    customer_id VARCHAR,
    product_id VARCHAR,
    quantity INT,
    price DECIMAL(10,2),
    order_time TIMESTAMP
) WITH (
    KAFKA_TOPIC = 'orders',
    VALUE_FORMAT = 'JSON',
    TIMESTAMP = 'order_time'
);

-- With Avro (schema from Schema Registry)
CREATE STREAM orders_avro
WITH (
    KAFKA_TOPIC = 'orders-avro',
    VALUE_FORMAT = 'AVRO'
);

-- Create stream from another stream
CREATE STREAM high_value_orders AS
SELECT *
FROM orders
WHERE price * quantity > 1000
EMIT CHANGES;
```

### Creating a table

```sql
-- Create table from topic (compacted topic recommended)
CREATE TABLE customers (
    customer_id VARCHAR PRIMARY KEY,
    name VARCHAR,
    email VARCHAR,
    created_at TIMESTAMP
) WITH (
    KAFKA_TOPIC = 'customers',
    VALUE_FORMAT = 'JSON'
);

-- Create table from stream aggregation
CREATE TABLE orders_per_customer AS
SELECT
    customer_id,
    COUNT(*) AS order_count,
    SUM(price * quantity) AS total_spent
FROM orders
GROUP BY customer_id
EMIT CHANGES;
```

### Stream vs Table

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STREAM vs TABLE IN ksqlDB                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  STREAM                                                                     │
│  ──────                                                                     │
│  INSERT INTO orders VALUES ('O1', 'C1', 100);                              │
│  INSERT INTO orders VALUES ('O2', 'C1', 200);                              │
│  INSERT INTO orders VALUES ('O3', 'C2', 150);                              │
│                                                                             │
│  SELECT * FROM orders EMIT CHANGES;                                         │
│  → O1, C1, 100  (all events visible)                                       │
│  → O2, C1, 200                                                              │
│  → O3, C2, 150                                                              │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  TABLE                                                                      │
│  ─────                                                                      │
│  INSERT INTO customers VALUES ('C1', 'Alice');                             │
│  INSERT INTO customers VALUES ('C2', 'Bob');                               │
│  INSERT INTO customers VALUES ('C1', 'Alice Smith');  -- Update C1         │
│                                                                             │
│  SELECT * FROM customers;                                                   │
│  → C1, Alice Smith  (only latest per key)                                  │
│  → C2, Bob                                                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Queries

### Basic queries

```sql
-- Select all from stream (push query)
SELECT * FROM orders EMIT CHANGES;

-- Filter
SELECT *
FROM orders
WHERE product_id = 'PROD-001'
EMIT CHANGES;

-- Project specific columns
SELECT order_id, customer_id, price * quantity AS total
FROM orders
EMIT CHANGES;

-- Limit results
SELECT *
FROM orders
EMIT CHANGES
LIMIT 10;
```

### Transformations

```sql
-- String functions
SELECT
    order_id,
    UCASE(customer_id) AS customer_upper,
    CONCAT(product_id, '-', CAST(quantity AS VARCHAR)) AS product_qty
FROM orders
EMIT CHANGES;

-- Date/time functions
SELECT
    order_id,
    order_time,
    TIMESTAMPTOSTRING(order_time, 'yyyy-MM-dd HH:mm:ss') AS formatted_time,
    TIMESTAMPTOSTRING(order_time, 'yyyy-MM-dd') AS order_date
FROM orders
EMIT CHANGES;

-- Conditional logic
SELECT
    order_id,
    price * quantity AS total,
    CASE
        WHEN price * quantity > 1000 THEN 'HIGH'
        WHEN price * quantity > 100 THEN 'MEDIUM'
        ELSE 'LOW'
    END AS value_tier
FROM orders
EMIT CHANGES;

-- Nested fields (JSON/AVRO)
SELECT
    order_id,
    address->city AS city,
    address->zip AS zip_code
FROM orders
EMIT CHANGES;

-- Array operations
SELECT
    order_id,
    items[1]->product_id AS first_item,
    ARRAY_LENGTH(items) AS item_count
FROM orders
EMIT CHANGES;
```

### Persistent queries

```sql
-- Create derived stream
CREATE STREAM orders_enriched AS
SELECT
    o.order_id,
    o.customer_id,
    o.product_id,
    o.quantity,
    o.price,
    o.price * o.quantity AS total,
    CASE
        WHEN o.price * o.quantity > 1000 THEN 'HIGH'
        ELSE 'NORMAL'
    END AS priority
FROM orders o
EMIT CHANGES;

-- The query runs continuously and writes to 'ORDERS_ENRICHED' topic
-- View the query
SHOW QUERIES;

-- Explain the query
EXPLAIN <query_id>;
```

---

## Windowed aggregations

### Tumbling windows

```sql
-- Orders per customer per hour
CREATE TABLE hourly_orders AS
SELECT
    customer_id,
    WINDOWSTART AS window_start,
    WINDOWEND AS window_end,
    COUNT(*) AS order_count,
    SUM(price * quantity) AS total_amount
FROM orders
WINDOW TUMBLING (SIZE 1 HOUR)
GROUP BY customer_id
EMIT CHANGES;
```

### Hopping windows

```sql
-- 5-minute totals, updated every minute
CREATE TABLE sliding_totals AS
SELECT
    product_id,
    WINDOWSTART AS window_start,
    COUNT(*) AS order_count,
    SUM(quantity) AS total_quantity
FROM orders
WINDOW HOPPING (SIZE 5 MINUTES, ADVANCE BY 1 MINUTE)
GROUP BY product_id
EMIT CHANGES;
```

### Session windows

```sql
-- User sessions (30 minute inactivity gap)
CREATE TABLE user_sessions AS
SELECT
    user_id,
    WINDOWSTART AS session_start,
    WINDOWEND AS session_end,
    COUNT(*) AS event_count
FROM user_events
WINDOW SESSION (30 MINUTES)
GROUP BY user_id
EMIT CHANGES;
```

### Window visualization

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    WINDOWED AGGREGATION EXAMPLE                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Input: orders stream                                                       │
│                                                                             │
│  Time:  10:00   10:15   10:30   10:45   11:00   11:15   11:30              │
│          │       │       │       │       │       │       │                 │
│          ▼       ▼       ▼       ▼       ▼       ▼       ▼                 │
│  C1:    $100    $200            $150            $300                        │
│  C2:            $50     $75                     $200    $100                │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  Output: hourly_orders table                                                │
│                                                                             │
│  │ customer │ window_start │ window_end │ count │ total  │                 │
│  ├──────────┼──────────────┼────────────┼───────┼────────┤                 │
│  │ C1       │ 10:00        │ 11:00      │ 3     │ $450   │                 │
│  │ C1       │ 11:00        │ 12:00      │ 1     │ $300   │                 │
│  │ C2       │ 10:00        │ 11:00      │ 2     │ $125   │                 │
│  │ C2       │ 11:00        │ 12:00      │ 2     │ $300   │                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Joins

### Stream-Stream join

```sql
-- Join orders with payments within 1 hour
CREATE STREAM orders_with_payments AS
SELECT
    o.order_id,
    o.customer_id,
    o.price * o.quantity AS order_total,
    p.payment_id,
    p.amount AS payment_amount,
    p.payment_time
FROM orders o
INNER JOIN payments p
    WITHIN 1 HOUR
    ON o.order_id = p.order_id
EMIT CHANGES;
```

### Stream-Table join

```sql
-- Enrich orders with customer data
CREATE STREAM orders_enriched AS
SELECT
    o.order_id,
    o.customer_id,
    c.name AS customer_name,
    c.email AS customer_email,
    o.product_id,
    o.price * o.quantity AS total
FROM orders o
LEFT JOIN customers c
    ON o.customer_id = c.customer_id
EMIT CHANGES;
```

### Table-Table join

```sql
-- Join customer profiles with addresses
CREATE TABLE customers_with_addresses AS
SELECT
    c.customer_id,
    c.name,
    c.email,
    a.street,
    a.city,
    a.zip
FROM customers c
LEFT JOIN addresses a
    ON c.customer_id = a.customer_id
EMIT CHANGES;
```

### Join requirements

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    JOIN REQUIREMENTS                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  JOIN TYPE            LEFT           RIGHT          REQUIREMENTS            │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  Stream-Stream        Stream         Stream         WITHIN clause required  │
│                                                     Co-partitioned or        │
│                                                     repartition occurs       │
│                                                                             │
│  Stream-Table         Stream         Table          Co-partitioned          │
│                                                     Table must have key     │
│                                                                             │
│  Table-Table          Table          Table          Co-partitioned          │
│                                                     Both must have keys     │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  CO-PARTITIONING RULES:                                                     │
│  • Same number of partitions                                                │
│  • Same partitioning key                                                    │
│  • Same partitioner                                                         │
│                                                                             │
│  If not co-partitioned, ksqlDB may automatically repartition               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Pull queries

### Querying materialized views

```sql
-- Create a materialized table
CREATE TABLE customer_summary AS
SELECT
    customer_id,
    COUNT(*) AS order_count,
    SUM(price * quantity) AS total_spent,
    MAX(order_time) AS last_order
FROM orders
GROUP BY customer_id
EMIT CHANGES;

-- Pull query (point lookup)
SELECT * FROM customer_summary WHERE customer_id = 'C123';

-- Pull query with range (if enabled)
SELECT * FROM customer_summary WHERE total_spent > 1000;
```

### REST API for pull queries

```bash
# Query via REST API
curl -X POST http://localhost:8088/query \
  -H "Content-Type: application/vnd.ksql.v1+json" \
  -d '{
    "ksql": "SELECT * FROM customer_summary WHERE customer_id = '\''C123'\'';",
    "streamsProperties": {}
  }'

# Response
{
  "rows": [
    {"customer_id": "C123", "order_count": 5, "total_spent": 499.95}
  ]
}
```

### Pull queries for serving layer

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ksqlDB AS SERVING LAYER                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                         Application                                         │
│                             │                                               │
│                    GET /customer/C123/summary                               │
│                             │                                               │
│                             ▼                                               │
│                    ┌─────────────────┐                                     │
│                    │   API Server    │                                     │
│                    └────────┬────────┘                                     │
│                             │                                               │
│          SELECT * FROM customer_summary WHERE customer_id = 'C123'          │
│                             │                                               │
│                             ▼                                               │
│                    ┌─────────────────┐                                     │
│                    │     ksqlDB      │                                     │
│                    │  (Pull Query)   │                                     │
│                    └────────┬────────┘                                     │
│                             │                                               │
│                    Reads from local                                         │
│                    materialized state                                       │
│                             │                                               │
│                             ▼                                               │
│                    Response: {order_count: 5, total_spent: 499.95}         │
│                                                                             │
│  Benefits:                                                                  │
│  • Real-time aggregated data                                                │
│  • Low latency (<10ms typical)                                              │
│  • No separate database needed                                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Connectors

### Built-in source connectors

```sql
-- Create source connector for PostgreSQL
CREATE SOURCE CONNECTOR postgres_source WITH (
    'connector.class' = 'io.debezium.connector.postgresql.PostgresConnector',
    'database.hostname' = 'postgres',
    'database.port' = '5432',
    'database.user' = 'postgres',
    'database.password' = 'postgres',
    'database.dbname' = 'mydb',
    'database.server.name' = 'dbserver1',
    'table.include.list' = 'public.customers,public.orders',
    'plugin.name' = 'pgoutput'
);

-- List connectors
SHOW CONNECTORS;

-- Describe connector
DESCRIBE CONNECTOR postgres_source;

-- Drop connector
DROP CONNECTOR postgres_source;
```

### Sink connectors

```sql
-- Create sink connector to Elasticsearch
CREATE SINK CONNECTOR es_sink WITH (
    'connector.class' = 'io.confluent.connect.elasticsearch.ElasticsearchSinkConnector',
    'connection.url' = 'http://elasticsearch:9200',
    'topics' = 'orders_enriched',
    'key.ignore' = 'false',
    'type.name' = '_doc'
);
```

---

## Hands-on exercises

### Exercise 1: Create streams and run queries

```sql
-- 1. Create a stream from the orders topic
-- CREATE STREAM orders ...

-- 2. Query to find all orders over $100
-- SELECT ... WHERE ...

-- 3. Create a derived stream with calculated totals
-- CREATE STREAM orders_with_totals AS ...
```

### Exercise 2: Windowed aggregation

```sql
-- Create a table showing orders per product per 5-minute window
-- Hint: Use WINDOW TUMBLING

-- CREATE TABLE product_orders_5min AS ...
```

### Exercise 3: Stream-Table join

```sql
-- 1. Create a customers table
-- 2. Join the orders stream with customers
-- 3. Output should include customer name and email
```

---

## Key takeaways

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ksqlDB KEY TAKEAWAYS                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ✓ ksqlDB enables stream processing with SQL - no Java required            │
│                                                                             │
│  ✓ Streams are for events (append-only), Tables are for state (updates)    │
│                                                                             │
│  ✓ Persistent queries run continuously and write to Kafka topics           │
│                                                                             │
│  ✓ Push queries stream results, Pull queries do point lookups              │
│                                                                             │
│  ✓ Windowed aggregations support tumbling, hopping, and session windows    │
│                                                                             │
│  ✓ Joins require co-partitioned data (or automatic repartitioning)         │
│                                                                             │
│  ✓ Pull queries on materialized tables enable ksqlDB as a serving layer    │
│                                                                             │
│  ✓ Built-in connectors simplify data ingestion and export                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

**[← Back to Kafka Streams](./13_kafka_streams.md)** | **[Next: Security →](./15_security.md)**

[↑ Back to Top](#lesson-14-ksqldb)
