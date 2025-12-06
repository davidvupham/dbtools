import logging
import json
import time
from datetime import datetime
from flask import Flask, request, jsonify

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

# ============================================
# 1. OpenTelemetry Setup
# ============================================


def setup_telemetry():
    """Initialize OpenTelemetry with OTLP export."""

    resource = Resource.create(
        {
            "service.name": "order-service",
            "service.version": "1.0.0",
            "deployment.environment": "development",
        }
    )

    provider = TracerProvider(resource=resource)

    exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)

    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    print("OpenTelemetry initialized")


# ============================================
# 2. Structured Logging
# ============================================


class JSONFormatter(logging.Formatter):
    """JSON formatter with trace context."""

    def format(self, record):
        span = trace.get_current_span()
        ctx = span.get_span_context()

        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }

        if ctx.trace_id != 0:
            log_entry["trace_id"] = format(ctx.trace_id, "032x")
            log_entry["span_id"] = format(ctx.span_id, "016x")

        return json.dumps(log_entry)


def setup_logging():
    """Configure structured JSON logging."""
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logging.root.addHandler(handler)
    logging.root.setLevel(logging.INFO)


# ============================================
# 3. Flask Application
# ============================================

app = Flask(__name__)
tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)


@app.route("/health")
def health():
    return jsonify({"status": "healthy"})


@app.route("/api/orders", methods=["POST"])
def create_order():
    """Create a new order with tracing."""

    data = request.json or {}
    span = trace.get_current_span()

    # Add business context to span
    span.set_attribute("order.customer_id", data.get("customer_id", "unknown"))
    span.set_attribute("order.items_count", len(data.get("items", [])))

    logger.info(f"Creating order for customer {data.get('customer_id')}")

    try:
        # Step 1: Validate order
        with tracer.start_as_current_span("validate_order") as validate_span:
            validate_span.set_attribute("order.customer_id", data.get("customer_id"))
            time.sleep(0.05)  # Simulate work

            if not data.get("customer_id"):
                raise ValueError("customer_id is required")

            logger.info("Order validated successfully")

        # Step 2: Check inventory (external call)
        with tracer.start_as_current_span("check_inventory") as inv_span:
            inv_span.set_attribute("inventory.items", len(data.get("items", [])))
            time.sleep(0.1)  # Simulate external call
            logger.info("Inventory checked")

        # Step 3: Process payment
        with tracer.start_as_current_span("process_payment") as pay_span:
            amount = sum(item.get("price", 0) for item in data.get("items", []))
            pay_span.set_attribute("payment.amount", amount)
            pay_span.add_event("payment_initiated", {"amount": amount})

            time.sleep(0.15)  # Simulate payment processing

            pay_span.add_event("payment_completed", {"transaction_id": "txn_123"})
            logger.info(f"Payment processed: ${amount}")

        # Step 4: Create order record
        with tracer.start_as_current_span("save_order"):
            order_id = f"ORD-{int(time.time())}"
            time.sleep(0.02)
            logger.info(f"Order {order_id} created")

        span.set_attribute("order.id", order_id)
        span.set_attribute("order.status", "completed")

        return jsonify({"order_id": order_id, "status": "created"}), 201

    except ValueError as e:
        span.record_exception(e)
        logger.error(f"Validation failed: {e}")
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        span.record_exception(e)
        logger.error(f"Order creation failed: {e}")
        return jsonify({"error": "Internal error"}), 500


@app.route("/api/orders/<order_id>")
def get_order(order_id):
    """Get order by ID with tracing."""

    span = trace.get_current_span()
    span.set_attribute("order.id", order_id)

    logger.info(f"Fetching order {order_id}")

    with tracer.start_as_current_span("database_query") as db_span:
        db_span.set_attribute("db.system", "postgresql")
        db_span.set_attribute("db.operation", "SELECT")
        time.sleep(0.03)  # Simulate DB query

    return jsonify({"order_id": order_id, "status": "completed", "items": []})


# ============================================
# 4. Main Entry Point
# ============================================

if __name__ == "__main__":
    # Initialize telemetry
    setup_telemetry()
    setup_logging()

    # Auto-instrument Flask
    FlaskInstrumentor().instrument_app(app)

    # Auto-instrument requests library
    RequestsInstrumentor().instrument()

    print("Starting Order Service on http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
