# Capstone Project: Order Processing System

Build a complete, production-ready order processing system using RabbitMQ.

## Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Order Processing System                               │
│                                                                              │
│  ┌──────────┐     ┌─────────────┐     ┌─────────────────────────────────┐  │
│  │  Order   │────▶│   orders    │────▶│        Order Processor          │  │
│  │   API    │     │  (exchange) │     │  - Validate order               │  │
│  └──────────┘     └─────────────┘     │  - Check inventory              │  │
│                          │            │  - Process payment              │  │
│                          │            └─────────────┬───────────────────┘  │
│                          │                          │                       │
│                          ▼                          ▼                       │
│                   ┌─────────────┐           ┌─────────────┐                │
│                   │notifications│           │   events    │                │
│                   │ (exchange)  │           │ (exchange)  │                │
│                   └──────┬──────┘           └──────┬──────┘                │
│                          │                          │                       │
│          ┌───────────────┼───────────────┐         │                       │
│          ▼               ▼               ▼         ▼                       │
│    ┌──────────┐   ┌──────────┐   ┌──────────┐ ┌──────────┐               │
│    │  Email   │   │   SMS    │   │   Push   │ │ Analytics│               │
│    │ Service  │   │ Service  │   │ Service  │ │ Service  │               │
│    └──────────┘   └──────────┘   └──────────┘ └──────────┘               │
│                                                                              │
│                   ┌─────────────────────────────────────┐                   │
│                   │          Dead Letter Queue          │                   │
│                   │     (failed orders for review)      │                   │
│                   └─────────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Requirements

### Functional requirements

1. **Order Submission**
   - Accept orders via API/CLI
   - Validate order data
   - Acknowledge receipt immediately

2. **Order Processing**
   - Check inventory availability
   - Process payment (simulated)
   - Update order status

3. **Notifications**
   - Send email confirmation
   - Send SMS for shipping updates
   - Push notifications for mobile

4. **Event Broadcasting**
   - Broadcast order events to interested services
   - Analytics service tracks all events

5. **Error Handling**
   - Retry failed operations
   - Dead-letter unprocessable orders
   - Alert on persistent failures

### Technical requirements

1. **Exchanges**
   - `orders` (direct) - Order submission
   - `notifications` (fanout) - Notification broadcasting
   - `events` (topic) - Event streaming
   - `dlx` (direct) - Dead letter handling

2. **Queues**
   - `order_processing` - Main processing queue
   - `email_notifications` - Email service queue
   - `sms_notifications` - SMS service queue
   - `push_notifications` - Push service queue
   - `analytics` - Analytics events
   - `dead_letters` - Failed messages
   - Retry queues with delays

3. **Reliability**
   - Durable queues and persistent messages
   - Manual acknowledgments
   - Publisher confirms
   - Retry with exponential backoff

## Project structure

```
capstone_order_system/
├── config.py                 # Configuration
├── setup_infrastructure.py   # Create exchanges/queues
├── models.py                 # Data models
├── order_api.py              # Order submission API
├── order_processor.py        # Main order processor
├── notification_service.py   # Notification handlers
├── analytics_service.py      # Analytics consumer
├── dead_letter_handler.py    # DLQ processor
├── docker-compose.yml        # RabbitMQ setup
└── README.md                 # Project documentation
```

## Implementation guide

### Step 1: Configuration

```python
# config.py
"""System configuration."""

RABBITMQ_HOST = 'localhost'
RABBITMQ_PORT = 5672
RABBITMQ_USER = 'guest'
RABBITMQ_PASS = 'guest'

# Exchanges
ORDERS_EXCHANGE = 'orders'
NOTIFICATIONS_EXCHANGE = 'notifications'
EVENTS_EXCHANGE = 'events'
DLX_EXCHANGE = 'dlx'

# Queues
ORDER_PROCESSING_QUEUE = 'order_processing'
EMAIL_QUEUE = 'email_notifications'
SMS_QUEUE = 'sms_notifications'
PUSH_QUEUE = 'push_notifications'
ANALYTICS_QUEUE = 'analytics'
DEAD_LETTER_QUEUE = 'dead_letters'

# Retry configuration
RETRY_DELAYS = [5000, 30000, 120000]  # 5s, 30s, 2m
MAX_RETRIES = 3
```

### Step 2: Infrastructure setup

```python
# setup_infrastructure.py
"""Create all exchanges, queues, and bindings."""
import pika
from config import *


def setup():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(RABBITMQ_HOST)
    )
    channel = connection.channel()

    # === Exchanges ===
    channel.exchange_declare(
        exchange=ORDERS_EXCHANGE,
        exchange_type='direct',
        durable=True
    )

    channel.exchange_declare(
        exchange=NOTIFICATIONS_EXCHANGE,
        exchange_type='fanout',
        durable=True
    )

    channel.exchange_declare(
        exchange=EVENTS_EXCHANGE,
        exchange_type='topic',
        durable=True
    )

    channel.exchange_declare(
        exchange=DLX_EXCHANGE,
        exchange_type='direct',
        durable=True
    )

    # === Dead Letter Queue ===
    channel.queue_declare(queue=DEAD_LETTER_QUEUE, durable=True)
    channel.queue_bind(
        exchange=DLX_EXCHANGE,
        queue=DEAD_LETTER_QUEUE,
        routing_key='failed'
    )

    # === Retry Queues ===
    for i, delay in enumerate(RETRY_DELAYS):
        channel.queue_declare(
            queue=f'order_retry_{i}',
            durable=True,
            arguments={
                'x-message-ttl': delay,
                'x-dead-letter-exchange': ORDERS_EXCHANGE,
                'x-dead-letter-routing-key': 'process'
            }
        )

    # === Order Processing Queue ===
    channel.queue_declare(
        queue=ORDER_PROCESSING_QUEUE,
        durable=True,
        arguments={
            'x-dead-letter-exchange': DLX_EXCHANGE,
            'x-dead-letter-routing-key': 'failed'
        }
    )
    channel.queue_bind(
        exchange=ORDERS_EXCHANGE,
        queue=ORDER_PROCESSING_QUEUE,
        routing_key='process'
    )

    # === Notification Queues ===
    for queue in [EMAIL_QUEUE, SMS_QUEUE, PUSH_QUEUE]:
        channel.queue_declare(queue=queue, durable=True)
        channel.queue_bind(exchange=NOTIFICATIONS_EXCHANGE, queue=queue)

    # === Analytics Queue ===
    channel.queue_declare(queue=ANALYTICS_QUEUE, durable=True)
    channel.queue_bind(
        exchange=EVENTS_EXCHANGE,
        queue=ANALYTICS_QUEUE,
        routing_key='#'  # All events
    )

    print("Infrastructure created successfully!")
    connection.close()


if __name__ == '__main__':
    setup()
```

### Step 3: Data models

```python
# models.py
"""Order data models."""
from dataclasses import dataclass, asdict
from typing import List
from enum import Enum
import json
import uuid
from datetime import datetime


class OrderStatus(Enum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    CONFIRMED = 'confirmed'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    FAILED = 'failed'


@dataclass
class OrderItem:
    sku: str
    quantity: int
    price: float


@dataclass
class Order:
    id: str
    customer_id: str
    email: str
    phone: str
    items: List[OrderItem]
    total: float
    status: OrderStatus = OrderStatus.PENDING
    created_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()

    def to_json(self) -> str:
        data = asdict(self)
        data['status'] = self.status.value
        return json.dumps(data)

    @classmethod
    def from_json(cls, json_str: str) -> 'Order':
        data = json.loads(json_str)
        data['status'] = OrderStatus(data['status'])
        data['items'] = [OrderItem(**item) for item in data['items']]
        return cls(**data)


def create_order(customer_id: str, email: str, phone: str, items: List[dict]) -> Order:
    """Factory function to create orders."""
    order_items = [OrderItem(**item) for item in items]
    total = sum(item.quantity * item.price for item in order_items)

    return Order(
        id=str(uuid.uuid4()),
        customer_id=customer_id,
        email=email,
        phone=phone,
        items=order_items,
        total=total
    )
```

### Step 4: Order API

```python
# order_api.py
"""Order submission API."""
import json
import pika
from config import *
from models import create_order


class OrderAPI:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(RABBITMQ_HOST)
        )
        self.channel = self.connection.channel()
        self.channel.confirm_delivery()

    def submit_order(self, customer_id: str, email: str, phone: str, items: list) -> str:
        """Submit a new order for processing."""
        order = create_order(customer_id, email, phone, items)

        self.channel.basic_publish(
            exchange=ORDERS_EXCHANGE,
            routing_key='process',
            body=order.to_json(),
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type='application/json'
            )
        )

        print(f"Order {order.id} submitted")
        return order.id

    def close(self):
        self.connection.close()


# CLI interface
if __name__ == '__main__':
    api = OrderAPI()

    # Submit sample order
    order_id = api.submit_order(
        customer_id='CUST001',
        email='customer@example.com',
        phone='+1234567890',
        items=[
            {'sku': 'WIDGET-01', 'quantity': 2, 'price': 29.99},
            {'sku': 'GADGET-02', 'quantity': 1, 'price': 49.99}
        ]
    )

    print(f"Submitted order: {order_id}")
    api.close()
```

### Step 5: Order processor (skeleton)

```python
# order_processor.py
"""Main order processing service."""
import json
import logging
import pika
from config import *
from models import Order, OrderStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OrderProcessor:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(RABBITMQ_HOST)
        )
        self.channel = self.connection.channel()
        self.channel.basic_qos(prefetch_count=1)

    def process_order(self, order: Order) -> bool:
        """
        Process an order through the pipeline.

        TODO: Implement these steps:
        1. Validate order
        2. Check inventory
        3. Process payment
        4. Update order status
        5. Publish events
        6. Trigger notifications
        """
        logger.info(f"Processing order {order.id}")

        # Step 1: Validate
        if not self._validate_order(order):
            raise ValueError("Invalid order data")

        # Step 2: Check inventory
        if not self._check_inventory(order):
            raise RuntimeError("Insufficient inventory")

        # Step 3: Process payment
        if not self._process_payment(order):
            raise RuntimeError("Payment failed")

        # Step 4: Update status
        order.status = OrderStatus.CONFIRMED

        # Step 5: Publish event
        self._publish_event('order.confirmed', order)

        # Step 6: Send notifications
        self._send_notifications(order)

        logger.info(f"Order {order.id} confirmed")
        return True

    def _validate_order(self, order: Order) -> bool:
        """Validate order data."""
        # TODO: Implement validation
        return True

    def _check_inventory(self, order: Order) -> bool:
        """Check inventory availability."""
        # TODO: Implement inventory check
        return True

    def _process_payment(self, order: Order) -> bool:
        """Process payment."""
        # TODO: Implement payment processing
        return True

    def _publish_event(self, event_type: str, order: Order):
        """Publish order event."""
        self.channel.basic_publish(
            exchange=EVENTS_EXCHANGE,
            routing_key=event_type,
            body=order.to_json(),
            properties=pika.BasicProperties(delivery_mode=2)
        )

    def _send_notifications(self, order: Order):
        """Send notifications via fanout."""
        notification = json.dumps({
            'type': 'order_confirmation',
            'order_id': order.id,
            'email': order.email,
            'phone': order.phone,
            'total': order.total
        })

        self.channel.basic_publish(
            exchange=NOTIFICATIONS_EXCHANGE,
            routing_key='',
            body=notification,
            properties=pika.BasicProperties(delivery_mode=2)
        )

    def callback(self, ch, method, properties, body):
        """Handle incoming orders."""
        headers = properties.headers or {}
        retry_count = headers.get('x-retry-count', 0)

        try:
            order = Order.from_json(body)
            self.process_order(order)
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            logger.error(f"Error processing order: {e}")

            if retry_count < MAX_RETRIES:
                # Retry with delay
                self._retry_order(ch, body, retry_count)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                # Max retries exceeded, dead-letter
                logger.error(f"Max retries exceeded, dead-lettering")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def _retry_order(self, ch, body, retry_count):
        """Send order to retry queue."""
        ch.basic_publish(
            exchange='',
            routing_key=f'order_retry_{retry_count}',
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=2,
                headers={'x-retry-count': retry_count + 1}
            )
        )
        logger.info(f"Scheduled retry {retry_count + 1}/{MAX_RETRIES}")

    def start(self):
        """Start processing orders."""
        self.channel.basic_consume(
            queue=ORDER_PROCESSING_QUEUE,
            on_message_callback=self.callback,
            auto_ack=False
        )

        logger.info("Order Processor started")
        self.channel.start_consuming()


if __name__ == '__main__':
    processor = OrderProcessor()
    processor.start()
```

## Evaluation criteria

| Criteria | Points |
|:---|:---|
| Infrastructure setup correct | 15 |
| Order submission works | 10 |
| Order processing pipeline complete | 20 |
| Retry logic implemented | 15 |
| Dead letter handling works | 10 |
| Notifications broadcast correctly | 10 |
| Events published with proper routing | 10 |
| Error handling and logging | 10 |
| **Total** | **100** |

**Passing score:** 80 points

## Bonus challenges

1. **Add inventory service** - Separate service that manages stock
2. **Add payment service** - RPC call to payment processor
3. **Add order tracking** - Status updates via WebSocket
4. **Add monitoring dashboard** - Prometheus metrics
5. **Add Kubernetes deployment** - Deploy to K8s cluster

## Testing checklist

- [ ] Submit order and verify processing
- [ ] Verify notifications sent to all services
- [ ] Verify events published to analytics
- [ ] Test retry by simulating failures
- [ ] Test dead lettering after max retries
- [ ] Verify messages survive RabbitMQ restart
- [ ] Test with multiple processors (scaling)

## Submission

Submit:
1. All Python source files
2. docker-compose.yml for RabbitMQ
3. README with setup and run instructions
4. Demo video or screenshots showing the system working

---

[← Back to Course Index](../README.md)
