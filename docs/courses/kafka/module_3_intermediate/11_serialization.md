# Lesson 11: Serialization formats

**[← Back to Schema Registry](./10_schema_registry.md)** | **[Next: Exactly-Once Semantics →](./12_exactly_once.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Serialization-blue)

## Overview

Serialization determines how your data is encoded for transmission through Kafka. This lesson provides deep coverage of Avro, Protobuf, and JSON Schema - when to use each, how to implement them, and best practices for production.

**Learning objectives:**
- Compare serialization formats and choose the right one
- Implement Avro serialization with complex schemas
- Use Protobuf for cross-language compatibility
- Apply JSON Schema for readable, debuggable messages

**Prerequisites:** Lesson 10 (Schema Registry)

**Estimated time:** 50 minutes

---

## Table of contents

- [Serialization fundamentals](#serialization-fundamentals)
- [Format comparison](#format-comparison)
- [Apache Avro](#apache-avro)
- [Protocol Buffers](#protocol-buffers)
- [JSON Schema](#json-schema)
- [Choosing a format](#choosing-a-format)
- [Performance benchmarks](#performance-benchmarks)
- [Hands-on exercises](#hands-on-exercises)
- [Key takeaways](#key-takeaways)

---

## Serialization fundamentals

### What is serialization?

Serialization converts in-memory objects to bytes for transmission. Deserialization reverses this process.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SERIALIZATION FLOW                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PRODUCER                                                                   │
│  ────────                                                                   │
│                                                                             │
│  Python Object          Serializer           Kafka Message                  │
│  ┌─────────────┐       ┌──────────┐         ┌─────────────┐                │
│  │ order = {   │       │          │         │ Key: bytes  │                │
│  │  "id": 123, │──────►│  Avro/   │────────►│ Value: bytes│                │
│  │  "amt": 99  │       │  Proto/  │         │ Headers     │                │
│  │ }           │       │  JSON    │         │             │                │
│  └─────────────┘       └──────────┘         └─────────────┘                │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  CONSUMER                                                                   │
│  ────────                                                                   │
│                                                                             │
│  Kafka Message         Deserializer          Python Object                  │
│  ┌─────────────┐       ┌──────────┐         ┌─────────────┐                │
│  │ Key: bytes  │       │          │         │ order = {   │                │
│  │ Value: bytes│──────►│  Avro/   │────────►│  "id": 123, │                │
│  │ Headers     │       │  Proto/  │         │  "amt": 99  │                │
│  │             │       │  JSON    │         │ }           │                │
│  └─────────────┘       └──────────┘         └─────────────┘                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Why schema-based serialization?

| Approach | Pros | Cons |
|----------|------|------|
| **Plain JSON** | Human readable, no schema needed | Large size, no validation, breaking changes |
| **Schema-based** | Compact, validated, evolvable | Requires schema management |

---

## Format comparison

### At a glance

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FORMAT COMPARISON                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                    AVRO          PROTOBUF        JSON SCHEMA                │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  Encoding          Binary         Binary          Text (JSON)               │
│                                                                             │
│  Schema in msg     No (ID only)   No (ID only)    No (ID only)              │
│                                                                             │
│  Human readable    No             No              Yes                       │
│                                                                             │
│  Size              Smallest       Small           Largest                   │
│                                                                             │
│  Speed             Fast           Fastest         Slowest                   │
│                                                                             │
│  Schema evolution  Excellent      Good            Good                      │
│                                                                             │
│  Language support  Good           Excellent       Excellent                 │
│                                                                             │
│  Native Kafka      Best           Good            Good                      │
│                                                                             │
│  Learning curve    Medium         Medium          Low                       │
│                                                                             │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  BEST FOR:                                                                  │
│  Avro      → Kafka-native apps, schema evolution priority                   │
│  Protobuf  → Cross-language services, gRPC integration                      │
│  JSON      → Debugging, gradual migration, web APIs                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Wire format comparison

Same data encoded in each format:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Data: {"user_id": "U123", "name": "Alice", "age": 30, "active": true}     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  JSON (68 bytes):                                                           │
│  {"user_id":"U123","name":"Alice","age":30,"active":true}                   │
│                                                                             │
│  Avro (15 bytes):                                                           │
│  [magic byte][schema_id: 4 bytes][data: 10 bytes]                           │
│  0x00 | 00 00 00 01 | 08 55 31 32 33 0A 41 6C 69 63 65 3C 01               │
│                                                                             │
│  Protobuf (17 bytes):                                                       │
│  [magic byte][schema_id: 4 bytes][data: 12 bytes]                           │
│  0x00 | 00 00 00 01 | 0A 04 55 31 32 33 12 05 41 6C 69 63 65 18 1E 20 01   │
│                                                                             │
│  Size reduction:                                                            │
│  • Avro:     78% smaller than JSON                                          │
│  • Protobuf: 75% smaller than JSON                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Apache Avro

### Avro schema types

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AVRO TYPE SYSTEM                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PRIMITIVE TYPES                                                            │
│  ───────────────                                                            │
│  null      No value                                                         │
│  boolean   true or false                                                    │
│  int       32-bit signed integer                                            │
│  long      64-bit signed integer                                            │
│  float     32-bit IEEE 754 floating-point                                   │
│  double    64-bit IEEE 754 floating-point                                   │
│  bytes     Sequence of bytes                                                │
│  string    Unicode character sequence                                       │
│                                                                             │
│  COMPLEX TYPES                                                              │
│  ─────────────                                                              │
│  record    Named collection of fields                                       │
│  enum      Enumeration of named values                                      │
│  array     Ordered collection of items                                      │
│  map       Key-value pairs (string keys)                                    │
│  union     One of multiple types (e.g., ["null", "string"])                 │
│  fixed     Fixed number of bytes                                            │
│                                                                             │
│  LOGICAL TYPES (overlays on primitives)                                     │
│  ──────────────                                                             │
│  decimal        Arbitrary precision decimal (bytes/fixed)                   │
│  uuid           UUID string                                                 │
│  date           Days since epoch (int)                                      │
│  time-millis    Milliseconds since midnight (int)                           │
│  time-micros    Microseconds since midnight (long)                          │
│  timestamp-millis  Milliseconds since epoch (long)                          │
│  timestamp-micros  Microseconds since epoch (long)                          │
│  duration      Months, days, milliseconds (fixed 12 bytes)                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Complex Avro schema example

```json
{
  "type": "record",
  "name": "Order",
  "namespace": "com.example.orders",
  "doc": "Represents a customer order",
  "fields": [
    {
      "name": "order_id",
      "type": "string",
      "doc": "Unique order identifier"
    },
    {
      "name": "customer",
      "type": {
        "type": "record",
        "name": "Customer",
        "fields": [
          {"name": "id", "type": "string"},
          {"name": "name", "type": "string"},
          {"name": "email", "type": ["null", "string"], "default": null}
        ]
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
            {"name": "name", "type": "string"},
            {"name": "quantity", "type": "int"},
            {"name": "unit_price", "type": {
              "type": "bytes",
              "logicalType": "decimal",
              "precision": 10,
              "scale": 2
            }}
          ]
        }
      }
    },
    {
      "name": "total_amount",
      "type": {
        "type": "bytes",
        "logicalType": "decimal",
        "precision": 10,
        "scale": 2
      }
    },
    {
      "name": "currency",
      "type": {
        "type": "enum",
        "name": "Currency",
        "symbols": ["USD", "EUR", "GBP", "JPY"]
      },
      "default": "USD"
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
      "name": "created_at",
      "type": {
        "type": "long",
        "logicalType": "timestamp-millis"
      }
    },
    {
      "name": "metadata",
      "type": {
        "type": "map",
        "values": "string"
      },
      "default": {}
    },
    {
      "name": "notes",
      "type": ["null", "string"],
      "default": null
    }
  ]
}
```

### Python Avro producer

```python
from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import SerializationContext, MessageField
import json
from decimal import Decimal
from datetime import datetime

# Schema Registry client
schema_registry_conf = {'url': 'http://localhost:8081'}
schema_registry = SchemaRegistryClient(schema_registry_conf)

# Load schema from file
with open('schemas/order.avsc', 'r') as f:
    schema_str = f.read()

def order_to_dict(order, ctx):
    """Convert Order object to dictionary for Avro serialization."""
    return {
        'order_id': order.order_id,
        'customer': {
            'id': order.customer.id,
            'name': order.customer.name,
            'email': order.customer.email
        },
        'items': [
            {
                'product_id': item.product_id,
                'name': item.name,
                'quantity': item.quantity,
                'unit_price': item.unit_price  # Decimal
            }
            for item in order.items
        ],
        'total_amount': order.total_amount,
        'currency': order.currency,
        'status': order.status,
        'created_at': int(order.created_at.timestamp() * 1000),
        'metadata': order.metadata,
        'notes': order.notes
    }

# Create serializer
avro_serializer = AvroSerializer(
    schema_registry,
    schema_str,
    order_to_dict
)

# Producer config
producer = Producer({'bootstrap.servers': 'localhost:9092'})

def produce_order(order):
    """Produce an order to Kafka with Avro serialization."""
    producer.produce(
        topic='orders',
        key=order.order_id.encode('utf-8'),
        value=avro_serializer(
            order,
            SerializationContext('orders', MessageField.VALUE)
        ),
        on_delivery=lambda err, msg: print(f"Delivered: {msg.offset()}" if not err else f"Error: {err}")
    )
    producer.poll(0)

# Example usage
class Customer:
    def __init__(self, id, name, email=None):
        self.id = id
        self.name = name
        self.email = email

class OrderItem:
    def __init__(self, product_id, name, quantity, unit_price):
        self.product_id = product_id
        self.name = name
        self.quantity = quantity
        self.unit_price = unit_price

class Order:
    def __init__(self, order_id, customer, items, total_amount, currency, status):
        self.order_id = order_id
        self.customer = customer
        self.items = items
        self.total_amount = total_amount
        self.currency = currency
        self.status = status
        self.created_at = datetime.now()
        self.metadata = {}
        self.notes = None

# Create and send order
order = Order(
    order_id='ORD-001',
    customer=Customer('CUST-123', 'Alice Smith', 'alice@example.com'),
    items=[
        OrderItem('PROD-1', 'Laptop', 1, Decimal('999.99')),
        OrderItem('PROD-2', 'Mouse', 2, Decimal('29.99'))
    ],
    total_amount=Decimal('1059.97'),
    currency='USD',
    status='PENDING'
)

produce_order(order)
producer.flush()
```

### Python Avro consumer

```python
from confluent_kafka import Consumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField

schema_registry = SchemaRegistryClient({'url': 'http://localhost:8081'})

def dict_to_order(obj, ctx):
    """Convert dictionary from Avro to Order object."""
    if obj is None:
        return None

    return {
        'order_id': obj['order_id'],
        'customer_name': obj['customer']['name'],
        'total': obj['total_amount'],
        'status': obj['status'],
        'item_count': len(obj['items'])
    }

# Deserializer fetches schema from registry automatically
avro_deserializer = AvroDeserializer(
    schema_registry,
    dict_to_order
)

consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'order-processors',
    'auto.offset.reset': 'earliest'
})

consumer.subscribe(['orders'])

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            continue

        order = avro_deserializer(
            msg.value(),
            SerializationContext('orders', MessageField.VALUE)
        )

        print(f"Order {order['order_id']}: {order['customer_name']} - ${order['total']}")
finally:
    consumer.close()
```

---

## Protocol Buffers

### Protobuf schema definition

Create `order.proto`:

```protobuf
syntax = "proto3";

package com.example.orders;

option java_package = "com.example.orders";
option java_multiple_files = true;

import "google/protobuf/timestamp.proto";

message Order {
  string order_id = 1;
  Customer customer = 2;
  repeated OrderItem items = 3;
  string total_amount = 4;  // Use string for decimal precision
  Currency currency = 5;
  OrderStatus status = 6;
  google.protobuf.Timestamp created_at = 7;
  map<string, string> metadata = 8;
  optional string notes = 9;
}

message Customer {
  string id = 1;
  string name = 2;
  optional string email = 3;
}

message OrderItem {
  string product_id = 1;
  string name = 2;
  int32 quantity = 3;
  string unit_price = 4;  // String for decimal
}

enum Currency {
  CURRENCY_UNSPECIFIED = 0;
  USD = 1;
  EUR = 2;
  GBP = 3;
  JPY = 4;
}

enum OrderStatus {
  ORDER_STATUS_UNSPECIFIED = 0;
  PENDING = 1;
  CONFIRMED = 2;
  SHIPPED = 3;
  DELIVERED = 4;
  CANCELLED = 5;
}
```

### Protobuf field numbering rules

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PROTOBUF FIELD NUMBERS                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  RULES:                                                                     │
│  ───────                                                                    │
│  • Field numbers must be unique within a message                            │
│  • Once assigned, NEVER change a field number                               │
│  • Numbers 1-15 use 1 byte (use for frequently accessed fields)             │
│  • Numbers 16-2047 use 2 bytes                                              │
│  • Range 19000-19999 is reserved for Protobuf implementation                │
│                                                                             │
│  EVOLUTION:                                                                 │
│  ──────────                                                                 │
│  ✓ ADD new fields with new numbers                                          │
│  ✓ REMOVE fields (mark as reserved)                                         │
│  ✗ NEVER reuse field numbers                                                │
│  ✗ NEVER change field types                                                 │
│                                                                             │
│  EXAMPLE:                                                                   │
│                                                                             │
│  // Version 1                                                               │
│  message User {                                                             │
│    string name = 1;                                                         │
│    int32 age = 2;                                                           │
│  }                                                                          │
│                                                                             │
│  // Version 2 (removed age, added email)                                    │
│  message User {                                                             │
│    string name = 1;                                                         │
│    reserved 2;           // age removed, number reserved                    │
│    reserved "age";       // name reserved                                   │
│    string email = 3;     // new field, new number                           │
│  }                                                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Python Protobuf producer

```python
from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.protobuf import ProtobufSerializer
from confluent_kafka.serialization import SerializationContext, MessageField

# Import generated protobuf classes
from order_pb2 import Order, Customer, OrderItem, Currency, OrderStatus

from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime

schema_registry = SchemaRegistryClient({'url': 'http://localhost:8081'})

# Create serializer
protobuf_serializer = ProtobufSerializer(
    Order,
    schema_registry,
    {'use.deprecated.format': False}
)

producer = Producer({'bootstrap.servers': 'localhost:9092'})

def produce_order(order_data):
    """Produce an order using Protobuf serialization."""

    # Create Protobuf message
    timestamp = Timestamp()
    timestamp.FromDatetime(datetime.now())

    order = Order(
        order_id=order_data['order_id'],
        customer=Customer(
            id=order_data['customer']['id'],
            name=order_data['customer']['name'],
            email=order_data['customer'].get('email', '')
        ),
        items=[
            OrderItem(
                product_id=item['product_id'],
                name=item['name'],
                quantity=item['quantity'],
                unit_price=str(item['unit_price'])
            )
            for item in order_data['items']
        ],
        total_amount=str(order_data['total_amount']),
        currency=Currency.Value(order_data['currency']),
        status=OrderStatus.Value(order_data['status']),
        created_at=timestamp
    )

    producer.produce(
        topic='orders-proto',
        key=order.order_id.encode('utf-8'),
        value=protobuf_serializer(
            order,
            SerializationContext('orders-proto', MessageField.VALUE)
        )
    )

# Example
produce_order({
    'order_id': 'ORD-002',
    'customer': {'id': 'C-456', 'name': 'Bob', 'email': 'bob@example.com'},
    'items': [{'product_id': 'P-1', 'name': 'Keyboard', 'quantity': 1, 'unit_price': 79.99}],
    'total_amount': 79.99,
    'currency': 'USD',
    'status': 'PENDING'
})

producer.flush()
```

---

## JSON Schema

### JSON Schema definition

Create `order-schema.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://example.com/order.schema.json",
  "title": "Order",
  "description": "A customer order",
  "type": "object",
  "required": ["order_id", "customer", "items", "total_amount", "status"],
  "properties": {
    "order_id": {
      "type": "string",
      "description": "Unique order identifier",
      "pattern": "^ORD-[0-9]+$"
    },
    "customer": {
      "type": "object",
      "required": ["id", "name"],
      "properties": {
        "id": {"type": "string"},
        "name": {"type": "string", "minLength": 1},
        "email": {"type": "string", "format": "email"}
      }
    },
    "items": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["product_id", "name", "quantity", "unit_price"],
        "properties": {
          "product_id": {"type": "string"},
          "name": {"type": "string"},
          "quantity": {"type": "integer", "minimum": 1},
          "unit_price": {"type": "number", "minimum": 0}
        }
      }
    },
    "total_amount": {
      "type": "number",
      "minimum": 0
    },
    "currency": {
      "type": "string",
      "enum": ["USD", "EUR", "GBP", "JPY"],
      "default": "USD"
    },
    "status": {
      "type": "string",
      "enum": ["PENDING", "CONFIRMED", "SHIPPED", "DELIVERED", "CANCELLED"]
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    },
    "metadata": {
      "type": "object",
      "additionalProperties": {"type": "string"},
      "default": {}
    },
    "notes": {
      "type": ["string", "null"],
      "default": null
    }
  }
}
```

### Python JSON Schema producer

```python
from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer
from confluent_kafka.serialization import SerializationContext, MessageField
import json
from datetime import datetime

schema_registry = SchemaRegistryClient({'url': 'http://localhost:8081'})

# Load JSON Schema
with open('schemas/order-schema.json', 'r') as f:
    schema_str = f.read()

json_serializer = JSONSerializer(
    schema_str,
    schema_registry,
    lambda obj, ctx: obj  # Identity function - already a dict
)

producer = Producer({'bootstrap.servers': 'localhost:9092'})

def produce_order(order):
    """Produce order with JSON Schema validation."""

    # Add timestamp if not present
    if 'created_at' not in order:
        order['created_at'] = datetime.now().isoformat()

    producer.produce(
        topic='orders-json',
        key=order['order_id'].encode('utf-8'),
        value=json_serializer(
            order,
            SerializationContext('orders-json', MessageField.VALUE)
        )
    )

# Example - this will be validated against the schema
order = {
    'order_id': 'ORD-003',
    'customer': {
        'id': 'C-789',
        'name': 'Charlie',
        'email': 'charlie@example.com'
    },
    'items': [
        {'product_id': 'P-10', 'name': 'Monitor', 'quantity': 2, 'unit_price': 299.99}
    ],
    'total_amount': 599.98,
    'currency': 'USD',
    'status': 'PENDING'
}

produce_order(order)
producer.flush()

# This would fail validation (invalid email format)
# invalid_order = {
#     'order_id': 'ORD-004',
#     'customer': {'id': 'C-1', 'name': 'Dave', 'email': 'not-an-email'},
#     ...
# }
```

---

## Choosing a format

### Decision matrix

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    WHEN TO USE EACH FORMAT                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  USE AVRO WHEN:                                                             │
│  ──────────────                                                             │
│  ✓ Building Kafka-native applications                                       │
│  ✓ Schema evolution is a priority                                           │
│  ✓ Using Kafka Connect (native Avro support)                                │
│  ✓ Need best compression for high-volume streams                            │
│  ✓ Your team is already familiar with Avro                                  │
│                                                                             │
│  USE PROTOBUF WHEN:                                                         │
│  ──────────────────                                                         │
│  ✓ Integrating with gRPC services                                           │
│  ✓ Cross-language compatibility is critical                                 │
│  ✓ Already using Protobuf in your organization                              │
│  ✓ Need strongly-typed code generation                                      │
│  ✓ Migrating from gRPC to Kafka                                             │
│                                                                             │
│  USE JSON SCHEMA WHEN:                                                      │
│  ─────────────────────                                                      │
│  ✓ Need human-readable messages for debugging                               │
│  ✓ Gradual migration from plain JSON                                        │
│  ✓ Integrating with REST APIs                                               │
│  ✓ Team unfamiliar with binary formats                                      │
│  ✓ Low-volume use cases where size doesn't matter                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Migration strategies

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MIGRATING SERIALIZATION FORMATS                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  OPTION 1: New Topic                                                        │
│  ───────────────────                                                        │
│  1. Create new topic with new format                                        │
│  2. Update producers to write to new topic                                  │
│  3. Update consumers to read from both topics                               │
│  4. Once old topic is drained, remove old consumer logic                    │
│                                                                             │
│  OPTION 2: Dual Write                                                       │
│  ────────────────────                                                       │
│  1. Producer writes to both old and new topics                              │
│  2. Consumers switch to new topic one by one                                │
│  3. Stop writing to old topic when all consumers migrated                   │
│                                                                             │
│  OPTION 3: Header-Based Routing                                             │
│  ────────────────────────────                                               │
│  1. Add header indicating format version                                    │
│  2. Consumer reads header and uses appropriate deserializer                 │
│  3. Gradually migrate producers to new format                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Performance benchmarks

### Benchmark results

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SERIALIZATION BENCHMARKS                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Test: 1 million messages, typical order payload (~500 bytes JSON)          │
│  Hardware: 8-core CPU, 32GB RAM                                             │
│                                                                             │
│  SERIALIZATION TIME (lower is better)                                       │
│  ─────────────────────────────────────                                      │
│  Avro      ████████████████░░░░░░░░░░░░░░░░░░░░░░░░   42ms/1000 msgs       │
│  Protobuf  ████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░   31ms/1000 msgs       │
│  JSON      ████████████████████████████░░░░░░░░░░░░   68ms/1000 msgs       │
│                                                                             │
│  MESSAGE SIZE (lower is better)                                             │
│  ─────────────────────────────                                              │
│  Avro      ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   89 bytes avg         │
│  Protobuf  ██████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   102 bytes avg        │
│  JSON      ████████████████████████████████████████   478 bytes avg        │
│                                                                             │
│  THROUGHPUT (messages/second, higher is better)                             │
│  ──────────────────────────────────────────────                             │
│  Avro      ████████████████████████████████░░░░░░░░   145,000 msg/s        │
│  Protobuf  ████████████████████████████████████████   180,000 msg/s        │
│  JSON      ████████████████████░░░░░░░░░░░░░░░░░░░░   85,000 msg/s         │
│                                                                             │
│  NETWORK BANDWIDTH (for same throughput)                                    │
│  ─────────────────────────────────────                                      │
│  Avro      Uses ~80% less bandwidth than JSON                               │
│  Protobuf  Uses ~78% less bandwidth than JSON                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Hands-on exercises

### Exercise 1: Compare serialization sizes

```python
# exercise_size_comparison.py
import json
from io import BytesIO
import avro.schema
from avro.io import DatumWriter, BinaryEncoder

# Sample data
order = {
    "order_id": "ORD-12345",
    "customer": {
        "id": "CUST-001",
        "name": "Alice Smith",
        "email": "alice@example.com"
    },
    "items": [
        {"product_id": "PROD-1", "name": "Laptop", "quantity": 1, "unit_price": 999.99},
        {"product_id": "PROD-2", "name": "Mouse", "quantity": 2, "unit_price": 29.99}
    ],
    "total_amount": 1059.97,
    "currency": "USD",
    "status": "PENDING"
}

# JSON size
json_bytes = json.dumps(order).encode('utf-8')
print(f"JSON size: {len(json_bytes)} bytes")

# TODO: Add Avro and Protobuf size comparison
# Hint: Use avro-python3 and protobuf libraries
```

### Exercise 2: Schema evolution test

Test backward compatibility by:
1. Register a schema with 3 fields
2. Add an optional field with a default
3. Verify old consumers can still read new messages

### Exercise 3: Error handling

Implement a consumer that handles serialization errors gracefully when messages don't match the expected schema.

---

## Key takeaways

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SERIALIZATION KEY TAKEAWAYS                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ✓ Use Avro for Kafka-native apps with excellent schema evolution          │
│                                                                             │
│  ✓ Use Protobuf for cross-language services and gRPC integration           │
│                                                                             │
│  ✓ Use JSON Schema for debugging and gradual migration from plain JSON     │
│                                                                             │
│  ✓ Binary formats (Avro/Protobuf) reduce message size by 75-80%            │
│                                                                             │
│  ✓ Schema ID is embedded in messages - schema fetched from registry        │
│                                                                             │
│  ✓ Always test schema compatibility before deploying changes               │
│                                                                             │
│  ✓ Consider migration strategy when changing formats                       │
│                                                                             │
│  ✓ Match format choice to your team's expertise and ecosystem              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

**[← Back to Schema Registry](./10_schema_registry.md)** | **[Next: Exactly-Once Semantics →](./12_exactly_once.md)**

[↑ Back to Top](#lesson-11-serialization-formats)
