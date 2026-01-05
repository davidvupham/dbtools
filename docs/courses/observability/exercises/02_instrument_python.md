# Exercise 2: Instrument a Python Application

## Objective

Add OpenTelemetry instrumentation to a Python Flask application:

- Auto-instrument Flask for request tracing
- Add manual spans for business logic
- Configure structured logging with trace context

## Prerequisites

- Python 3.9+
- OpenTelemetry Collector running (from Exercise 1)

---

## Step 1: Setup Environment

Navigate to the exercise source directory:

```bash
cd src/02_instrument_python
```

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

---

## Step 2: Install Dependencies

Inspect `requirements.txt` to see the necessary packages:

```bash
cat requirements.txt
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Step 3: Inspect the Application

Open `app.py` to review the implementation:

1. **OpenTelemetry Setup**: Initializes the TracerProvider and OTLP exporter.
2. **Structured Logging**: Configures a JSON formatter that includes trace context.
3. **Flask Application**: Includes endpoints with manual instrumentation.

```python
# Excerpt from app.py
def setup_telemetry():
    """Initialize OpenTelemetry with OTLP export."""
    # ... resource creation ...
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
    # ...
```

---

## Step 4: Run the Application

Start the application:

```bash
python app.py
```

The service will start on `http://localhost:5000`.

---

## Step 5: Generate Traffic

You can generate traffic manually using curl, or use the provided traffic generator script.

### Option A: Manual Traffic (curl)

**Create an Order:**

```bash
curl -X POST http://localhost:5000/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "cust_123",
    "items": [
      {"name": "Widget", "price": 29.99},
      {"name": "Gadget", "price": 49.99}
    ]
  }'
```

**Trigger an Error:**

```bash
curl -X POST http://localhost:5000/api/orders \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Option B: Automated Traffic Generator

Open a **new terminal**, activate the virtual environment, and run the generator:

```bash
cd docs/tutorials/observability/exercises/src/02_instrument_python
source venv/bin/activate
python traffic_generator.py
```

This script will simulate multiple users creating orders and fetching status, including occasional errors.

---

## Step 6: View Traces and Logs

### Jaeger (Traces)

1. Open Jaeger UI: <http://localhost:16686>
2. Select "order-service" from the Service dropdown
3. Click "Find Traces"
4. Click on a trace to see:
    - Request span (from Flask instrumentation)
    - Child spans (validate, inventory, payment, save)
    - Span attributes and events
    - Error details for failed requests

### Console Logs

Check the console output of `app.py` for structured logs:

```json
{"timestamp": "2025-01-15T10:30:45.123Z", "level": "INFO", "message": "Creating order for customer cust_123", "trace_id": "abc123...", "span_id": "def456..."}
```

Note how `trace_id` links logs to traces!

---

## Verification Checklist

- [ ] Application starts without errors
- [ ] Can create orders via API
- [ ] Traces appear in Jaeger with nested spans
- [ ] Logs contain trace_id and span_id
- [ ] Error traces show exception details

---

## Challenge Tasks

1. Add a `/api/orders/<id>/status` endpoint with tracing
2. Make an external HTTP call (to httpbin.org) and verify trace propagation
3. Add metrics for request count and duration
4. Implement custom span attributes for business metrics

---

## Next Steps

Move to [Exercise 3: PowerShell Logging](03_powershell_logging.md)
