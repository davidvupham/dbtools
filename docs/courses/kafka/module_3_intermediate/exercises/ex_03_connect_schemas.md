# Module 3 Exercises: Kafka Connect, Schema Registry, and Exactly-Once

**[← Back to Module 3](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

## Overview

These exercises will help you master Kafka Connect, Schema Registry, serialization formats, and exactly-once semantics through hands-on practice. Complete all exercises to solidify your understanding of intermediate Kafka concepts.

**Prerequisites:**
- Completed Lessons 09-12
- Docker environment running with Schema Registry (see [Docker Setup](../../docker/README.md))
- Python with `confluent-kafka[avro]` installed

---

## Exercise 1: File Source Connector

**Objective:** Configure and deploy a File Source connector to stream log data into Kafka.

### Setup

```bash
# Start the Kafka Connect environment (if using docker-compose)
docker-compose up -d

# Create the target topic
docker exec -it kafka kafka-topics --create --topic server-logs \
    --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1

# Create a sample log file
docker exec -it kafka-connect bash -c 'mkdir -p /tmp/logs && \
    echo "2026-01-22 10:00:00 INFO Application started" > /tmp/logs/app.log && \
    echo "2026-01-22 10:00:01 DEBUG Processing request 1" >> /tmp/logs/app.log && \
    echo "2026-01-22 10:00:02 ERROR Connection timeout" >> /tmp/logs/app.log'
```

### Task

Create a File Source connector configuration that:
1. Reads from `/tmp/logs/app.log`
2. Sends each line to the `server-logs` topic
3. Tracks file position to avoid re-reading on restart

### Template

```json
{
    "name": "file-source-logs",
    "config": {
        "connector.class": "TODO",
        "tasks.max": "1",
        "file": "TODO",
        "topic": "TODO"
    }
}
```

### Deploy the connector

```bash
# Submit connector configuration
curl -X POST http://localhost:8083/connectors \
    -H "Content-Type: application/json" \
    -d @file-source-config.json

# Check connector status
curl http://localhost:8083/connectors/file-source-logs/status
```

### Verification

```bash
# Consume from the topic to verify data
docker exec -it kafka kafka-console-consumer \
    --bootstrap-server localhost:9092 \
    --topic server-logs \
    --from-beginning
```

### Solution

<details>
<summary>Click to reveal solution</summary>

```json
{
    "name": "file-source-logs",
    "config": {
        "connector.class": "org.apache.kafka.connect.file.FileStreamSourceConnector",
        "tasks.max": "1",
        "file": "/tmp/logs/app.log",
        "topic": "server-logs",
        "key.converter": "org.apache.kafka.connect.storage.StringConverter",
        "value.converter": "org.apache.kafka.connect.storage.StringConverter"
    }
}
```

**Explanation:**
- `FileStreamSourceConnector` is a simple built-in connector for file streaming
- `tasks.max=1` because we have a single file
- Converters set to String for plain text log lines
- File position is tracked in Connect's offset storage

</details>

---

## Exercise 2: JDBC Sink Connector

**Objective:** Configure a JDBC Sink connector to write Kafka messages to a database.

### Setup

```bash
# Start PostgreSQL (add to docker-compose or run separately)
docker run -d --name postgres \
    -e POSTGRES_USER=kafka \
    -e POSTGRES_PASSWORD=kafka123 \
    -e POSTGRES_DB=kafkadb \
    -p 5432:5432 \
    postgres:14

# Create a table
docker exec -it postgres psql -U kafka -d kafkadb -c "
CREATE TABLE orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50),
    product VARCHAR(100),
    quantity INT,
    price DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);"

# Create source topic
docker exec -it kafka kafka-topics --create --topic orders-for-db \
    --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
```

### Task

Create a JDBC Sink connector that:
1. Reads from `orders-for-db` topic
2. Writes to the `orders` table in PostgreSQL
3. Uses upsert mode (insert or update)
4. Uses `order_id` as the primary key

### Template

```json
{
    "name": "jdbc-sink-orders",
    "config": {
        "connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
        "tasks.max": "1",
        "topics": "TODO",
        "connection.url": "TODO",
        "connection.user": "TODO",
        "connection.password": "TODO",
        "insert.mode": "TODO",
        "pk.mode": "TODO",
        "pk.fields": "TODO",
        "auto.create": "false",
        "key.converter": "org.apache.kafka.connect.storage.StringConverter",
        "value.converter": "org.apache.kafka.connect.json.JsonConverter",
        "value.converter.schemas.enable": "false"
    }
}
```

### Producer Script (to test)

```python
# produce_orders.py
from confluent_kafka import Producer
import json
import uuid

producer = Producer({'bootstrap.servers': 'localhost:9092'})

orders = [
    {'order_id': 'ORD-001', 'customer_id': 'CUST-100', 'product': 'Laptop', 'quantity': 1, 'price': 999.99},
    {'order_id': 'ORD-002', 'customer_id': 'CUST-101', 'product': 'Mouse', 'quantity': 2, 'price': 29.99},
    {'order_id': 'ORD-003', 'customer_id': 'CUST-100', 'product': 'Keyboard', 'quantity': 1, 'price': 79.99},
]

for order in orders:
    producer.produce(
        'orders-for-db',
        key=order['order_id'],
        value=json.dumps(order)
    )

producer.flush()
print(f"Sent {len(orders)} orders")
```

### Verification

```bash
# Check data in PostgreSQL
docker exec -it postgres psql -U kafka -d kafkadb -c "SELECT * FROM orders;"
```

### Solution

<details>
<summary>Click to reveal solution</summary>

```json
{
    "name": "jdbc-sink-orders",
    "config": {
        "connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
        "tasks.max": "1",
        "topics": "orders-for-db",
        "connection.url": "jdbc:postgresql://postgres:5432/kafkadb",
        "connection.user": "kafka",
        "connection.password": "kafka123",
        "insert.mode": "upsert",
        "pk.mode": "record_value",
        "pk.fields": "order_id",
        "auto.create": "false",
        "auto.evolve": "false",
        "key.converter": "org.apache.kafka.connect.storage.StringConverter",
        "value.converter": "org.apache.kafka.connect.json.JsonConverter",
        "value.converter.schemas.enable": "false"
    }
}
```

**Explanation:**
- `insert.mode=upsert` updates existing rows or inserts new ones
- `pk.mode=record_value` extracts primary key from message value
- `pk.fields=order_id` specifies which field is the primary key
- The connector will match JSON fields to table columns by name

</details>

---

## Exercise 3: Schema Registry with Avro Producer

**Objective:** Create a producer that uses Avro serialization with Schema Registry.

### Setup

```bash
# Verify Schema Registry is running
curl http://localhost:8081/subjects

# Create topic for Avro messages
docker exec -it kafka kafka-topics --create --topic users-avro \
    --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
```

### Task

Create a Python producer that:
1. Defines an Avro schema for User records
2. Registers the schema with Schema Registry
3. Produces Avro-serialized messages
4. Handles schema evolution (add an optional field)

### Template

```python
# avro_producer.py
from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import SerializationContext, MessageField

# TODO: Define Avro schema
USER_SCHEMA = """
{
    "type": "record",
    "name": "User",
    "namespace": "com.example",
    "fields": [
        // TODO: Add fields
    ]
}
"""

def user_to_dict(user, ctx):
    """Convert User object to dictionary for serialization."""
    # TODO: Implement
    pass

class User:
    def __init__(self, user_id: str, name: str, email: str, age: int):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.age = age

def main():
    # TODO: Set up Schema Registry client
    # TODO: Create Avro serializer
    # TODO: Configure producer
    # TODO: Produce sample users
    pass

if __name__ == '__main__':
    main()
```

### Expected Output

```
Registered schema with ID: 1
Produced user-001 to partition 0
Produced user-002 to partition 1
Produced user-003 to partition 2
All users produced successfully
```

### Solution

<details>
<summary>Click to reveal solution</summary>

```python
from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import SerializationContext, MessageField

USER_SCHEMA = """
{
    "type": "record",
    "name": "User",
    "namespace": "com.example",
    "fields": [
        {"name": "user_id", "type": "string"},
        {"name": "name", "type": "string"},
        {"name": "email", "type": "string"},
        {"name": "age", "type": "int"},
        {"name": "phone", "type": ["null", "string"], "default": null}
    ]
}
"""

class User:
    def __init__(self, user_id: str, name: str, email: str, age: int, phone: str = None):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.age = age
        self.phone = phone

def user_to_dict(user, ctx):
    """Convert User object to dictionary for Avro serialization."""
    return {
        'user_id': user.user_id,
        'name': user.name,
        'email': user.email,
        'age': user.age,
        'phone': user.phone
    }

def delivery_callback(err, msg):
    if err:
        print(f"Delivery failed: {err}")
    else:
        print(f"Produced {msg.key().decode()} to partition {msg.partition()}")

def main():
    # Schema Registry client
    schema_registry_conf = {'url': 'http://localhost:8081'}
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)

    # Avro serializer
    avro_serializer = AvroSerializer(
        schema_registry_client,
        USER_SCHEMA,
        user_to_dict
    )

    # Producer configuration
    producer_conf = {
        'bootstrap.servers': 'localhost:9092',
        'acks': 'all'
    }
    producer = Producer(producer_conf)

    # Sample users
    users = [
        User('user-001', 'Alice Smith', 'alice@example.com', 30, '+1-555-0101'),
        User('user-002', 'Bob Jones', 'bob@example.com', 25),
        User('user-003', 'Carol White', 'carol@example.com', 35, '+1-555-0103'),
    ]

    # Produce users
    topic = 'users-avro'
    for user in users:
        producer.produce(
            topic=topic,
            key=user.user_id.encode('utf-8'),
            value=avro_serializer(user, SerializationContext(topic, MessageField.VALUE)),
            callback=delivery_callback
        )
        producer.poll(0)

    producer.flush()
    print("\nAll users produced successfully")

    # Check registered schema
    subjects = schema_registry_client.get_subjects()
    print(f"\nRegistered subjects: {subjects}")

if __name__ == '__main__':
    main()
```

**Key Points:**
- Schema includes optional `phone` field with null union type
- `user_to_dict` converts objects to dictionaries for serialization
- Schema is automatically registered on first produce
- Schema ID is included in each message header

</details>

---

## Exercise 4: Avro Consumer with Schema Evolution

**Objective:** Create a consumer that reads Avro messages and handles schema evolution.

### Task

Create a Python consumer that:
1. Reads Avro-serialized messages from `users-avro`
2. Deserializes using Schema Registry
3. Handles messages produced with different schema versions
4. Prints user information

### Template

```python
# avro_consumer.py
from confluent_kafka import Consumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField

def dict_to_user(obj, ctx):
    """Convert dictionary to User object."""
    # TODO: Implement
    pass

class User:
    def __init__(self, user_id: str, name: str, email: str, age: int, phone: str = None):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.age = age
        self.phone = phone

    def __str__(self):
        phone_str = self.phone if self.phone else 'N/A'
        return f"User({self.user_id}, {self.name}, {self.email}, age={self.age}, phone={phone_str})"

def main():
    # TODO: Set up Schema Registry client
    # TODO: Create Avro deserializer
    # TODO: Configure consumer
    # TODO: Consume and print users
    pass

if __name__ == '__main__':
    main()
```

### Solution

<details>
<summary>Click to reveal solution</summary>

```python
from confluent_kafka import Consumer, KafkaError
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField

class User:
    def __init__(self, user_id: str, name: str, email: str, age: int, phone: str = None):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.age = age
        self.phone = phone

    def __str__(self):
        phone_str = self.phone if self.phone else 'N/A'
        return f"User({self.user_id}, {self.name}, {self.email}, age={self.age}, phone={phone_str})"

def dict_to_user(obj, ctx):
    """Convert dictionary from Avro to User object."""
    if obj is None:
        return None
    return User(
        user_id=obj['user_id'],
        name=obj['name'],
        email=obj['email'],
        age=obj['age'],
        phone=obj.get('phone')  # Handle optional field
    )

def main():
    # Schema Registry client
    schema_registry_conf = {'url': 'http://localhost:8081'}
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)

    # Avro deserializer (schema fetched from registry)
    avro_deserializer = AvroDeserializer(
        schema_registry_client,
        schema_str=None,  # Use schema from registry
        from_dict=dict_to_user
    )

    # Consumer configuration
    consumer_conf = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'avro-consumer-group',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': True
    }
    consumer = Consumer(consumer_conf)
    consumer.subscribe(['users-avro'])

    print("Consuming users (Ctrl+C to exit)...")
    print("-" * 60)

    try:
        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    print(f"Reached end of partition {msg.partition()}")
                else:
                    print(f"Error: {msg.error()}")
                continue

            # Deserialize Avro message
            user = avro_deserializer(
                msg.value(),
                SerializationContext(msg.topic(), MessageField.VALUE)
            )

            if user:
                print(f"Received: {user}")
                print(f"  Partition: {msg.partition()}, Offset: {msg.offset()}")

    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        consumer.close()

if __name__ == '__main__':
    main()
```

**Key Points:**
- `schema_str=None` tells the deserializer to fetch schema from registry
- `obj.get('phone')` handles optional fields gracefully
- Schema evolution is automatic - old messages work with new schema

</details>

---

## Exercise 5: JSON Schema Validation

**Objective:** Implement JSON Schema validation for Kafka messages.

### Setup

```bash
# Create topic for JSON Schema messages
docker exec -it kafka kafka-topics --create --topic products-json \
    --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
```

### Task

Create a producer and consumer that:
1. Define a JSON Schema for Product records
2. Validate messages before producing
3. Register schema with Schema Registry
4. Consume and validate messages

### Template

```python
# json_schema_producer.py
from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer
from confluent_kafka.serialization import SerializationContext, MessageField

# TODO: Define JSON Schema
PRODUCT_SCHEMA = """
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Product",
    "type": "object",
    "properties": {
        // TODO: Add properties
    },
    "required": ["TODO"]
}
"""

class Product:
    def __init__(self, product_id: str, name: str, category: str, price: float, in_stock: bool):
        self.product_id = product_id
        self.name = name
        self.category = category
        self.price = price
        self.in_stock = in_stock

def product_to_dict(product, ctx):
    """Convert Product to dictionary."""
    # TODO: Implement
    pass

def main():
    # TODO: Implement producer with JSON Schema
    pass

if __name__ == '__main__':
    main()
```

### Solution

<details>
<summary>Click to reveal solution</summary>

```python
from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer
from confluent_kafka.serialization import SerializationContext, MessageField

PRODUCT_SCHEMA = """
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Product",
    "type": "object",
    "properties": {
        "product_id": {
            "type": "string",
            "description": "Unique product identifier"
        },
        "name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 100
        },
        "category": {
            "type": "string",
            "enum": ["electronics", "clothing", "food", "books", "other"]
        },
        "price": {
            "type": "number",
            "minimum": 0,
            "exclusiveMinimum": true
        },
        "in_stock": {
            "type": "boolean"
        }
    },
    "required": ["product_id", "name", "category", "price", "in_stock"]
}
"""

class Product:
    def __init__(self, product_id: str, name: str, category: str, price: float, in_stock: bool):
        self.product_id = product_id
        self.name = name
        self.category = category
        self.price = price
        self.in_stock = in_stock

def product_to_dict(product, ctx):
    return {
        'product_id': product.product_id,
        'name': product.name,
        'category': product.category,
        'price': product.price,
        'in_stock': product.in_stock
    }

def delivery_callback(err, msg):
    if err:
        print(f"Delivery failed: {err}")
    else:
        print(f"Produced {msg.key().decode()} to partition {msg.partition()}")

def main():
    # Schema Registry client
    schema_registry_conf = {'url': 'http://localhost:8081'}
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)

    # JSON Schema serializer
    json_serializer = JSONSerializer(
        PRODUCT_SCHEMA,
        schema_registry_client,
        product_to_dict
    )

    # Producer
    producer = Producer({'bootstrap.servers': 'localhost:9092'})

    # Valid products
    products = [
        Product('PROD-001', 'Laptop Pro', 'electronics', 1299.99, True),
        Product('PROD-002', 'Python Book', 'books', 49.99, True),
        Product('PROD-003', 'T-Shirt', 'clothing', 29.99, False),
    ]

    topic = 'products-json'
    for product in products:
        try:
            producer.produce(
                topic=topic,
                key=product.product_id.encode('utf-8'),
                value=json_serializer(product, SerializationContext(topic, MessageField.VALUE)),
                callback=delivery_callback
            )
            producer.poll(0)
        except Exception as e:
            print(f"Validation error for {product.product_id}: {e}")

    producer.flush()

    # Try invalid product (should fail validation)
    print("\nTrying invalid product...")
    try:
        invalid_product = Product('PROD-004', 'Invalid', 'INVALID_CATEGORY', -10, True)
        producer.produce(
            topic=topic,
            key=invalid_product.product_id.encode('utf-8'),
            value=json_serializer(invalid_product, SerializationContext(topic, MessageField.VALUE))
        )
    except Exception as e:
        print(f"Expected validation error: {e}")

if __name__ == '__main__':
    main()
```

**Key Points:**
- JSON Schema enforces data types, enums, and constraints
- Invalid messages are rejected before being sent
- Schema is registered automatically with Schema Registry

</details>

---

## Exercise 6: Transactional Producer

**Objective:** Implement a transactional producer for exactly-once semantics.

### Setup

```bash
# Create topics for transactional processing
docker exec -it kafka kafka-topics --create --topic inventory-input \
    --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1

docker exec -it kafka kafka-topics --create --topic inventory-output \
    --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
```

### Task

Create a transactional application that:
1. Reads inventory updates from `inventory-input`
2. Processes updates (adjust stock levels)
3. Writes results to `inventory-output`
4. Uses transactions to ensure exactly-once processing

### Template

```python
# transactional_processor.py
from confluent_kafka import Consumer, Producer, KafkaError
import json
import uuid

def create_transactional_producer():
    """Create a producer configured for transactions."""
    config = {
        'bootstrap.servers': 'localhost:9092',
        # TODO: Add transaction configuration
    }
    producer = Producer(config)
    # TODO: Initialize transactions
    return producer

def process_inventory_update(update: dict) -> dict:
    """Process an inventory update and return result."""
    # Simulate processing: add timestamp and calculate new stock
    return {
        'product_id': update['product_id'],
        'previous_stock': update.get('current_stock', 0),
        'adjustment': update['adjustment'],
        'new_stock': update.get('current_stock', 0) + update['adjustment'],
        'processed': True
    }

def main():
    # TODO: Create transactional producer
    # TODO: Create consumer
    # TODO: Implement consume-process-produce loop with transactions
    pass

if __name__ == '__main__':
    main()
```

### Test Data Producer

```python
# produce_inventory_updates.py
from confluent_kafka import Producer
import json

producer = Producer({'bootstrap.servers': 'localhost:9092'})

updates = [
    {'product_id': 'SKU-001', 'current_stock': 100, 'adjustment': -5},
    {'product_id': 'SKU-002', 'current_stock': 50, 'adjustment': 10},
    {'product_id': 'SKU-001', 'current_stock': 95, 'adjustment': -3},
    {'product_id': 'SKU-003', 'current_stock': 200, 'adjustment': -50},
]

for update in updates:
    producer.produce(
        'inventory-input',
        key=update['product_id'].encode(),
        value=json.dumps(update).encode()
    )

producer.flush()
print(f"Sent {len(updates)} inventory updates")
```

### Solution

<details>
<summary>Click to reveal solution</summary>

```python
from confluent_kafka import Consumer, Producer, KafkaError, TopicPartition
import json
import uuid

def create_transactional_producer():
    """Create a producer configured for transactions."""
    config = {
        'bootstrap.servers': 'localhost:9092',
        'transactional.id': f'inventory-processor-{uuid.uuid4()}',
        'enable.idempotence': True,
        'acks': 'all',
        'retries': 3
    }
    producer = Producer(config)
    producer.init_transactions()
    return producer

def create_consumer():
    """Create a consumer for transactional processing."""
    config = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'inventory-processor-group',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': False,  # Manual commit via transaction
        'isolation.level': 'read_committed'  # Only read committed messages
    }
    return Consumer(config)

def process_inventory_update(update: dict) -> dict:
    """Process an inventory update and return result."""
    return {
        'product_id': update['product_id'],
        'previous_stock': update.get('current_stock', 0),
        'adjustment': update['adjustment'],
        'new_stock': update.get('current_stock', 0) + update['adjustment'],
        'processed': True
    }

def main():
    producer = create_transactional_producer()
    consumer = create_consumer()
    consumer.subscribe(['inventory-input'])

    print("Starting transactional processor...")
    print("=" * 60)

    processed_count = 0

    try:
        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                if processed_count > 0:
                    print(f"\nProcessed {processed_count} messages")
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                print(f"Error: {msg.error()}")
                continue

            # Parse input
            update = json.loads(msg.value().decode())
            print(f"\nReceived: {update}")

            # Begin transaction
            producer.begin_transaction()

            try:
                # Process the update
                result = process_inventory_update(update)
                print(f"Processed: {result}")

                # Produce to output topic (within transaction)
                producer.produce(
                    'inventory-output',
                    key=result['product_id'].encode(),
                    value=json.dumps(result).encode()
                )

                # Send consumer offsets as part of transaction
                producer.send_offsets_to_transaction(
                    consumer.position(consumer.assignment()),
                    consumer.consumer_group_metadata()
                )

                # Commit transaction (atomic: produce + offset commit)
                producer.commit_transaction()
                processed_count += 1
                print(f"Transaction committed (total: {processed_count})")

            except Exception as e:
                print(f"Transaction failed: {e}")
                producer.abort_transaction()

    except KeyboardInterrupt:
        print(f"\nShutting down. Processed {processed_count} messages.")
    finally:
        consumer.close()

if __name__ == '__main__':
    main()
```

**Key Points:**
- `transactional.id` enables transactions (must be unique per instance)
- `init_transactions()` must be called before any transactional operations
- `send_offsets_to_transaction()` includes consumer offsets in the transaction
- `commit_transaction()` atomically commits produce + offset
- `isolation.level=read_committed` ensures consumer only sees committed data

</details>

---

## Exercise 7: Schema Compatibility Testing

**Objective:** Test schema compatibility rules in Schema Registry.

### Task

1. Register an initial schema
2. Try to evolve it with compatible changes
3. Try to evolve it with incompatible changes
4. Observe which changes are allowed

### Template

```python
# schema_compatibility_test.py
from confluent_kafka.schema_registry import SchemaRegistryClient, Schema
import json

def test_schema_evolution():
    """Test schema compatibility rules."""
    client = SchemaRegistryClient({'url': 'http://localhost:8081'})

    # Initial schema
    schema_v1 = Schema("""
    {
        "type": "record",
        "name": "Event",
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "timestamp", "type": "long"}
        ]
    }
    """, schema_type='AVRO')

    # TODO: Register initial schema
    # TODO: Test adding optional field (should succeed)
    # TODO: Test adding required field (should fail with BACKWARD compatibility)
    # TODO: Test removing field (depends on compatibility mode)

if __name__ == '__main__':
    test_schema_evolution()
```

### Solution

<details>
<summary>Click to reveal solution</summary>

```python
from confluent_kafka.schema_registry import SchemaRegistryClient, Schema
from confluent_kafka.schema_registry.error import SchemaRegistryError

def test_schema_evolution():
    """Test schema compatibility rules."""
    client = SchemaRegistryClient({'url': 'http://localhost:8081'})
    subject = 'events-value'

    print("Schema Compatibility Testing")
    print("=" * 60)

    # Initial schema
    schema_v1 = Schema("""
    {
        "type": "record",
        "name": "Event",
        "namespace": "com.example",
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "timestamp", "type": "long"}
        ]
    }
    """, schema_type='AVRO')

    # Register initial schema
    print("\n1. Registering initial schema...")
    schema_id_v1 = client.register_schema(subject, schema_v1)
    print(f"   Registered with ID: {schema_id_v1}")

    # Check current compatibility level
    try:
        compat_level = client.get_compatibility(subject)
        print(f"   Compatibility level: {compat_level}")
    except SchemaRegistryError:
        print("   Compatibility level: BACKWARD (default)")

    # Test 1: Add optional field (should succeed)
    print("\n2. Adding optional field (source) with default...")
    schema_v2 = Schema("""
    {
        "type": "record",
        "name": "Event",
        "namespace": "com.example",
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "timestamp", "type": "long"},
            {"name": "source", "type": "string", "default": "unknown"}
        ]
    }
    """, schema_type='AVRO')

    try:
        # Test compatibility first
        is_compatible = client.test_compatibility(subject, schema_v2)
        print(f"   Compatible: {is_compatible}")

        if is_compatible:
            schema_id_v2 = client.register_schema(subject, schema_v2)
            print(f"   Registered with ID: {schema_id_v2}")
    except SchemaRegistryError as e:
        print(f"   Failed: {e}")

    # Test 2: Add required field without default (should fail with BACKWARD)
    print("\n3. Adding required field (category) WITHOUT default...")
    schema_v3_bad = Schema("""
    {
        "type": "record",
        "name": "Event",
        "namespace": "com.example",
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "timestamp", "type": "long"},
            {"name": "source", "type": "string", "default": "unknown"},
            {"name": "category", "type": "string"}
        ]
    }
    """, schema_type='AVRO')

    try:
        is_compatible = client.test_compatibility(subject, schema_v3_bad)
        print(f"   Compatible: {is_compatible}")
    except SchemaRegistryError as e:
        print(f"   Incompatible (expected): {e}")

    # Test 3: Add nullable field (should succeed)
    print("\n4. Adding nullable field (metadata)...")
    schema_v3_good = Schema("""
    {
        "type": "record",
        "name": "Event",
        "namespace": "com.example",
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "timestamp", "type": "long"},
            {"name": "source", "type": "string", "default": "unknown"},
            {"name": "metadata", "type": ["null", "string"], "default": null}
        ]
    }
    """, schema_type='AVRO')

    try:
        is_compatible = client.test_compatibility(subject, schema_v3_good)
        print(f"   Compatible: {is_compatible}")

        if is_compatible:
            schema_id_v3 = client.register_schema(subject, schema_v3_good)
            print(f"   Registered with ID: {schema_id_v3}")
    except SchemaRegistryError as e:
        print(f"   Failed: {e}")

    # List all versions
    print("\n5. All registered versions:")
    versions = client.get_versions(subject)
    for version in versions:
        schema = client.get_schema(client.get_latest_version(subject).schema_id)
        print(f"   Version {version}")

    print("\n" + "=" * 60)
    print("Summary: BACKWARD compatibility allows:")
    print("  - Adding fields with defaults")
    print("  - Adding nullable fields")
    print("  - Widening types")
    print("Does NOT allow:")
    print("  - Adding required fields without defaults")
    print("  - Removing fields (without FORWARD compatibility)")
    print("  - Renaming fields")

if __name__ == '__main__':
    test_schema_evolution()
```

</details>

---

## Exercise 8: Connector Transforms

**Objective:** Apply Single Message Transforms (SMTs) to modify data in flight.

### Task

Configure a connector with SMTs that:
1. Filter out records based on a field value
2. Add a timestamp field
3. Rename a field
4. Mask sensitive data

### Template

```json
{
    "name": "orders-with-transforms",
    "config": {
        "connector.class": "io.confluent.connect.jdbc.JdbcSourceConnector",
        "tasks.max": "1",
        "connection.url": "jdbc:postgresql://postgres:5432/kafkadb",
        "connection.user": "kafka",
        "connection.password": "kafka123",
        "table.whitelist": "orders",
        "mode": "incrementing",
        "incrementing.column.name": "id",
        "topic.prefix": "db-",

        "transforms": "TODO",
        "transforms.addTimestamp.type": "TODO",
        "transforms.filter.type": "TODO",
        "transforms.filter.condition": "TODO"
    }
}
```

### Solution

<details>
<summary>Click to reveal solution</summary>

```json
{
    "name": "orders-with-transforms",
    "config": {
        "connector.class": "io.confluent.connect.jdbc.JdbcSourceConnector",
        "tasks.max": "1",
        "connection.url": "jdbc:postgresql://postgres:5432/kafkadb",
        "connection.user": "kafka",
        "connection.password": "kafka123",
        "table.whitelist": "orders",
        "mode": "incrementing",
        "incrementing.column.name": "id",
        "topic.prefix": "db-",

        "transforms": "addTimestamp,filterSmallOrders,renameField,maskEmail",

        "transforms.addTimestamp.type": "org.apache.kafka.connect.transforms.InsertField$Value",
        "transforms.addTimestamp.timestamp.field": "processed_at",

        "transforms.filterSmallOrders.type": "org.apache.kafka.connect.transforms.Filter",
        "transforms.filterSmallOrders.predicate": "isSmallOrder",

        "predicates": "isSmallOrder",
        "predicates.isSmallOrder.type": "org.apache.kafka.connect.transforms.predicates.RecordIsTombstone",

        "transforms.renameField.type": "org.apache.kafka.connect.transforms.ReplaceField$Value",
        "transforms.renameField.renames": "customer_email:email",

        "transforms.maskEmail.type": "org.apache.kafka.connect.transforms.MaskField$Value",
        "transforms.maskEmail.fields": "email",
        "transforms.maskEmail.replacement": "***@***.***"
    }
}
```

**Common SMTs:**
- `InsertField` - Add static or timestamp fields
- `ReplaceField` - Rename, include, or exclude fields
- `MaskField` - Replace sensitive field values
- `Filter` - Drop records based on predicates
- `TimestampRouter` - Route to topics based on timestamp
- `ValueToKey` - Extract key from value fields

</details>

---

## Verification Checklist

After completing these exercises, you should be able to:

- [ ] Configure and deploy Kafka Connect source connectors
- [ ] Configure and deploy Kafka Connect sink connectors
- [ ] Create Avro schemas and register them with Schema Registry
- [ ] Produce and consume Avro-serialized messages
- [ ] Implement JSON Schema validation
- [ ] Use transactional producers for exactly-once semantics
- [ ] Test schema compatibility and evolution
- [ ] Apply Single Message Transforms in connectors

---

## Cleanup

```bash
# Delete test topics
docker exec -it kafka kafka-topics --delete --topic server-logs --bootstrap-server localhost:9092
docker exec -it kafka kafka-topics --delete --topic orders-for-db --bootstrap-server localhost:9092
docker exec -it kafka kafka-topics --delete --topic users-avro --bootstrap-server localhost:9092
docker exec -it kafka kafka-topics --delete --topic products-json --bootstrap-server localhost:9092
docker exec -it kafka kafka-topics --delete --topic inventory-input --bootstrap-server localhost:9092
docker exec -it kafka kafka-topics --delete --topic inventory-output --bootstrap-server localhost:9092

# Delete connectors
curl -X DELETE http://localhost:8083/connectors/file-source-logs
curl -X DELETE http://localhost:8083/connectors/jdbc-sink-orders

# Delete Schema Registry subjects
curl -X DELETE http://localhost:8081/subjects/users-avro-value
curl -X DELETE http://localhost:8081/subjects/products-json-value
curl -X DELETE http://localhost:8081/subjects/events-value

# Stop PostgreSQL
docker stop postgres && docker rm postgres
```

---

**[← Back to Module 3](../README.md)** | **[Next: Module 3 Quiz →](../quiz_module_3.md)**
