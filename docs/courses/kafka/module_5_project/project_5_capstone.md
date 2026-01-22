# Project 5: Event-Driven Order Processing System

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Status:** Production

![Project](https://img.shields.io/badge/Project-Capstone-red)
![Difficulty](https://img.shields.io/badge/Difficulty-Advanced-red)

## Project overview

Build a complete event-driven e-commerce order processing system that demonstrates mastery of all Kafka concepts covered in this course.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ORDER PROCESSING SYSTEM                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────┐   orders.created   ┌──────────────┐   orders.validated        │
│  │  Order  │─────────────────►  │  Validation  │────────────────────┐      │
│  │  API    │                    │   Service    │                    │      │
│  └─────────┘                    └──────────────┘                    │      │
│                                        │                            │      │
│                                        │ orders.rejected            │      │
│                                        ▼                            │      │
│                                 ┌──────────────┐                    │      │
│                                 │ Notification │                    │      │
│                                 │   Service    │                    │      │
│                                 └──────────────┘                    │      │
│                                        ▲                            ▼      │
│  ┌─────────┐   payments.processed      │            ┌──────────────┐      │
│  │ Payment │◄──────────────────────────┼────────────│   Payment    │      │
│  │ Gateway │                           │            │   Service    │      │
│  └─────────┘                           │            └──────────────┘      │
│                                        │                    │              │
│                                        │    payments.failed │              │
│                                        └────────────────────┘              │
│                                                     │                      │
│                                                     │ payments.completed   │
│                                                     ▼                      │
│  ┌─────────┐   shipments.created       ┌──────────────┐                   │
│  │Warehouse│◄──────────────────────────│  Inventory   │                   │
│  │ System  │                           │   Service    │                   │
│  └─────────┘                           └──────────────┘                   │
│       │                                                                    │
│       │ shipments.dispatched                                               │
│       ▼                                                                    │
│  ┌──────────────┐                      ┌──────────────┐                   │
│  │   Tracking   │─────────────────────►│  Analytics   │                   │
│  │   Service    │   (all events)       │   (ksqlDB)   │                   │
│  └──────────────┘                      └──────────────┘                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Learning objectives

By completing this project, you will demonstrate:

1. **Architecture design** - Event-driven microservices with Kafka
2. **Producer patterns** - Reliable message production with idempotence
3. **Consumer patterns** - Consumer groups, error handling, dead letters
4. **Kafka Connect** - Database integration with CDC
5. **Schema Registry** - Schema evolution and compatibility
6. **Kafka Streams/ksqlDB** - Real-time analytics
7. **Security** - Authentication and authorization
8. **Monitoring** - Observability and alerting

## Requirements

### Functional requirements

| Service | Responsibility | Topics |
|---------|---------------|--------|
| **Order API** | Accept orders, publish events | `orders.created` |
| **Validation** | Validate orders, check inventory | `orders.validated`, `orders.rejected` |
| **Payment** | Process payments | `payments.processed`, `payments.failed` |
| **Inventory** | Reserve stock, create shipments | `inventory.reserved`, `shipments.created` |
| **Notification** | Send customer notifications | Consumes all relevant events |
| **Analytics** | Real-time dashboards | Aggregates all events |

### Technical requirements

| Requirement | Details |
|-------------|---------|
| **Language** | Python (recommended) or Java |
| **Serialization** | Avro with Schema Registry |
| **Exactly-once** | Idempotent producers, transactional where needed |
| **Error handling** | Dead letter queues, retry logic |
| **Monitoring** | Prometheus metrics, Grafana dashboard |
| **Documentation** | API docs, event catalog, runbook |

## System architecture

### Topics

```yaml
# Topic definitions
topics:
  orders.created:
    partitions: 6
    replication: 3
    retention: 7d
    key: order_id

  orders.validated:
    partitions: 6
    replication: 3
    retention: 7d
    key: order_id

  orders.rejected:
    partitions: 3
    replication: 3
    retention: 30d
    key: order_id

  payments.processed:
    partitions: 6
    replication: 3
    retention: 7d
    key: order_id

  payments.failed:
    partitions: 3
    replication: 3
    retention: 30d
    key: order_id

  inventory.reserved:
    partitions: 6
    replication: 3
    retention: 7d
    key: product_id

  shipments.created:
    partitions: 6
    replication: 3
    retention: 30d
    key: order_id

  notifications.outbound:
    partitions: 3
    replication: 3
    retention: 1d
    key: customer_id
```

### Event schemas (Avro)

```json
// Order Created Event
{
  "type": "record",
  "name": "OrderCreated",
  "namespace": "com.tutorial.orders",
  "fields": [
    {"name": "order_id", "type": "string"},
    {"name": "customer_id", "type": "string"},
    {"name": "items", "type": {"type": "array", "items": {
      "type": "record",
      "name": "OrderItem",
      "fields": [
        {"name": "product_id", "type": "string"},
        {"name": "quantity", "type": "int"},
        {"name": "unit_price", "type": {"type": "bytes", "logicalType": "decimal", "precision": 10, "scale": 2}}
      ]
    }}},
    {"name": "total_amount", "type": {"type": "bytes", "logicalType": "decimal", "precision": 10, "scale": 2}},
    {"name": "shipping_address", "type": "string"},
    {"name": "created_at", "type": {"type": "long", "logicalType": "timestamp-millis"}}
  ]
}
```

## Implementation guide

### Phase 1: Foundation (Week 1)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PHASE 1: FOUNDATION                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Tasks:                                                                     │
│  ☐ Set up Kafka cluster with KRaft                                          │
│  ☐ Configure Schema Registry                                                │
│  ☐ Define and register all Avro schemas                                     │
│  ☐ Create topics with appropriate configurations                            │
│  ☐ Implement Order API service                                              │
│  ☐ Write unit tests for Order API                                           │
│                                                                             │
│  Deliverables:                                                              │
│  • Running Kafka cluster                                                    │
│  • All schemas registered                                                   │
│  • Order API producing events                                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Phase 2: Core services (Week 2)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PHASE 2: CORE SERVICES                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Tasks:                                                                     │
│  ☐ Implement Validation service                                             │
│  ☐ Implement Payment service                                                │
│  ☐ Implement Inventory service                                              │
│  ☐ Configure consumer groups                                                │
│  ☐ Add dead letter queue handling                                           │
│  ☐ Write integration tests                                                  │
│                                                                             │
│  Deliverables:                                                              │
│  • All core services running                                                │
│  • End-to-end order flow working                                            │
│  • Error scenarios handled                                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Phase 3: Advanced features (Week 3)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PHASE 3: ADVANCED FEATURES                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Tasks:                                                                     │
│  ☐ Implement Notification service                                           │
│  ☐ Build Analytics with ksqlDB                                              │
│  ☐ Add exactly-once semantics where needed                                  │
│  ☐ Implement schema evolution                                               │
│  ☐ Add Kafka Connect for database sync                                      │
│                                                                             │
│  Deliverables:                                                              │
│  • Real-time notifications                                                  │
│  • Analytics dashboards                                                     │
│  • Database integration                                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Phase 4: Production readiness (Week 4)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PHASE 4: PRODUCTION READINESS                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Tasks:                                                                     │
│  ☐ Configure TLS encryption                                                 │
│  ☐ Set up SASL authentication                                               │
│  ☐ Implement ACLs                                                           │
│  ☐ Add Prometheus metrics                                                   │
│  ☐ Create Grafana dashboards                                                │
│  ☐ Configure alerts                                                         │
│  ☐ Write runbook documentation                                              │
│  ☐ Perform chaos testing                                                    │
│                                                                             │
│  Deliverables:                                                              │
│  • Secured cluster                                                          │
│  • Complete observability                                                   │
│  • Operational documentation                                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Sample code

### Order API (Python)

```python
from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
import json
from datetime import datetime
from decimal import Decimal

class OrderService:
    def __init__(self, config):
        # Schema Registry
        sr_client = SchemaRegistryClient({'url': config['schema.registry.url']})

        # Avro serializer
        self.serializer = AvroSerializer(
            sr_client,
            self._load_schema('order_created.avsc'),
            self._to_dict
        )

        # Producer
        self.producer = Producer({
            'bootstrap.servers': config['bootstrap.servers'],
            'enable.idempotence': True,
            'acks': 'all'
        })

    def create_order(self, order_data):
        """Create and publish a new order."""
        order_id = self._generate_order_id()

        event = {
            'order_id': order_id,
            'customer_id': order_data['customer_id'],
            'items': order_data['items'],
            'total_amount': self._calculate_total(order_data['items']),
            'shipping_address': order_data['shipping_address'],
            'created_at': int(datetime.now().timestamp() * 1000)
        }

        self.producer.produce(
            topic='orders.created',
            key=order_id,
            value=self.serializer(event, None),
            callback=self._delivery_callback
        )

        self.producer.flush()
        return order_id

    def _delivery_callback(self, err, msg):
        if err:
            print(f"Delivery failed: {err}")
            # Handle error: retry, alert, etc.
        else:
            print(f"Order published: {msg.topic()}[{msg.partition()}]@{msg.offset()}")
```

### ksqlDB Analytics

```sql
-- Create stream from orders
CREATE STREAM orders_stream (
    order_id VARCHAR KEY,
    customer_id VARCHAR,
    items ARRAY<STRUCT<product_id VARCHAR, quantity INT, unit_price DECIMAL(10,2)>>,
    total_amount DECIMAL(10,2),
    created_at TIMESTAMP
) WITH (
    KAFKA_TOPIC='orders.created',
    VALUE_FORMAT='AVRO'
);

-- Real-time order metrics (tumbling window)
CREATE TABLE order_metrics AS
SELECT
    TIMESTAMPTOSTRING(WINDOWSTART, 'yyyy-MM-dd HH:mm') AS window_start,
    COUNT(*) AS order_count,
    SUM(total_amount) AS total_revenue,
    AVG(total_amount) AS avg_order_value
FROM orders_stream
WINDOW TUMBLING (SIZE 1 HOUR)
GROUP BY 1
EMIT CHANGES;

-- Top products by quantity sold
CREATE TABLE top_products AS
SELECT
    item->product_id AS product_id,
    SUM(item->quantity) AS total_quantity,
    SUM(item->quantity * item->unit_price) AS total_revenue
FROM orders_stream
CROSS JOIN UNNEST(items) AS item
GROUP BY item->product_id
EMIT CHANGES;
```

## Evaluation rubric

| Criteria | Points | Description |
|----------|--------|-------------|
| **Architecture** | 20 | Clean design, proper separation of concerns |
| **Kafka Patterns** | 20 | Correct use of topics, partitions, keys |
| **Error Handling** | 15 | DLQ, retries, graceful degradation |
| **Schema Management** | 15 | Avro schemas, evolution, compatibility |
| **Security** | 10 | TLS, SASL, ACLs |
| **Monitoring** | 10 | Metrics, dashboards, alerts |
| **Documentation** | 10 | Clear docs, runbooks, API specs |
| **Total** | **100** | |

## Submission checklist

- [ ] All services running and integrated
- [ ] End-to-end order flow working
- [ ] Error scenarios handled (DLQ, retries)
- [ ] Schemas registered and compatible
- [ ] Security configured (TLS, SASL, ACLs)
- [ ] Metrics exposed and dashboards created
- [ ] Documentation complete
- [ ] Chaos test results documented

## Resources

- [Confluent Developer Portal](https://developer.confluent.io/)
- [Kafka Streams Documentation](https://kafka.apache.org/documentation/streams/)
- [ksqlDB Documentation](https://docs.ksqldb.io/)
- [Schema Registry Documentation](https://docs.confluent.io/platform/current/schema-registry/)

---

**Congratulations on completing the Kafka Engineering Course!**

You now have the skills to design, build, and operate event-driven systems with Apache Kafka.
