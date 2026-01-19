# Solutions — 14: Logging

## Key Concepts Demonstrated

- Python logging module configuration
- Log levels and when to use each
- Custom formatters and handlers
- Logger hierarchy and propagation
- Structured logging with structlog
- Bound loggers for context
- Environment-based configuration
- Log filtering and redaction

## Common Mistakes to Avoid

- Using print() instead of logging
- Hardcoding log configuration (use environment variables)
- Logging sensitive data (passwords, tokens, PII)
- Using f-strings in log calls (use lazy formatting)
- Not configuring logging early in application startup
- Over-logging (too much DEBUG in production)

---

## Exercise 1 Solution

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s:%(name)s:%(message)s'
)

logger = logging.getLogger(__name__)

def process_order(order_id, items):
    logger.info(f"Starting to process order {order_id}")
    logger.debug(f"Processing {len(items)} items")

    for item in items:
        logger.debug(f"  Processing item: {item}")

    logger.info(f"Order {order_id} completed")
    return {"order_id": order_id, "status": "completed"}

# Test
process_order("ORD-123", ["item1", "item2", "item3"])
```

**Best practice**: Use lazy formatting for performance:
```python
logger.info("Starting to process order %s", order_id)  # Preferred
logger.info(f"Starting to process order {order_id}")   # Works but less efficient
```

---

## Exercise 2 Solution

```python
import logging

# Create a custom format
FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s"

# Configure logging with custom format
logging.basicConfig(
    level=logging.DEBUG,
    format=FORMAT,
    datefmt="%Y-%m-%dT%H:%M:%S"
)

logger = logging.getLogger(__name__)

def calculate_total(items):
    logger.info("Starting calculation")
    total = sum(items)
    logger.debug(f"Calculated total: {total}")
    return total

def main():
    logger.info("Application started")
    result = calculate_total([10, 20, 30])
    logger.info(f"Final result: {result}")

main()
```

**Output**:
```
2024-01-15T10:30:45 | INFO     | __main__:main:15 | Application started
2024-01-15T10:30:45 | INFO     | __main__:calculate_total:9 | Starting calculation
2024-01-15T10:30:45 | DEBUG    | __main__:calculate_total:11 | Calculated total: 60
2024-01-15T10:30:45 | INFO     | __main__:main:17 | Final result: 60
```

---

## Exercise 3 Solution

```python
import logging
import sys

def setup_logging(log_file: str = "app.log"):
    """Configure logging with console and file handlers."""
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Remove existing handlers
    logger.handlers.clear()

    # Console handler - INFO and above
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_format)

    # File handler - DEBUG and above
    file_handler = logging.FileHandler(log_file, mode='a')
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

# Test
logger = setup_logging()
logger.debug("This goes to file only")
logger.info("This goes to both console and file")
logger.warning("This is a warning")
logger.error("This is an error")
```

**Console Output**:
```
INFO - This goes to both console and file
WARNING - This is a warning
ERROR - This is an error
```

**File Output (app.log)**:
```
2024-01-15 10:30:45 - root - DEBUG - <module>:24 - This goes to file only
2024-01-15 10:30:45 - root - INFO - <module>:25 - This goes to both console and file
2024-01-15 10:30:45 - root - WARNING - <module>:26 - This is a warning
2024-01-15 10:30:45 - root - ERROR - <module>:27 - This is an error
```

---

## Exercise 4 Solution

```python
import logging

logging.basicConfig(level=logging.WARNING, format='%(name)s - %(levelname)s - %(message)s')

root_logger = logging.getLogger()
app_logger = logging.getLogger('app')
db_logger = logging.getLogger('app.database')
api_logger = logging.getLogger('app.api')

app_logger.setLevel(logging.DEBUG)
db_logger.setLevel(logging.ERROR)

root_logger.info("Root info")       # NOT shown - root is WARNING
root_logger.warning("Root warning") # Shown
app_logger.debug("App debug")       # Shown - app is DEBUG
app_logger.info("App info")         # Shown - app is DEBUG
db_logger.debug("DB debug")         # NOT shown - db is ERROR
db_logger.warning("DB warning")     # NOT shown - db is ERROR
db_logger.error("DB error")         # Shown
api_logger.debug("API debug")       # Shown - inherits DEBUG from app
api_logger.info("API info")         # Shown - inherits DEBUG from app
```

**Output**:
```
root - WARNING - Root warning
app - DEBUG - App debug
app - INFO - App info
app.database - ERROR - DB error
app.api - DEBUG - API debug
app.api - INFO - API info
```

**Answers**:

1. **Which messages appear?**
   - Root warning, App debug, App info, DB error, API debug, API info

2. **Why doesn't "Root info" appear?**
   - Root logger level is WARNING, so INFO is filtered out

3. **Why doesn't "DB warning" appear?**
   - db_logger has level ERROR, so WARNING is filtered out

4. **What level does api_logger effectively use?**
   - DEBUG (inherited from parent 'app' logger since no level is set on api_logger)

**Logger Hierarchy**:
```
root (WARNING)
  └── app (DEBUG)
        ├── app.database (ERROR)
        └── app.api (inherits DEBUG from app)
```

---

## Exercise 5 Solution

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def divide(a, b):
    """Divide a by b with proper error logging."""
    logger.debug(f"Dividing {a} by {b}")
    try:
        result = a / b
        logger.info(f"Division result: {a} / {b} = {result}")
        return result
    except ZeroDivisionError:
        logger.error("Division by zero!", exc_info=True)
        return None

def process_data(data):
    """Process data with comprehensive error logging."""
    logger.info(f"Processing {len(data)} items")
    results = []

    for i, item in enumerate(data):
        try:
            # Simulate processing that might fail
            result = item * 2
            results.append(result)
            logger.debug(f"Processed item {i}: {item} -> {result}")
        except TypeError as e:
            logger.warning(
                f"Skipping item {i} due to type error",
                exc_info=True,
                extra={'item': item, 'index': i}
            )
            continue

    logger.info(f"Processing complete: {len(results)}/{len(data)} succeeded")
    return results

# Test
divide(10, 2)
divide(10, 0)
process_data([1, 2, "three", 4])
```

**Output**:
```
2024-01-15 10:30:45 - DEBUG - Dividing 10 by 2
2024-01-15 10:30:45 - INFO - Division result: 10 / 2 = 5.0
2024-01-15 10:30:45 - DEBUG - Dividing 10 by 0
2024-01-15 10:30:45 - ERROR - Division by zero!
Traceback (most recent call last):
  File "...", line 9, in divide
    result = a / b
ZeroDivisionError: division by zero
2024-01-15 10:30:45 - INFO - Processing 4 items
2024-01-15 10:30:45 - DEBUG - Processed item 0: 1 -> 2
2024-01-15 10:30:45 - DEBUG - Processed item 1: 2 -> 4
2024-01-15 10:30:45 - WARNING - Skipping item 2 due to type error
Traceback (most recent call last):
  ...
TypeError: can't multiply sequence by non-int of type 'str'
2024-01-15 10:30:45 - DEBUG - Processed item 3: 4 -> 8
2024-01-15 10:30:45 - INFO - Processing complete: 3/4 succeeded
```

---

## Exercise 6 Solution

```python
import structlog

# Configure structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.dev.ConsoleRenderer()  # Use JSONRenderer for production
    ]
)

log = structlog.get_logger()

def process_payment(user_id, amount, currency):
    # Bind context for all logs in this function
    payment_log = log.bind(user_id=user_id, amount=amount, currency=currency)

    payment_log.info("payment_started")

    # Validate
    if amount <= 0:
        payment_log.error("invalid_amount", reason="Amount must be positive")
        return False

    # Process
    payment_log.debug("connecting_to_gateway")
    transaction_id = "TXN-12345"

    payment_log.info(
        "payment_completed",
        transaction_id=transaction_id,
        status="success"
    )

    return transaction_id

# Test
process_payment(user_id=42, amount=99.99, currency="USD")
print()
process_payment(user_id=43, amount=-10, currency="USD")
```

**Output**:
```
2024-01-15T10:30:45.123456Z [info     ] payment_started                amount=99.99 currency=USD user_id=42
2024-01-15T10:30:45.123457Z [debug    ] connecting_to_gateway          amount=99.99 currency=USD user_id=42
2024-01-15T10:30:45.123458Z [info     ] payment_completed              amount=99.99 currency=USD status=success transaction_id=TXN-12345 user_id=42

2024-01-15T10:30:45.123459Z [info     ] payment_started                amount=-10 currency=USD user_id=43
2024-01-15T10:30:45.123460Z [error    ] invalid_amount                 amount=-10 currency=USD reason=Amount must be positive user_id=43
```

---

## Exercise 7 Solution

```python
import structlog
import uuid

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.dev.ConsoleRenderer()
    ]
)

def process_request(user_id: int, action: str, data: dict):
    """Process a request with full context logging."""
    request_id = str(uuid.uuid4())[:8]

    # Create bound logger with context
    log = structlog.get_logger()
    log = log.bind(
        request_id=request_id,
        user_id=user_id,
        action=action
    )

    log.info("request_started")

    # Validate
    log.debug("validating_request", data_keys=list(data.keys()))

    if not data:
        log.warning("empty_request_data")

    # Process based on action
    if action == "update_profile":
        log.info("updating_profile", fields=list(data.keys()))
    elif action == "delete_account":
        log.warning("account_deletion_requested")

    # Complete
    log.info("request_completed", success=True)

    return {"status": "ok", "request_id": request_id}

# Test
result = process_request(
    user_id=42,
    action="update_profile",
    data={"name": "Alice", "email": "alice@example.com"}
)
print(f"\nResult: {result}")
```

---

## Exercise 8 Solution

```python
import os
import logging
import structlog
from enum import Enum

class Environment(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

def configure_logging(env: Environment):
    """Configure logging based on environment."""

    if env == Environment.DEVELOPMENT:
        # Development: DEBUG, colored console, human-readable
        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.add_log_level,
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.dev.ConsoleRenderer(colors=True)
            ],
            wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
        )

    elif env == Environment.STAGING:
        # Staging: INFO, console + file, JSON format
        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler("staging.log")
            ]
        )

        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.add_log_level,
                structlog.processors.format_exc_info,
                structlog.processors.JSONRenderer()
            ],
            wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
            logger_factory=structlog.stdlib.LoggerFactory(),
        )

    elif env == Environment.PRODUCTION:
        # Production: WARNING+, JSON only, no console
        logging.basicConfig(
            level=logging.WARNING,
            format="%(message)s",
            handlers=[
                logging.FileHandler("production.log")
            ]
        )

        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.add_log_level,
                structlog.processors.format_exc_info,
                structlog.processors.JSONRenderer()
            ],
            wrapper_class=structlog.make_filtering_bound_logger(logging.WARNING),
            logger_factory=structlog.stdlib.LoggerFactory(),
        )

def get_logger(name: str):
    """Get a configured logger."""
    return structlog.get_logger(name)

# Test
if __name__ == "__main__":
    env = Environment(os.getenv("APP_ENV", "development"))
    print(f"Configuring for: {env.value}")
    configure_logging(env)

    log = get_logger(__name__)
    log.debug("Debug message")
    log.info("Info message", key="value")
    log.warning("Warning message")
    log.error("Error message", error_code=500)
```

---

## Exercise 9 Solution

```python
import logging
import re

class SensitiveDataFilter(logging.Filter):
    """Filter that redacts sensitive data from log messages."""

    PATTERNS = {
        'password': (r'password["\']?\s*[:=]\s*["\']?[\w@#$%^&*]+["\']?', 'password=***REDACTED***'),
        'token': (r'token["\']?\s*[:=]\s*["\']?[\w\-\.]+["\']?', 'token=***REDACTED***'),
        'credit_card': (r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '****-****-****-****'),
        'ssn': (r'\b\d{3}[-]?\d{2}[-]?\d{4}\b', '***-**-****'),
        'api_key': (r'api[_-]?key["\']?\s*[:=]\s*["\']?[\w\-]+["\']?', 'api_key=***REDACTED***'),
    }

    def filter(self, record):
        message = record.getMessage()

        for name, (pattern, replacement) in self.PATTERNS.items():
            message = re.sub(pattern, replacement, message, flags=re.IGNORECASE)

        record.msg = message
        record.args = ()  # Clear args since we've already formatted

        return True


class NoiseFilter(logging.Filter):
    """Filter out noisy/repetitive log messages."""

    NOISY_PATTERNS = [
        r'heartbeat',
        r'health.?check',
        r'^ping$',
        r'keep.?alive',
    ]

    def __init__(self):
        super().__init__()
        self._compiled = [re.compile(p, re.IGNORECASE) for p in self.NOISY_PATTERNS]

    def filter(self, record):
        message = record.getMessage()

        for pattern in self._compiled:
            if pattern.search(message):
                return False  # Filter out this record

        return True  # Keep this record


class ContextFilter(logging.Filter):
    """Add custom context to all log records."""

    def __init__(self, app_name: str, version: str):
        super().__init__()
        self.app_name = app_name
        self.version = version

    def filter(self, record):
        record.app_name = self.app_name
        record.version = self.version
        return True


# Test
logging.basicConfig(
    level=logging.DEBUG,
    format='%(app_name)s v%(version)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.addFilter(SensitiveDataFilter())
logger.addFilter(NoiseFilter())
logger.addFilter(ContextFilter("MyApp", "1.0.0"))

logger.info("User login with password=secret123")
logger.info("API token: abc123xyz")
logger.debug("Heartbeat received")  # Filtered out
logger.info("Processing order 12345")
logger.info("Credit card: 4111-1111-1111-1111")
logger.debug("Health check passed")  # Filtered out
logger.warning("SSN provided: 123-45-6789")
```

**Output**:
```
MyApp v1.0.0 - INFO - User login with password=***REDACTED***
MyApp v1.0.0 - INFO - API token=***REDACTED***
MyApp v1.0.0 - INFO - Processing order 12345
MyApp v1.0.0 - INFO - Credit card: ****-****-****-****
MyApp v1.0.0 - WARNING - SSN provided: ***-**-****
```

Note: "Heartbeat received" and "Health check passed" are not shown because they're filtered by NoiseFilter.

---

## Logging Best Practices Summary

| Level | When to Use |
|-------|-------------|
| DEBUG | Detailed diagnostic info (disabled in production) |
| INFO | Key business events, application milestones |
| WARNING | Unexpected but recoverable situations |
| ERROR | Errors that need attention but app continues |
| CRITICAL | Fatal errors, app cannot continue |

| Practice | Good | Bad |
|----------|------|-----|
| Format | `logger.info("User %s", user_id)` | `logger.info(f"User {user_id}")` |
| Sensitive data | Redact passwords, tokens, PII | Log raw credentials |
| Exception logging | `logger.exception("msg")` or `exc_info=True` | Just log the message |
| Configuration | Environment variables, config files | Hardcoded values |
| Production | Structured JSON, appropriate level | DEBUG level, print statements |

---

[← Back to Exercises](../exercises/ex_14_logging.md) | [← Back to Chapter](../14_logging.md) | [← Back to Module 2](../README.md)
