# Logging

## Why Logging?

Printing to the console (`print()`) is not enough for production applications. You need:

* **Levels**: Info, Warning, Error.
* **Destinations**: File, Console, Cloud.
* **Format**: Timestamps, module names.

## Basic Usage

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Starting app...")
logger.warning("Disk space low")
logger.error("Database connection failed")
```

## Configuration

```python
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Best Practices

1. **Use `__name__`**: `logger = logging.getLogger(__name__)` ensures the logger name matches the module.
2. **Lazy Formatting**: Use `logger.info("User %s", name)` instead of f-strings for performance.
3. **Handlers**: Use specific handlers (FileHandler, StreamHandler) for different outputs.

## structlog - Structured Logging

Traditional logging produces unstructured text that's hard to parse and query. [structlog](https://www.structlog.org/) produces structured, JSON-first logs that integrate with observability tools.

### Installation

```bash
uv add structlog
```

### Basic Usage

```python
import structlog

log = structlog.get_logger()

log.info("job_started", job_id=42, priority="high")
# Output: {"event": "job_started", "job_id": 42, "priority": "high", "timestamp": "..."}
```

### Why Structured Logging?

Traditional logging hides context:

```python
# Traditional - hard to parse
logger.info(f"Processing order {order_id} for user {user_id}")
# Output: "Processing order 12345 for user 789"
```

Structured logging makes data explicit:

```python
# Structured - easy to query
log.info("processing_order", order_id=12345, user_id=789)
# Output: {"event": "processing_order", "order_id": 12345, "user_id": 789}
```

### Bound Loggers (Context)

Add context that persists across log calls:

```python
log = structlog.get_logger()

# Bind context once
log = log.bind(request_id="abc-123", user_id=42)

# All subsequent logs include the bound context
log.info("starting_request")      # includes request_id, user_id
log.info("processing_payment")    # includes request_id, user_id
log.error("payment_failed")       # includes request_id, user_id
```

### Configuration

Configure structlog for development vs production:

```python
import structlog

# Development - human-readable console output
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.dev.ConsoleRenderer()  # Pretty colored output
    ]
)

# Production - JSON for log aggregation
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()  # JSON output
    ]
)
```

### Integration with stdlib logging

structlog can wrap the standard library logger:

```python
import logging
import structlog

# Configure stdlib logging
logging.basicConfig(format="%(message)s", level=logging.INFO)

# Configure structlog to use stdlib
structlog.configure(
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
)

log = structlog.get_logger()
log.info("works_with_stdlib", key="value")
```

### When to Use structlog

| Scenario | Use stdlib logging | Use structlog |
|----------|-------------------|---------------|
| Simple scripts | Yes | No |
| Production services | Maybe | Yes |
| Log aggregation (ELK, Datadog) | No | Yes |
| Debugging complex flows | No | Yes |
| Microservices | No | Yes |

**Use stdlib logging** for simple scripts or when you cannot add dependencies.

**Use structlog** for production services where logs need to be searchable and queryable
