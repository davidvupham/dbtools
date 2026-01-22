# Project 3: Real-Time CDC Data Pipeline

**[← Back to Module 3](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Estimated Time:** 4-6 hours
> **Difficulty:** Intermediate

## Project Overview

In this project, you will build a complete Change Data Capture (CDC) pipeline that streams database changes to Kafka in real-time, transforms the data, and loads it into a data warehouse. This is a common pattern for building real-time analytics and data synchronization systems.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     CDC PIPELINE ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐     ┌───────────────┐     ┌─────────────────────┐   │
│  │  PostgreSQL  │     │    Kafka      │     │     ksqlDB          │   │
│  │  (Source)    │────►│   Connect     │────►│   (Processing)      │   │
│  │              │     │  (Debezium)   │     │                     │   │
│  └──────────────┘     └───────────────┘     └──────────┬──────────┘   │
│        │                     │                         │              │
│        │                     │                         ▼              │
│        │              ┌──────▼──────┐          ┌──────────────┐       │
│        │              │   Schema    │          │   Kafka      │       │
│        │              │  Registry   │          │   Topics     │       │
│        │              │   (Avro)    │          │ (Processed)  │       │
│        │              └─────────────┘          └──────┬───────┘       │
│        │                                              │               │
│        │                                              ▼               │
│        │                                       ┌──────────────┐       │
│        └───────────────────────────────────────│   Target DB  │       │
│                     Traditional ETL            │  (Analytics) │       │
│                     vs Real-time CDC           └──────────────┘       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Learning Objectives

By completing this project, you will:

- Configure Debezium for CDC from PostgreSQL
- Use Schema Registry for Avro serialization
- Build stream processing with ksqlDB
- Implement data transformations and enrichment
- Handle schema evolution in a pipeline
- Deploy a complete end-to-end data pipeline

## Prerequisites

- Completed Module 3 lessons (09-12)
- Docker and Docker Compose installed
- Basic SQL knowledge
- Python 3.9+ with `confluent-kafka[avro]` installed

---

## Part 1: Environment Setup

### 1.1 Docker Compose Configuration

Create a `docker-compose.yml` file for the complete CDC environment:

```yaml
# docker-compose-cdc.yml
version: '3.8'

services:
  # Source Database (PostgreSQL)
  postgres-source:
    image: postgres:14
    container_name: postgres-source
    hostname: postgres-source
    environment:
      POSTGRES_USER: cdc_user
      POSTGRES_PASSWORD: cdc_password
      POSTGRES_DB: ecommerce
    ports:
      - "5432:5432"
    volumes:
      - ./init-source.sql:/docker-entrypoint-initdb.d/init.sql
    command:
      - "postgres"
      - "-c"
      - "wal_level=logical"  # Required for CDC

  # Target Database (PostgreSQL for analytics)
  postgres-target:
    image: postgres:14
    container_name: postgres-target
    hostname: postgres-target
    environment:
      POSTGRES_USER: analytics_user
      POSTGRES_PASSWORD: analytics_password
      POSTGRES_DB: analytics
    ports:
      - "5433:5432"
    volumes:
      - ./init-target.sql:/docker-entrypoint-initdb.d/init.sql

  # Kafka (KRaft mode)
  kafka:
    image: confluentinc/cp-kafka:7.5.0
    container_name: kafka
    hostname: kafka
    ports:
      - "9092:9092"
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT,HOST:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092,HOST://localhost:9092
      KAFKA_LISTENERS: PLAINTEXT://kafka:29092,CONTROLLER://kafka:29093,HOST://0.0.0.0:9092
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka:29093
      KAFKA_PROCESS_ROLES: broker,controller
      CLUSTER_ID: 'MkU3OEVBNTcwNTJENDM2Qk'
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
      KAFKA_LOG_RETENTION_HOURS: 168

  # Schema Registry
  schema-registry:
    image: confluentinc/cp-schema-registry:7.5.0
    container_name: schema-registry
    hostname: schema-registry
    depends_on:
      - kafka
    ports:
      - "8081:8081"
    environment:
      SCHEMA_REGISTRY_HOST_NAME: schema-registry
      SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS: kafka:29092
      SCHEMA_REGISTRY_LISTENERS: http://0.0.0.0:8081

  # Kafka Connect with Debezium
  kafka-connect:
    image: confluentinc/cp-kafka-connect:7.5.0
    container_name: kafka-connect
    hostname: kafka-connect
    depends_on:
      - kafka
      - schema-registry
      - postgres-source
    ports:
      - "8083:8083"
    environment:
      CONNECT_BOOTSTRAP_SERVERS: kafka:29092
      CONNECT_REST_ADVERTISED_HOST_NAME: kafka-connect
      CONNECT_GROUP_ID: cdc-connect-group
      CONNECT_CONFIG_STORAGE_TOPIC: _connect-configs
      CONNECT_OFFSET_STORAGE_TOPIC: _connect-offsets
      CONNECT_STATUS_STORAGE_TOPIC: _connect-status
      CONNECT_CONFIG_STORAGE_REPLICATION_FACTOR: 1
      CONNECT_OFFSET_STORAGE_REPLICATION_FACTOR: 1
      CONNECT_STATUS_STORAGE_REPLICATION_FACTOR: 1
      CONNECT_KEY_CONVERTER: io.confluent.connect.avro.AvroConverter
      CONNECT_KEY_CONVERTER_SCHEMA_REGISTRY_URL: http://schema-registry:8081
      CONNECT_VALUE_CONVERTER: io.confluent.connect.avro.AvroConverter
      CONNECT_VALUE_CONVERTER_SCHEMA_REGISTRY_URL: http://schema-registry:8081
      CONNECT_PLUGIN_PATH: /usr/share/java,/usr/share/confluent-hub-components
    command:
      - bash
      - -c
      - |
        confluent-hub install --no-prompt debezium/debezium-connector-postgresql:2.4.0
        confluent-hub install --no-prompt confluentinc/kafka-connect-jdbc:10.7.4
        /etc/confluent/docker/run

  # ksqlDB
  ksqldb-server:
    image: confluentinc/cp-ksqldb-server:7.5.0
    container_name: ksqldb-server
    hostname: ksqldb-server
    depends_on:
      - kafka
      - schema-registry
    ports:
      - "8088:8088"
    environment:
      KSQL_BOOTSTRAP_SERVERS: kafka:29092
      KSQL_LISTENERS: http://0.0.0.0:8088
      KSQL_KSQL_SCHEMA_REGISTRY_URL: http://schema-registry:8081
      KSQL_KSQL_SERVICE_ID: cdc_ksql_
      KSQL_KSQL_STREAMS_AUTO_OFFSET_RESET: earliest

  # ksqlDB CLI
  ksqldb-cli:
    image: confluentinc/cp-ksqldb-cli:7.5.0
    container_name: ksqldb-cli
    depends_on:
      - ksqldb-server
    entrypoint: /bin/sh
    tty: true

networks:
  default:
    name: cdc-network
```

### 1.2 Source Database Initialization

Create `init-source.sql`:

```sql
-- init-source.sql
-- E-commerce source database schema

-- Customers table
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products table
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    sku VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    category VARCHAR(100),
    stock_quantity INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Orders table
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    order_status VARCHAR(50) DEFAULT 'pending',
    total_amount DECIMAL(10,2),
    shipping_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Order items table
CREATE TABLE order_items (
    item_id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(order_id),
    product_id INT REFERENCES products(product_id),
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create publication for CDC
CREATE PUBLICATION cdc_publication FOR ALL TABLES;

-- Insert sample data
INSERT INTO customers (email, first_name, last_name) VALUES
    ('alice@example.com', 'Alice', 'Smith'),
    ('bob@example.com', 'Bob', 'Jones'),
    ('carol@example.com', 'Carol', 'Williams');

INSERT INTO products (sku, name, description, price, category, stock_quantity) VALUES
    ('LAPTOP-001', 'Pro Laptop 15"', 'High-performance laptop', 1299.99, 'Electronics', 50),
    ('PHONE-001', 'SmartPhone X', 'Latest smartphone', 899.99, 'Electronics', 100),
    ('BOOK-001', 'Kafka Guide', 'Complete Kafka reference', 49.99, 'Books', 200),
    ('HDPH-001', 'Wireless Headphones', 'Noise-canceling headphones', 199.99, 'Electronics', 75);

-- Create function to update timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for updated_at
CREATE TRIGGER customers_updated_at BEFORE UPDATE ON customers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER products_updated_at BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER orders_updated_at BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
```

### 1.3 Target Database Initialization

Create `init-target.sql`:

```sql
-- init-target.sql
-- Analytics database schema (denormalized for reporting)

-- Customer orders summary (materialized view target)
CREATE TABLE customer_order_summary (
    customer_id INT PRIMARY KEY,
    email VARCHAR(255),
    full_name VARCHAR(255),
    total_orders INT DEFAULT 0,
    total_spent DECIMAL(12,2) DEFAULT 0,
    avg_order_value DECIMAL(10,2) DEFAULT 0,
    last_order_date TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Product sales metrics
CREATE TABLE product_sales_metrics (
    product_id INT PRIMARY KEY,
    sku VARCHAR(50),
    name VARCHAR(255),
    category VARCHAR(100),
    units_sold INT DEFAULT 0,
    total_revenue DECIMAL(12,2) DEFAULT 0,
    avg_quantity_per_order DECIMAL(5,2) DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Real-time order events (append-only log)
CREATE TABLE order_events (
    event_id SERIAL PRIMARY KEY,
    order_id INT,
    customer_id INT,
    customer_email VARCHAR(255),
    event_type VARCHAR(50),
    order_status VARCHAR(50),
    total_amount DECIMAL(10,2),
    event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for time-based queries
CREATE INDEX idx_order_events_timestamp ON order_events(event_timestamp);
```

### 1.4 Start the Environment

```bash
# Start all services
docker-compose -f docker-compose-cdc.yml up -d

# Wait for services to be ready (about 60 seconds)
echo "Waiting for services to start..."
sleep 60

# Verify services
docker-compose -f docker-compose-cdc.yml ps

# Check Kafka Connect is ready
curl -s http://localhost:8083/connectors | jq

# Check Schema Registry
curl -s http://localhost:8081/subjects | jq
```

---

## Part 2: Configure CDC with Debezium

### 2.1 Task: Create Debezium PostgreSQL Connector

Create a Debezium source connector that captures changes from all tables.

**Requirements:**
- Capture all tables (customers, products, orders, order_items)
- Use Avro serialization with Schema Registry
- Include before/after states for updates
- Use `pgoutput` plugin (native PostgreSQL)

### Template

Create `debezium-source.json`:

```json
{
    "name": "ecommerce-cdc-source",
    "config": {
        "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
        "tasks.max": "1",

        "database.hostname": "TODO",
        "database.port": "TODO",
        "database.user": "TODO",
        "database.password": "TODO",
        "database.dbname": "TODO",

        "topic.prefix": "TODO",
        "plugin.name": "TODO",
        "publication.name": "TODO",

        "schema.include.list": "public",
        "table.include.list": "TODO",

        "key.converter": "TODO",
        "key.converter.schema.registry.url": "TODO",
        "value.converter": "TODO",
        "value.converter.schema.registry.url": "TODO",

        "transforms": "unwrap",
        "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
        "transforms.unwrap.add.fields": "op,source.ts_ms",
        "transforms.unwrap.delete.handling.mode": "rewrite"
    }
}
```

### Solution

<details>
<summary>Click to reveal solution</summary>

```json
{
    "name": "ecommerce-cdc-source",
    "config": {
        "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
        "tasks.max": "1",

        "database.hostname": "postgres-source",
        "database.port": "5432",
        "database.user": "cdc_user",
        "database.password": "cdc_password",
        "database.dbname": "ecommerce",

        "topic.prefix": "ecommerce",
        "plugin.name": "pgoutput",
        "publication.name": "cdc_publication",

        "schema.include.list": "public",
        "table.include.list": "public.customers,public.products,public.orders,public.order_items",

        "key.converter": "io.confluent.connect.avro.AvroConverter",
        "key.converter.schema.registry.url": "http://schema-registry:8081",
        "value.converter": "io.confluent.connect.avro.AvroConverter",
        "value.converter.schema.registry.url": "http://schema-registry:8081",

        "transforms": "unwrap",
        "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
        "transforms.unwrap.add.fields": "op,source.ts_ms",
        "transforms.unwrap.delete.handling.mode": "rewrite"
    }
}
```

</details>

### 2.2 Deploy and Verify

```bash
# Deploy the connector
curl -X POST http://localhost:8083/connectors \
    -H "Content-Type: application/json" \
    -d @debezium-source.json

# Check connector status
curl http://localhost:8083/connectors/ecommerce-cdc-source/status | jq

# List created topics
docker exec -it kafka kafka-topics --list --bootstrap-server localhost:9092

# View messages from customers topic
docker exec -it kafka kafka-console-consumer \
    --bootstrap-server localhost:9092 \
    --topic ecommerce.public.customers \
    --from-beginning \
    --property print.key=true \
    --max-messages 3
```

---

## Part 3: Stream Processing with ksqlDB

### 3.1 Task: Create ksqlDB Streams and Tables

Connect to ksqlDB and create streams for processing CDC data.

```bash
# Connect to ksqlDB CLI
docker exec -it ksqldb-cli ksql http://ksqldb-server:8088
```

### 3.2 Create Source Streams

```sql
-- Set auto offset reset to earliest
SET 'auto.offset.reset' = 'earliest';

-- Create stream for customers CDC events
CREATE STREAM customers_cdc (
    customer_id INT KEY,
    email VARCHAR,
    first_name VARCHAR,
    last_name VARCHAR,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    __op VARCHAR,
    __source_ts_ms BIGINT
) WITH (
    KAFKA_TOPIC = 'ecommerce.public.customers',
    VALUE_FORMAT = 'AVRO'
);

-- Create stream for orders CDC events
CREATE STREAM orders_cdc (
    order_id INT KEY,
    customer_id INT,
    order_status VARCHAR,
    total_amount DECIMAL(10,2),
    shipping_address VARCHAR,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    __op VARCHAR,
    __source_ts_ms BIGINT
) WITH (
    KAFKA_TOPIC = 'ecommerce.public.orders',
    VALUE_FORMAT = 'AVRO'
);

-- Create stream for products CDC events
CREATE STREAM products_cdc (
    product_id INT KEY,
    sku VARCHAR,
    name VARCHAR,
    description VARCHAR,
    price DECIMAL(10,2),
    category VARCHAR,
    stock_quantity INT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    __op VARCHAR,
    __source_ts_ms BIGINT
) WITH (
    KAFKA_TOPIC = 'ecommerce.public.products',
    VALUE_FORMAT = 'AVRO'
);

-- Create stream for order_items CDC events
CREATE STREAM order_items_cdc (
    item_id INT KEY,
    order_id INT,
    product_id INT,
    quantity INT,
    unit_price DECIMAL(10,2),
    created_at TIMESTAMP,
    __op VARCHAR,
    __source_ts_ms BIGINT
) WITH (
    KAFKA_TOPIC = 'ecommerce.public.order_items',
    VALUE_FORMAT = 'AVRO'
);
```

### 3.3 Task: Create Materialized Views

Create ksqlDB tables that materialize aggregated views.

**Requirements:**
1. Customer lookup table (latest state)
2. Order events enriched with customer info
3. Product sales aggregates

### Template

```sql
-- TODO: Create customers table (materialized view of latest state)
CREATE TABLE customers_table AS
    SELECT
        -- TODO: Select fields
    FROM customers_cdc
    -- TODO: Add grouping
    EMIT CHANGES;

-- TODO: Create enriched orders stream
CREATE STREAM orders_enriched AS
    SELECT
        -- TODO: Join orders with customers
    FROM orders_cdc o
    -- TODO: Add join
    EMIT CHANGES;

-- TODO: Create product sales aggregates
CREATE TABLE product_sales AS
    SELECT
        -- TODO: Aggregate order items
    FROM order_items_cdc
    -- TODO: Add windowing and grouping
    EMIT CHANGES;
```

### Solution

<details>
<summary>Click to reveal solution</summary>

```sql
-- Customers table (latest state per customer)
CREATE TABLE customers_table AS
    SELECT
        customer_id,
        LATEST_BY_OFFSET(email) AS email,
        LATEST_BY_OFFSET(first_name) AS first_name,
        LATEST_BY_OFFSET(last_name) AS last_name,
        LATEST_BY_OFFSET(first_name) + ' ' + LATEST_BY_OFFSET(last_name) AS full_name,
        LATEST_BY_OFFSET(created_at) AS created_at,
        LATEST_BY_OFFSET(updated_at) AS updated_at
    FROM customers_cdc
    GROUP BY customer_id
    EMIT CHANGES;

-- Products table (latest state per product)
CREATE TABLE products_table AS
    SELECT
        product_id,
        LATEST_BY_OFFSET(sku) AS sku,
        LATEST_BY_OFFSET(name) AS name,
        LATEST_BY_OFFSET(price) AS price,
        LATEST_BY_OFFSET(category) AS category,
        LATEST_BY_OFFSET(stock_quantity) AS stock_quantity
    FROM products_cdc
    GROUP BY product_id
    EMIT CHANGES;

-- Enriched orders stream (orders joined with customer details)
CREATE STREAM orders_enriched WITH (
    KAFKA_TOPIC = 'orders_enriched',
    VALUE_FORMAT = 'AVRO'
) AS
    SELECT
        o.order_id AS order_id,
        o.customer_id AS customer_id,
        c.email AS customer_email,
        c.full_name AS customer_name,
        o.order_status AS order_status,
        o.total_amount AS total_amount,
        o.shipping_address AS shipping_address,
        o.created_at AS order_created_at,
        o.updated_at AS order_updated_at,
        o.__op AS operation,
        o.__source_ts_ms AS source_timestamp
    FROM orders_cdc o
    LEFT JOIN customers_table c ON o.customer_id = c.customer_id
    EMIT CHANGES;

-- Order events by status (for monitoring)
CREATE TABLE order_status_counts AS
    SELECT
        order_status,
        COUNT(*) AS order_count,
        SUM(total_amount) AS total_value
    FROM orders_cdc
    WINDOW TUMBLING (SIZE 1 HOUR)
    GROUP BY order_status
    EMIT CHANGES;

-- Product sales aggregates
CREATE TABLE product_sales AS
    SELECT
        oi.product_id AS product_id,
        COUNT(*) AS order_count,
        SUM(oi.quantity) AS units_sold,
        SUM(oi.quantity * oi.unit_price) AS total_revenue,
        AVG(CAST(oi.quantity AS DOUBLE)) AS avg_quantity
    FROM order_items_cdc oi
    GROUP BY oi.product_id
    EMIT CHANGES;

-- Top customers by spend (windowed)
CREATE TABLE top_customers_hourly AS
    SELECT
        customer_id,
        COUNT(*) AS order_count,
        SUM(total_amount) AS total_spent
    FROM orders_cdc
    WINDOW TUMBLING (SIZE 1 HOUR)
    GROUP BY customer_id
    EMIT CHANGES;
```

</details>

### 3.4 Verify Stream Processing

```sql
-- Check streams and tables
SHOW STREAMS;
SHOW TABLES;

-- Query enriched orders
SELECT * FROM orders_enriched EMIT CHANGES LIMIT 5;

-- Check product sales
SELECT * FROM product_sales;

-- Check order status distribution
SELECT * FROM order_status_counts;
```

---

## Part 4: Sink to Analytics Database

### 4.1 Task: Create JDBC Sink Connectors

Create connectors to load processed data into the target database.

**Requirements:**
1. Sink enriched orders to `order_events` table
2. Sink product sales to `product_sales_metrics` table
3. Use upsert mode for aggregated data

### Template

Create `jdbc-sink-orders.json`:

```json
{
    "name": "jdbc-sink-order-events",
    "config": {
        "connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
        "tasks.max": "1",
        "topics": "TODO",
        "connection.url": "TODO",
        "connection.user": "TODO",
        "connection.password": "TODO",
        "table.name.format": "TODO",
        "insert.mode": "TODO",
        "key.converter": "TODO",
        "value.converter": "TODO"
    }
}
```

### Solution

<details>
<summary>Click to reveal solution</summary>

```json
{
    "name": "jdbc-sink-order-events",
    "config": {
        "connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
        "tasks.max": "1",
        "topics": "orders_enriched",
        "connection.url": "jdbc:postgresql://postgres-target:5432/analytics",
        "connection.user": "analytics_user",
        "connection.password": "analytics_password",
        "table.name.format": "order_events",
        "insert.mode": "insert",
        "auto.create": "false",
        "pk.mode": "none",
        "key.converter": "org.apache.kafka.connect.storage.StringConverter",
        "value.converter": "io.confluent.connect.avro.AvroConverter",
        "value.converter.schema.registry.url": "http://schema-registry:8081",
        "transforms": "RenameFields",
        "transforms.RenameFields.type": "org.apache.kafka.connect.transforms.ReplaceField$Value",
        "transforms.RenameFields.renames": "operation:event_type,source_timestamp:event_timestamp"
    }
}
```

Create `jdbc-sink-product-sales.json`:

```json
{
    "name": "jdbc-sink-product-sales",
    "config": {
        "connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
        "tasks.max": "1",
        "topics": "PRODUCT_SALES",
        "connection.url": "jdbc:postgresql://postgres-target:5432/analytics",
        "connection.user": "analytics_user",
        "connection.password": "analytics_password",
        "table.name.format": "product_sales_metrics",
        "insert.mode": "upsert",
        "pk.mode": "record_key",
        "pk.fields": "product_id",
        "auto.create": "false",
        "key.converter": "org.apache.kafka.connect.storage.StringConverter",
        "value.converter": "io.confluent.connect.avro.AvroConverter",
        "value.converter.schema.registry.url": "http://schema-registry:8081"
    }
}
```

</details>

### 4.2 Deploy Sink Connectors

```bash
# Deploy order events sink
curl -X POST http://localhost:8083/connectors \
    -H "Content-Type: application/json" \
    -d @jdbc-sink-orders.json

# Deploy product sales sink
curl -X POST http://localhost:8083/connectors \
    -H "Content-Type: application/json" \
    -d @jdbc-sink-product-sales.json

# Verify connectors
curl http://localhost:8083/connectors | jq

# Check connector status
curl http://localhost:8083/connectors/jdbc-sink-order-events/status | jq
curl http://localhost:8083/connectors/jdbc-sink-product-sales/status | jq
```

---

## Part 5: Testing the Pipeline

### 5.1 Generate Test Data

Create a Python script to simulate e-commerce activity:

```python
# simulate_activity.py
import psycopg2
import random
import time
from datetime import datetime

def connect_source():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="ecommerce",
        user="cdc_user",
        password="cdc_password"
    )

def create_order(conn, customer_id):
    """Create a new order with items."""
    cur = conn.cursor()

    # Create order
    cur.execute("""
        INSERT INTO orders (customer_id, order_status, total_amount, shipping_address)
        VALUES (%s, 'pending', 0, '123 Main St')
        RETURNING order_id
    """, (customer_id,))
    order_id = cur.fetchone()[0]

    # Add 1-3 items
    total = 0
    cur.execute("SELECT product_id, price FROM products")
    products = cur.fetchall()

    for _ in range(random.randint(1, 3)):
        product_id, price = random.choice(products)
        quantity = random.randint(1, 3)
        total += price * quantity

        cur.execute("""
            INSERT INTO order_items (order_id, product_id, quantity, unit_price)
            VALUES (%s, %s, %s, %s)
        """, (order_id, product_id, quantity, price))

    # Update order total
    cur.execute("""
        UPDATE orders SET total_amount = %s WHERE order_id = %s
    """, (total, order_id))

    conn.commit()
    print(f"Created order {order_id} for customer {customer_id}, total: ${total:.2f}")
    return order_id

def update_order_status(conn, order_id, status):
    """Update order status."""
    cur = conn.cursor()
    cur.execute("""
        UPDATE orders SET order_status = %s WHERE order_id = %s
    """, (status, order_id))
    conn.commit()
    print(f"Updated order {order_id} status to {status}")

def add_customer(conn, email, first_name, last_name):
    """Add a new customer."""
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO customers (email, first_name, last_name)
        VALUES (%s, %s, %s)
        RETURNING customer_id
    """, (email, first_name, last_name))
    customer_id = cur.fetchone()[0]
    conn.commit()
    print(f"Added customer {customer_id}: {first_name} {last_name}")
    return customer_id

def update_product_stock(conn, product_id, quantity_change):
    """Update product stock."""
    cur = conn.cursor()
    cur.execute("""
        UPDATE products SET stock_quantity = stock_quantity + %s
        WHERE product_id = %s
    """, (quantity_change, product_id))
    conn.commit()
    print(f"Updated product {product_id} stock by {quantity_change}")

def simulate_activity(duration_seconds=60):
    """Simulate e-commerce activity."""
    conn = connect_source()

    statuses = ['confirmed', 'processing', 'shipped', 'delivered']
    first_names = ['David', 'Emma', 'Frank', 'Grace', 'Henry']
    last_names = ['Miller', 'Davis', 'Garcia', 'Wilson', 'Taylor']

    start_time = time.time()
    order_ids = []

    print(f"Simulating activity for {duration_seconds} seconds...")
    print("=" * 60)

    while time.time() - start_time < duration_seconds:
        action = random.choice(['order', 'status', 'customer', 'stock'])

        try:
            if action == 'order':
                # Create new order for random customer (1-3)
                customer_id = random.randint(1, 3)
                order_id = create_order(conn, customer_id)
                order_ids.append(order_id)

            elif action == 'status' and order_ids:
                # Update random order status
                order_id = random.choice(order_ids)
                status = random.choice(statuses)
                update_order_status(conn, order_id, status)

            elif action == 'customer':
                # Add new customer
                first = random.choice(first_names)
                last = random.choice(last_names)
                email = f"{first.lower()}.{last.lower()}{random.randint(1,999)}@example.com"
                add_customer(conn, email, first, last)

            elif action == 'stock':
                # Update product stock
                product_id = random.randint(1, 4)
                change = random.randint(-10, 50)
                update_product_stock(conn, product_id, change)

        except Exception as e:
            print(f"Error: {e}")

        time.sleep(random.uniform(0.5, 2.0))

    conn.close()
    print("=" * 60)
    print("Simulation complete!")

if __name__ == '__main__':
    simulate_activity(60)
```

### 5.2 Run the Simulation

```bash
# Install psycopg2 if needed
pip install psycopg2-binary

# Run simulation
python simulate_activity.py
```

### 5.3 Verify Data Flow

```bash
# Check Kafka topics have data
docker exec -it kafka kafka-console-consumer \
    --bootstrap-server localhost:9092 \
    --topic orders_enriched \
    --from-beginning \
    --max-messages 5

# Check ksqlDB aggregates
docker exec -it ksqldb-cli ksql http://ksqldb-server:8088 -e "SELECT * FROM product_sales;"

# Check target database
docker exec -it postgres-target psql -U analytics_user -d analytics -c "SELECT * FROM order_events LIMIT 10;"
docker exec -it postgres-target psql -U analytics_user -d analytics -c "SELECT * FROM product_sales_metrics;"
```

---

## Part 6: Monitoring and Observability

### 6.1 Create Monitoring Queries

```sql
-- In ksqlDB: Real-time pipeline monitoring

-- Message lag monitoring
SELECT
    TOPIC,
    COUNT(*) as message_count,
    MAX(ROWTIME) as latest_event
FROM orders_cdc
WINDOW TUMBLING (SIZE 1 MINUTE)
GROUP BY TOPIC
EMIT CHANGES;

-- Error detection (orders without customers)
SELECT
    order_id,
    customer_id,
    'MISSING_CUSTOMER' as error_type
FROM orders_enriched
WHERE customer_name IS NULL
EMIT CHANGES;
```

### 6.2 Python Monitoring Script

```python
# monitor_pipeline.py
import requests
import json
from datetime import datetime

def check_connectors():
    """Check Kafka Connect connector status."""
    response = requests.get('http://localhost:8083/connectors')
    connectors = response.json()

    print("Connector Status:")
    print("-" * 40)
    for connector in connectors:
        status = requests.get(f'http://localhost:8083/connectors/{connector}/status').json()
        state = status['connector']['state']
        tasks = status.get('tasks', [])
        task_states = [t['state'] for t in tasks]
        print(f"  {connector}: {state} (tasks: {task_states})")

def check_schema_registry():
    """Check Schema Registry subjects."""
    response = requests.get('http://localhost:8081/subjects')
    subjects = response.json()

    print("\nSchema Registry Subjects:")
    print("-" * 40)
    for subject in subjects[:10]:  # First 10
        print(f"  {subject}")
    if len(subjects) > 10:
        print(f"  ... and {len(subjects) - 10} more")

def check_consumer_lag():
    """Check consumer group lag (requires Kafka CLI)."""
    import subprocess
    result = subprocess.run([
        'docker', 'exec', 'kafka', 'kafka-consumer-groups',
        '--bootstrap-server', 'localhost:9092',
        '--describe', '--all-groups'
    ], capture_output=True, text=True)
    print("\nConsumer Group Lag:")
    print("-" * 40)
    print(result.stdout[:1000])  # First 1000 chars

def main():
    print(f"Pipeline Health Check - {datetime.now()}")
    print("=" * 60)
    check_connectors()
    check_schema_registry()
    check_consumer_lag()

if __name__ == '__main__':
    main()
```

---

## Deliverables

Complete the following for project submission:

1. **Working Docker Compose configuration** with all services
2. **Debezium source connector** configuration
3. **ksqlDB streams and tables** for data processing
4. **JDBC sink connectors** for analytics database
5. **Test script** demonstrating end-to-end data flow
6. **Monitoring script** showing pipeline health

## Evaluation Criteria

| Criteria | Points |
|----------|--------|
| CDC connector properly configured | 20 |
| Schema Registry integration working | 15 |
| ksqlDB stream processing correct | 25 |
| Sink connectors loading data | 20 |
| End-to-end data flow verified | 15 |
| Documentation and cleanup scripts | 5 |
| **Total** | **100** |

## Cleanup

```bash
# Stop all containers
docker-compose -f docker-compose-cdc.yml down

# Remove volumes (optional - deletes all data)
docker-compose -f docker-compose-cdc.yml down -v

# Remove network
docker network rm cdc-network
```

---

## Extension Challenges

If you complete the project early, try these extensions:

1. **Add dead letter queue** for failed records
2. **Implement schema evolution** by adding a new column
3. **Add Prometheus metrics** for connector monitoring
4. **Implement exactly-once** with transactional sink
5. **Add data quality checks** in ksqlDB

---

**[← Back to Module 3](./README.md)** | **[Next: Module 4 →](../module_4_advanced/README.md)**
