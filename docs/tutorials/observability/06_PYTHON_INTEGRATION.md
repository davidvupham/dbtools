# Part 6: Python Integration

## What You'll Learn

In this part, you'll learn:

- Installing OpenTelemetry for Python
- Auto-instrumentation for popular frameworks
- Manual instrumentation for custom code
- Structured logging with trace context
- Metrics collection and export

---

## Installation

### Core Packages

```bash
# Core SDK
pip install opentelemetry-api opentelemetry-sdk

# OTLP exporter
pip install opentelemetry-exporter-otlp

# Auto-instrumentation
pip install opentelemetry-instrumentation
```

### Framework-Specific Instrumentation

```bash
# Web frameworks
pip install opentelemetry-instrumentation-flask
pip install opentelemetry-instrumentation-fastapi
pip install opentelemetry-instrumentation-django

# HTTP clients
pip install opentelemetry-instrumentation-requests
pip install opentelemetry-instrumentation-httpx
pip install opentelemetry-instrumentation-aiohttp-client

# Databases
pip install opentelemetry-instrumentation-sqlalchemy
pip install opentelemetry-instrumentation-psycopg2
pip install opentelemetry-instrumentation-pymongo
```

---

## Basic Setup

### Initialize OpenTelemetry

```python
# otel_setup.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

def setup_opentelemetry(
    service_name: str = "my-service",
    service_version: str = "1.0.0",
    environment: str = "production",
    collector_endpoint: str = "http://otel-collector:4317"
):
    """Initialize OpenTelemetry with OTLP export."""

    # Define service resource
    resource = Resource.create({
        "service.name": service_name,
        "service.version": service_version,
        "deployment.environment": environment,
    })

    # Create tracer provider
    provider = TracerProvider(resource=resource)

    # Configure OTLP exporter
    otlp_exporter = OTLPSpanExporter(
        endpoint=collector_endpoint,
        insecure=True  # Use TLS in production
    )

    # Add batch processor (improves performance)
    processor = BatchSpanProcessor(otlp_exporter)
    provider.add_span_processor(processor)

    # Set as global tracer provider
    trace.set_tracer_provider(provider)

    print(f"OpenTelemetry initialized for {service_name}")

# Call at application startup
if __name__ == "__main__":
    setup_opentelemetry("user-service", "1.2.0", "production")
```

---

## Auto-Instrumentation

Auto-instrumentation adds tracing to popular libraries without code changes.

### Flask Example

```python
# app.py
from flask import Flask
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from otel_setup import setup_opentelemetry
import requests

# Initialize OpenTelemetry
setup_opentelemetry("flask-app")

# Create Flask app
app = Flask(__name__)

# Auto-instrument Flask (adds spans for all requests)
FlaskInstrumentor().instrument_app(app)

# Auto-instrument requests library
RequestsInstrumentor().instrument()

@app.route('/api/users/<user_id>')
def get_user(user_id):
    # This creates automatic spans for:
    # 1. Incoming HTTP request (Flask)
    # 2. Outgoing HTTP call (requests)

    # External API call - automatically traced!
    response = requests.get(f"https://api.example.com/users/{user_id}")
    return response.json()

if __name__ == '__main__':
    app.run(port=5000)
```

### FastAPI Example

```python
# main.py
from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from otel_setup import setup_opentelemetry
import httpx

# Initialize OpenTelemetry
setup_opentelemetry("fastapi-app")

app = FastAPI()

# Auto-instrument FastAPI
FastAPIInstrumentor.instrument_app(app)

# Auto-instrument httpx
HTTPXClientInstrumentor().instrument()

@app.get("/api/orders/{order_id}")
async def get_order(order_id: str):
    async with httpx.AsyncClient() as client:
        # Automatically traced!
        response = await client.get(f"https://api.example.com/orders/{order_id}")
        return response.json()
```

### SQLAlchemy Example

```python
from sqlalchemy import create_engine
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

# Create engine
engine = create_engine('postgresql://user:pass@localhost/mydb')

# Auto-instrument SQLAlchemy
SQLAlchemyInstrumentor().instrument(engine=engine)

# All queries now create spans automatically!
with engine.connect() as conn:
    result = conn.execute("SELECT * FROM users WHERE id = ?", user_id)
```

---

## Manual Instrumentation

For custom business logic, add manual spans:

### Basic Span Creation

```python
from opentelemetry import trace

# Get a tracer
tracer = trace.get_tracer(__name__)

def process_order(order_id: str, customer_id: str):
    """Process an order with manual tracing."""

    # Create a span for this operation
    with tracer.start_as_current_span("process_order") as span:
        # Add attributes (dimensions for filtering)
        span.set_attribute("order.id", order_id)
        span.set_attribute("customer.id", customer_id)

        try:
            # Business logic with nested spans
            validate_order(order_id)
            charge_customer(customer_id, order_id)
            ship_order(order_id)

            span.set_attribute("order.status", "completed")
            span.set_status(trace.Status(trace.StatusCode.OK))

        except Exception as e:
            # Record exception in span
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            raise

def validate_order(order_id: str):
    """Nested span for validation."""
    with tracer.start_as_current_span("validate_order") as span:
        span.set_attribute("order.id", order_id)
        # Validation logic...

def charge_customer(customer_id: str, order_id: str):
    """Nested span with events."""
    with tracer.start_as_current_span("charge_customer") as span:
        span.set_attribute("customer.id", customer_id)
        span.set_attribute("order.id", order_id)

        # Add event (point-in-time annotation)
        span.add_event("payment_initiated", {
            "payment.method": "credit_card",
            "payment.amount": 99.99
        })

        # Payment logic...

        span.add_event("payment_completed", {
            "payment.transaction_id": "txn_abc123"
        })

def ship_order(order_id: str):
    with tracer.start_as_current_span("ship_order") as span:
        span.set_attribute("order.id", order_id)
        # Shipping logic...
```

### Decorators for Cleaner Code

```python
from functools import wraps
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

def traced(span_name: str = None, attributes: dict = None):
    """Decorator for tracing functions."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            name = span_name or func.__name__
            with tracer.start_as_current_span(name) as span:
                # Add static attributes
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)

                try:
                    result = func(*args, **kwargs)
                    span.set_status(trace.Status(trace.StatusCode.OK))
                    return result
                except Exception as e:
                    span.record_exception(e)
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                    raise
        return wrapper
    return decorator

# Usage
@traced("database_query", attributes={"db.system": "postgresql"})
def query_database(query: str):
    # Database logic...
    pass

@traced()  # Uses function name as span name
def process_batch(items: list):
    for item in items:
        process_item(item)
```

---

## Structured Logging with Trace Context

### JSON Logging with Trace Context

```python
import logging
import json
from datetime import datetime
from opentelemetry import trace

class JSONFormatter(logging.Formatter):
    """JSON formatter that includes trace context."""

    def format(self, record):
        # Get current span context
        span = trace.get_current_span()
        ctx = span.get_span_context()

        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add trace context if available
        if ctx.trace_id != 0:
            log_entry["trace_id"] = format(ctx.trace_id, '032x')
            log_entry["span_id"] = format(ctx.span_id, '016x')

        # Add extra fields
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)

        return json.dumps(log_entry)

def setup_logging():
    """Configure JSON logging with trace context."""
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())

    logging.root.addHandler(handler)
    logging.root.setLevel(logging.INFO)

# Usage
setup_logging()
logger = logging.getLogger(__name__)

with tracer.start_as_current_span("process_request"):
    logger.info("Processing started", extra={"extra_fields": {"user_id": "12345"}})
    # Output:
    # {
    #   "timestamp": "2025-01-15T10:30:45.123Z",
    #   "level": "INFO",
    #   "message": "Processing started",
    #   "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
    #   "span_id": "00f067aa0ba902b7",
    #   "user_id": "12345"
    # }
```

### Using OpenTelemetry Logging Integration

```python
from opentelemetry.instrumentation.logging import LoggingInstrumentor

# Auto-add trace context to all logs
LoggingInstrumentor().instrument(set_logging_format=True)

# Standard logging now includes trace IDs automatically
logger = logging.getLogger(__name__)
logger.info("This log includes trace context automatically")
```

---

## Metrics Collection

### Setting Up Metrics

```python
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

def setup_metrics(collector_endpoint: str = "http://otel-collector:4317"):
    """Initialize OpenTelemetry metrics."""

    exporter = OTLPMetricExporter(
        endpoint=collector_endpoint,
        insecure=True
    )

    reader = PeriodicExportingMetricReader(
        exporter,
        export_interval_millis=60000  # Export every minute
    )

    provider = MeterProvider(metric_readers=[reader])
    metrics.set_meter_provider(provider)
```

### Recording Metrics

```python
from opentelemetry import metrics

meter = metrics.get_meter(__name__)

# Counter (cumulative, only increases)
request_counter = meter.create_counter(
    "http.server.requests",
    description="Total HTTP requests",
    unit="1"
)

# Histogram (distribution of values)
request_duration = meter.create_histogram(
    "http.server.duration",
    description="HTTP request duration",
    unit="ms"
)

# UpDownCounter (can increase or decrease)
active_connections = meter.create_up_down_counter(
    "db.connections.active",
    description="Active database connections",
    unit="1"
)

# Usage in request handler
def handle_request(request):
    start = time.time()

    try:
        # Increment active connections
        active_connections.add(1, {"db.system": "postgresql"})

        response = process_request(request)

        # Record request
        request_counter.add(1, {
            "http.method": request.method,
            "http.status_code": response.status_code,
            "http.route": request.path
        })

        return response

    finally:
        # Record duration
        duration = (time.time() - start) * 1000
        request_duration.record(duration, {
            "http.method": request.method,
            "http.route": request.path
        })

        # Decrement active connections
        active_connections.add(-1, {"db.system": "postgresql"})
```

---

## Context Propagation

### HTTP Propagation

```python
from opentelemetry.propagate import inject, extract

# Outgoing request - inject trace context
def call_external_api(url: str, data: dict):
    with tracer.start_as_current_span("external_api_call") as span:
        span.set_attribute("http.url", url)

        headers = {}
        inject(headers)  # Adds traceparent header

        response = requests.post(url, json=data, headers=headers)
        span.set_attribute("http.status_code", response.status_code)
        return response

# Incoming request - extract trace context
def handle_incoming_request(request):
    # Extract trace context from headers
    ctx = extract(request.headers)

    # Start span with extracted context
    with tracer.start_as_current_span("handle_request", context=ctx) as span:
        span.set_attribute("http.method", request.method)
        return process_request(request)
```

### Kafka Propagation

```python
from opentelemetry.propagate import inject, extract

# Producer - inject context into message headers
def send_to_kafka(topic: str, message: dict):
    with tracer.start_as_current_span("kafka_produce") as span:
        span.set_attribute("messaging.system", "kafka")
        span.set_attribute("messaging.destination", topic)

        headers = {}
        inject(headers)

        producer.send(
            topic,
            value=json.dumps(message).encode(),
            headers=[(k, v.encode()) for k, v in headers.items()]
        )

# Consumer - extract context from message headers
def consume_from_kafka(message):
    headers = dict((k, v.decode()) for k, v in message.headers)
    ctx = extract(headers)

    with tracer.start_as_current_span("kafka_consume", context=ctx) as span:
        span.set_attribute("messaging.system", "kafka")
        data = json.loads(message.value)
        process_message(data)
```

---

## Complete Example: Flask API

```python
# app.py
import logging
import json
import time
from datetime import datetime
from flask import Flask, request, jsonify, g
from opentelemetry import trace, metrics
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
import requests as http_requests

# Setup (from previous examples)
from otel_setup import setup_opentelemetry

setup_opentelemetry("order-service", "1.0.0", "production")

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)
logger = logging.getLogger(__name__)

# Metrics
order_counter = meter.create_counter("orders.created")
order_duration = meter.create_histogram("orders.processing_duration")

@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    duration = (time.time() - g.start_time) * 1000
    order_duration.record(duration, {"http.route": request.path})
    return response

@app.route('/api/orders', methods=['POST'])
def create_order():
    span = trace.get_current_span()
    data = request.json

    try:
        # Add business context to span
        span.set_attribute("customer.id", data.get("customer_id"))
        span.set_attribute("order.items_count", len(data.get("items", [])))

        # Validate order
        with tracer.start_as_current_span("validate_order"):
            if not data.get("customer_id"):
                raise ValueError("customer_id is required")

        # Check inventory (external service)
        with tracer.start_as_current_span("check_inventory") as inv_span:
            inv_response = http_requests.post(
                "http://inventory-service/check",
                json={"items": data.get("items", [])}
            )
            inv_span.set_attribute("inventory.available", inv_response.json().get("available"))

        # Create order
        with tracer.start_as_current_span("save_order"):
            order_id = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            # Save to database...

        span.set_attribute("order.id", order_id)
        order_counter.add(1, {"status": "success"})

        logger.info("Order created", extra={
            "order_id": order_id,
            "customer_id": data.get("customer_id")
        })

        return jsonify({"order_id": order_id}), 201

    except Exception as e:
        order_counter.add(1, {"status": "error"})
        span.record_exception(e)
        logger.error(f"Order creation failed: {e}")
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(port=5000)
```

---

## Summary

| Topic | Key Points |
|-------|------------|
| **Installation** | Core SDK + exporters + instrumentations |
| **Auto-instrumentation** | Zero-code tracing for frameworks |
| **Manual instrumentation** | Spans for custom business logic |
| **Structured logging** | JSON with trace_id/span_id |
| **Metrics** | Counters, histograms, gauges |
| **Context propagation** | inject/extract for cross-service |

### Key Takeaways

1. **Start with auto-instrumentation** - covers most frameworks
2. **Add manual spans** for business-specific operations
3. **Include trace context in logs** for correlation
4. **Use decorators** for cleaner instrumentation
5. **Export via OTLP** to the Collector

---

## What's Next?

Part 7 will cover **Kafka Streaming** patterns for telemetry at scale.

[Continue to Part 7: Kafka Streaming →](07_KAFKA_STREAMING.md)
