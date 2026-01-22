# Lesson 10: Schema Registry

**[← Back to Kafka Connect](./09_kafka_connect.md)** | **[Next: Serialization Formats →](./11_serialization.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Schema_Registry-blue)

## Overview

Schema Registry is a centralized schema management service that enables producers and consumers to agree on data formats. This lesson covers schema management, compatibility, and evolution strategies.

**Learning objectives:**
- Understand why schema management is critical
- Register and manage schemas in Schema Registry
- Implement schema validation in producers and consumers
- Handle schema evolution with compatibility rules

**Prerequisites:** Lesson 09 (Kafka Connect)

**Estimated time:** 45 minutes

---

## Table of contents

- [Why Schema Registry](#why-schema-registry)
- [Architecture](#architecture)
- [Schema formats](#schema-formats)
- [Working with schemas](#working-with-schemas)
- [Schema compatibility](#schema-compatibility)
- [Schema evolution](#schema-evolution)
- [Client integration](#client-integration)
- [Hands-on exercises](#hands-on-exercises)
- [Key takeaways](#key-takeaways)

---

## Why Schema Registry

### The problem without schemas

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    WITHOUT SCHEMA REGISTRY                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Producer v1                              Consumer v1                       │
│  ┌─────────────────┐                     ┌─────────────────┐               │
│  │ {"name": "John"}│────► KAFKA ────────►│ Expects "name"  │ ✓ Works      │
│  └─────────────────┘                     └─────────────────┘               │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  Producer v2 (schema change!)             Consumer v1 (not updated)        │
│  ┌─────────────────────┐                 ┌─────────────────┐               │
│  │ {"full_name":"John"}│────► KAFKA ────►│ Expects "name"  │ ✗ BREAKS!   │
│  └─────────────────────┘                 └─────────────────┘               │
│                                                                             │
│  PROBLEMS:                                                                  │
│  • No validation - bad data gets into Kafka                                 │
│  • No documentation - what fields exist?                                    │
│  • Breaking changes - consumers crash on unexpected data                    │
│  • No evolution strategy - how to change schemas safely?                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### The solution with Schema Registry

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    WITH SCHEMA REGISTRY                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                       SCHEMA REGISTRY                                 │  │
│  │  ┌─────────────────────────────────────────────────────────┐        │  │
│  │  │ Subject: orders-value                                    │        │  │
│  │  │ Version 1: {"name": "string", "amount": "double"}        │        │  │
│  │  │ Version 2: {"name": "string", "amount": "double",        │        │  │
│  │  │             "currency": "string" (default: "USD")}       │        │  │
│  │  └─────────────────────────────────────────────────────────┘        │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                           ▲                    ▲                            │
│                           │                    │                            │
│               1. Register │        3. Fetch   │                            │
│                  Schema   │           Schema  │                            │
│                           │                    │                            │
│  ┌──────────────┐         │                    │         ┌──────────────┐  │
│  │   PRODUCER   │─────────┘                    └─────────│   CONSUMER   │  │
│  │              │                                        │              │  │
│  │ 2. Serialize │──────────────► KAFKA ─────────────────►│ 4. Deserial. │  │
│  │    + Validate│              [schema_id + data]        │   + Validate │  │
│  └──────────────┘                                        └──────────────┘  │
│                                                                             │
│  BENEFITS:                                                                  │
│  • Validation at produce time (reject bad data)                             │
│  • Schema evolution with compatibility checks                               │
│  • Schema documentation and discovery                                       │
│  • Efficient serialization (schema ID only, not full schema)                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SCHEMA REGISTRY ARCHITECTURE                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  CLIENTS                     SCHEMA REGISTRY           KAFKA CLUSTER        │
│  ───────                     ───────────────           ─────────────        │
│                                                                             │
│  ┌──────────┐               ┌────────────────┐        ┌────────────────┐   │
│  │ Producer │◄─────────────►│  HTTP API      │        │  _schemas      │   │
│  │ (Avro)   │   REST API    │  (port 8081)   │◄──────►│  (internal     │   │
│  └──────────┘               │                │        │   topic)       │   │
│                             │  ┌──────────┐  │        │                │   │
│  ┌──────────┐               │  │  Schema  │  │        │  Stores all    │   │
│  │ Consumer │◄─────────────►│  │  Cache   │  │        │  schemas       │   │
│  │ (Avro)   │               │  └──────────┘  │        │                │   │
│  └──────────┘               │                │        └────────────────┘   │
│                             │  ┌──────────┐  │                             │
│  ┌──────────┐               │  │Compat.   │  │                             │
│  │ Connect  │◄─────────────►│  │Checker   │  │                             │
│  └──────────┘               │  └──────────┘  │                             │
│                             └────────────────┘                             │
│                                                                             │
│  SUBJECT NAMING:                                                            │
│  • TopicNameStrategy: <topic>-key, <topic>-value (default)                  │
│  • RecordNameStrategy: <namespace>.<record-name>                            │
│  • TopicRecordNameStrategy: <topic>-<namespace>.<record-name>               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### REST API endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/subjects` | GET | List all subjects |
| `/subjects/{subject}/versions` | GET | List versions for subject |
| `/subjects/{subject}/versions/{version}` | GET | Get specific version |
| `/subjects/{subject}/versions/latest` | GET | Get latest version |
| `/subjects/{subject}/versions` | POST | Register new schema |
| `/subjects/{subject}` | DELETE | Delete subject |
| `/schemas/ids/{id}` | GET | Get schema by global ID |
| `/compatibility/subjects/{subject}/versions/{version}` | POST | Check compatibility |
| `/config` | GET/PUT | Global compatibility level |
| `/config/{subject}` | GET/PUT | Subject compatibility level |

---

## Schema formats

### Supported formats

| Format | Description | Use Case |
|--------|-------------|----------|
| **Avro** | Binary, schema evolution | Default choice, excellent compatibility |
| **Protobuf** | Binary, efficient | Cross-language, gRPC integration |
| **JSON Schema** | Text-based, readable | Debugging, gradual adoption |

### Avro schema example

```json
{
  "type": "record",
  "name": "Order",
  "namespace": "com.example.orders",
  "fields": [
    {
      "name": "order_id",
      "type": "string"
    },
    {
      "name": "customer_id",
      "type": "string"
    },
    {
      "name": "amount",
      "type": "double"
    },
    {
      "name": "currency",
      "type": "string",
      "default": "USD"
    },
    {
      "name": "timestamp",
      "type": {
        "type": "long",
        "logicalType": "timestamp-millis"
      }
    },
    {
      "name": "items",
      "type": {
        "type": "array",
        "items": {
          "type": "record",
          "name": "OrderItem",
          "fields": [
            {"name": "product_id", "type": "string"},
            {"name": "quantity", "type": "int"},
            {"name": "price", "type": "double"}
          ]
        }
      }
    },
    {
      "name": "status",
      "type": {
        "type": "enum",
        "name": "OrderStatus",
        "symbols": ["PENDING", "CONFIRMED", "SHIPPED", "DELIVERED", "CANCELLED"]
      }
    },
    {
      "name": "notes",
      "type": ["null", "string"],
      "default": null
    }
  ]
}
```

---

## Working with schemas

### Register a schema

```bash
# Register Avro schema
curl -X POST http://localhost:8081/subjects/orders-value/versions \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d '{
    "schema": "{\"type\":\"record\",\"name\":\"Order\",\"fields\":[{\"name\":\"order_id\",\"type\":\"string\"},{\"name\":\"amount\",\"type\":\"double\"}]}"
  }'

# Response: {"id": 1}
```

### List and get schemas

```bash
# List all subjects
curl http://localhost:8081/subjects
# ["orders-key", "orders-value", "payments-value"]

# List versions for a subject
curl http://localhost:8081/subjects/orders-value/versions
# [1, 2, 3]

# Get latest schema
curl http://localhost:8081/subjects/orders-value/versions/latest | jq

# Get schema by global ID
curl http://localhost:8081/schemas/ids/1 | jq
```

### Delete schemas

```bash
# Soft delete a version
curl -X DELETE http://localhost:8081/subjects/orders-value/versions/1

# Soft delete all versions
curl -X DELETE http://localhost:8081/subjects/orders-value

# Permanently delete (requires permanent=true)
curl -X DELETE http://localhost:8081/subjects/orders-value?permanent=true
```

---

## Schema compatibility

### Compatibility types

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SCHEMA COMPATIBILITY TYPES                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  BACKWARD (Default)                                                         │
│  ──────────────────                                                         │
│  New schema can read OLD data                                               │
│  Consumer upgrade FIRST, then producer                                      │
│                                                                             │
│  V1 data ──► V2 consumer ✓                                                  │
│                                                                             │
│  ALLOWED: Delete fields (with default), Add optional fields                 │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  FORWARD                                                                    │
│  ────────                                                                   │
│  Old schema can read NEW data                                               │
│  Producer upgrade FIRST, then consumer                                      │
│                                                                             │
│  V2 data ──► V1 consumer ✓                                                  │
│                                                                             │
│  ALLOWED: Add fields (with default), Delete optional fields                 │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  FULL                                                                       │
│  ────                                                                       │
│  Both BACKWARD and FORWARD compatible                                       │
│  Upgrade producer and consumer in any order                                 │
│                                                                             │
│  V1 ←──► V2 ✓ (bidirectional)                                               │
│                                                                             │
│  ALLOWED: Add/delete optional fields with defaults                          │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  NONE                                                                       │
│  ────                                                                       │
│  No compatibility checking (dangerous!)                                     │
│  Breaking changes allowed                                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Transitive compatibility

| Type | Description |
|------|-------------|
| BACKWARD | Compatible with previous version only |
| BACKWARD_TRANSITIVE | Compatible with ALL previous versions |
| FORWARD | Compatible with next version only |
| FORWARD_TRANSITIVE | Compatible with ALL future versions |
| FULL | Both backward and forward (one version) |
| FULL_TRANSITIVE | Both backward and forward (all versions) |

### Configure compatibility

```bash
# Get global compatibility level
curl http://localhost:8081/config
# {"compatibilityLevel": "BACKWARD"}

# Set global compatibility level
curl -X PUT http://localhost:8081/config \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d '{"compatibility": "FULL"}'

# Set subject-specific compatibility
curl -X PUT http://localhost:8081/config/orders-value \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d '{"compatibility": "FULL_TRANSITIVE"}'
```

### Test compatibility before registering

```bash
# Test if new schema is compatible
curl -X POST http://localhost:8081/compatibility/subjects/orders-value/versions/latest \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d '{
    "schema": "{\"type\":\"record\",\"name\":\"Order\",\"fields\":[{\"name\":\"order_id\",\"type\":\"string\"},{\"name\":\"amount\",\"type\":\"double\"},{\"name\":\"currency\",\"type\":\"string\",\"default\":\"USD\"}]}"
  }'

# Response if compatible:
{"is_compatible": true}

# Response if not compatible:
{"is_compatible": false, "messages": ["..."]}
```

---

## Schema evolution

### Safe schema changes

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SAFE SCHEMA EVOLUTION                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  BACKWARD COMPATIBLE CHANGES (default mode):                                │
│  ─────────────────────────────────────────                                  │
│                                                                             │
│  ✓ Add optional field with default                                          │
│    V1: {"name": "string"}                                                   │
│    V2: {"name": "string", "nickname": ["null", "string"], "default": null}  │
│                                                                             │
│  ✓ Delete field (consumers must handle missing field)                       │
│    V1: {"name": "string", "age": "int"}                                     │
│    V2: {"name": "string"}                                                   │
│                                                                             │
│  ✓ Change field to union with null                                          │
│    V1: {"email": "string"}                                                  │
│    V2: {"email": ["null", "string"]}                                        │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  BREAKING CHANGES (require NONE compatibility or new subject):              │
│  ─────────────────────────────────────────────────────────────              │
│                                                                             │
│  ✗ Rename field                                                             │
│    V1: {"name": "string"}                                                   │
│    V2: {"full_name": "string"}  ← OLD CONSUMERS WILL BREAK                  │
│                                                                             │
│  ✗ Change field type                                                        │
│    V1: {"amount": "int"}                                                    │
│    V2: {"amount": "double"}  ← INCOMPATIBLE TYPE CHANGE                     │
│                                                                             │
│  ✗ Add required field without default                                       │
│    V1: {"name": "string"}                                                   │
│    V2: {"name": "string", "email": "string"}  ← OLD DATA MISSING EMAIL     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Evolution example

```json
// Version 1: Initial schema
{
  "type": "record",
  "name": "User",
  "fields": [
    {"name": "id", "type": "string"},
    {"name": "name", "type": "string"}
  ]
}

// Version 2: Add optional field (BACKWARD compatible)
{
  "type": "record",
  "name": "User",
  "fields": [
    {"name": "id", "type": "string"},
    {"name": "name", "type": "string"},
    {"name": "email", "type": ["null", "string"], "default": null}
  ]
}

// Version 3: Add another optional field with string default
{
  "type": "record",
  "name": "User",
  "fields": [
    {"name": "id", "type": "string"},
    {"name": "name", "type": "string"},
    {"name": "email", "type": ["null", "string"], "default": null},
    {"name": "country", "type": "string", "default": "US"}
  ]
}
```

---

## Client integration

### Python producer with Avro

```python
from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import SerializationContext, MessageField

# Schema Registry configuration
schema_registry_conf = {'url': 'http://localhost:8081'}
schema_registry_client = SchemaRegistryClient(schema_registry_conf)

# Define schema
schema_str = """
{
  "type": "record",
  "name": "Order",
  "namespace": "com.example",
  "fields": [
    {"name": "order_id", "type": "string"},
    {"name": "customer_id", "type": "string"},
    {"name": "amount", "type": "double"},
    {"name": "currency", "type": "string", "default": "USD"}
  ]
}
"""

# Create serializer
avro_serializer = AvroSerializer(
    schema_registry_client,
    schema_str,
    lambda obj, ctx: obj  # to_dict function
)

# Producer configuration
producer_conf = {'bootstrap.servers': 'localhost:9092'}
producer = Producer(producer_conf)

def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed: {err}")
    else:
        print(f"Delivered to {msg.topic()} [{msg.partition()}]")

# Produce messages
order = {
    'order_id': 'ORD-001',
    'customer_id': 'CUST-123',
    'amount': 99.99,
    'currency': 'USD'
}

producer.produce(
    topic='orders',
    value=avro_serializer(
        order,
        SerializationContext('orders', MessageField.VALUE)
    ),
    on_delivery=delivery_report
)

producer.flush()
```

### Python consumer with Avro

```python
from confluent_kafka import Consumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField

# Schema Registry client
schema_registry_conf = {'url': 'http://localhost:8081'}
schema_registry_client = SchemaRegistryClient(schema_registry_conf)

# Create deserializer (schema fetched automatically by ID)
avro_deserializer = AvroDeserializer(
    schema_registry_client,
    lambda obj, ctx: obj  # from_dict function
)

# Consumer configuration
consumer_conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'order-consumers',
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(consumer_conf)
consumer.subscribe(['orders'])

try:
    while True:
        msg = consumer.poll(1.0)

        if msg is None:
            continue
        if msg.error():
            continue

        # Deserialize Avro message
        order = avro_deserializer(
            msg.value(),
            SerializationContext('orders', MessageField.VALUE)
        )

        print(f"Order: {order}")

finally:
    consumer.close()
```

---

## Hands-on exercises

### Exercise 1: Register and evolve a schema

```bash
# 1. Register initial schema
curl -X POST http://localhost:8081/subjects/users-value/versions \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d '{
    "schema": "{\"type\":\"record\",\"name\":\"User\",\"fields\":[{\"name\":\"id\",\"type\":\"string\"},{\"name\":\"name\",\"type\":\"string\"}]}"
  }'

# 2. Check current schema
curl http://localhost:8081/subjects/users-value/versions/latest | jq

# 3. Test compatibility of new schema
curl -X POST http://localhost:8081/compatibility/subjects/users-value/versions/latest \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d '{
    "schema": "{\"type\":\"record\",\"name\":\"User\",\"fields\":[{\"name\":\"id\",\"type\":\"string\"},{\"name\":\"name\",\"type\":\"string\"},{\"name\":\"email\",\"type\":[\"null\",\"string\"],\"default\":null}]}"
  }'

# 4. Register evolved schema
curl -X POST http://localhost:8081/subjects/users-value/versions \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d '{
    "schema": "{\"type\":\"record\",\"name\":\"User\",\"fields\":[{\"name\":\"id\",\"type\":\"string\"},{\"name\":\"name\",\"type\":\"string\"},{\"name\":\"email\",\"type\":[\"null\",\"string\"],\"default\":null}]}"
  }'

# 5. List all versions
curl http://localhost:8081/subjects/users-value/versions
```

### Exercise 2: Test breaking changes

Try to register an incompatible schema and observe the error.

---

## Key takeaways

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SCHEMA REGISTRY KEY TAKEAWAYS                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ✓ Schema Registry provides centralized schema management                  │
│                                                                             │
│  ✓ Use Avro for best schema evolution support                              │
│                                                                             │
│  ✓ BACKWARD compatibility is the default - consumers first, then producers │
│                                                                             │
│  ✓ Always add new fields with defaults for backward compatibility          │
│                                                                             │
│  ✓ Test schema compatibility BEFORE registering in production              │
│                                                                             │
│  ✓ Use subject naming conventions consistently                             │
│                                                                             │
│  ✓ Never rename fields - add new field and deprecate old one               │
│                                                                             │
│  ✓ Consider FULL_TRANSITIVE for maximum flexibility                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

**[← Back to Kafka Connect](./09_kafka_connect.md)** | **[Next: Serialization Formats →](./11_serialization.md)**

[↑ Back to Top](#lesson-10-schema-registry)
