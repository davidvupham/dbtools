# Exercises — 14: Logging

## Learning Objectives

After completing these exercises, you will be able to:
- Configure Python's logging module
- Use appropriate log levels
- Create custom formatters and handlers
- Implement structured logging with structlog
- Use bound loggers for context
- Configure logging for different environments

---

## Exercise 1: Basic Logging Setup (Warm-up)

**Bloom Level**: Remember

Replace the print statements with proper logging:

```python
# Before: Using print statements
def process_order(order_id, items):
    print(f"Starting to process order {order_id}")
    print(f"Processing {len(items)} items")

    for item in items:
        print(f"  Processing item: {item}")

    print(f"Order {order_id} completed")
    return {"order_id": order_id, "status": "completed"}

# After: Convert to logging
import logging

# Configure logging (your code here)

def process_order(order_id, items):
    # Use appropriate log levels
    pass

# Test
process_order("ORD-123", ["item1", "item2", "item3"])
```

**Expected Output**:
```
INFO:__main__:Starting to process order ORD-123
DEBUG:__main__:Processing 3 items
DEBUG:__main__:  Processing item: item1
DEBUG:__main__:  Processing item: item2
DEBUG:__main__:  Processing item: item3
INFO:__main__:Order ORD-123 completed
```

---

## Exercise 2: Custom Formatter (Practice)

**Bloom Level**: Apply

Create a custom log format that includes:
- Timestamp (ISO format)
- Log level
- Module name
- Function name
- Line number
- Message

```python
import logging

# Create a custom format
FORMAT = ???

# Configure logging with custom format
logging.basicConfig(???)

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

**Expected Output**:
```
2024-01-15T10:30:45 | INFO     | __main__:main:15 | Application started
2024-01-15T10:30:45 | INFO     | __main__:calculate_total:9 | Starting calculation
2024-01-15T10:30:45 | DEBUG    | __main__:calculate_total:11 | Calculated total: 60
2024-01-15T10:30:45 | INFO     | __main__:main:17 | Final result: 60
```

---

## Exercise 3: Multiple Handlers (Practice)

**Bloom Level**: Apply

Configure logging to output to both console and file with different levels:
- Console: INFO and above (colored if possible)
- File: DEBUG and above (detailed format)

```python
import logging
import sys

def setup_logging(log_file: str = "app.log"):
    """Configure logging with console and file handlers."""
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Console handler - INFO and above
    console_handler = ???

    # File handler - DEBUG and above
    file_handler = ???

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

---

## Exercise 4: Logger Hierarchy (Analyze)

**Bloom Level**: Analyze

Predict the output and explain the logger hierarchy:

```python
import logging

# Configure root logger
logging.basicConfig(level=logging.WARNING, format='%(name)s - %(levelname)s - %(message)s')

# Create loggers
root_logger = logging.getLogger()
app_logger = logging.getLogger('app')
db_logger = logging.getLogger('app.database')
api_logger = logging.getLogger('app.api')

# Set specific levels
app_logger.setLevel(logging.DEBUG)
db_logger.setLevel(logging.ERROR)
# api_logger inherits from app_logger

# Log messages
root_logger.info("Root info")
root_logger.warning("Root warning")
app_logger.debug("App debug")
app_logger.info("App info")
db_logger.debug("DB debug")
db_logger.warning("DB warning")
db_logger.error("DB error")
api_logger.debug("API debug")
api_logger.info("API info")
```

**Questions**:
1. Which messages appear in the output?
2. Why doesn't "Root info" appear?
3. Why doesn't "DB warning" appear?
4. What level does api_logger effectively use?

---

## Exercise 5: Logging Exceptions (Practice)

**Bloom Level**: Apply

Create a function that properly logs exceptions with full tracebacks:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def divide(a, b):
    """Divide a by b with proper error logging."""
    pass

def process_data(data):
    """Process data with comprehensive error logging."""
    pass

# Test
divide(10, 2)   # Should log the result
divide(10, 0)   # Should log the exception

process_data([1, 2, "three", 4])  # Should handle and log the error
```

**Expected behavior**:
- Successful operations logged at DEBUG or INFO
- Exceptions logged at ERROR with full traceback
- Function should handle errors gracefully

---

## Exercise 6: Structured Logging with structlog (Practice)

**Bloom Level**: Apply

Convert traditional logging to structured logging:

```python
# Traditional logging (convert this)
import logging
logger = logging.getLogger(__name__)

def process_payment(user_id, amount, currency):
    logger.info(f"Processing payment of {amount} {currency} for user {user_id}")

    # Validate
    if amount <= 0:
        logger.error(f"Invalid amount {amount} for user {user_id}")
        return False

    # Process
    logger.debug(f"Connecting to payment gateway for user {user_id}")
    transaction_id = "TXN-12345"
    logger.info(f"Payment successful: transaction {transaction_id} for user {user_id}, amount {amount} {currency}")

    return transaction_id
```

Convert to structlog:

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
    # Your implementation using structured logging
    pass

# Test
process_payment(user_id=42, amount=99.99, currency="USD")
process_payment(user_id=43, amount=-10, currency="USD")
```

---

## Exercise 7: Bound Loggers for Request Context (Practice)

**Bloom Level**: Apply

Create a request processing system that maintains context across log calls:

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
    """
    Process a request with full context logging.

    Each log message should include:
    - request_id (generated UUID)
    - user_id
    - action
    """
    # Create bound logger with context
    log = structlog.get_logger()
    # Bind context that persists across all log calls
    # log = log.bind(???)

    log.info("request_started")

    # Validate
    log.debug("validating_request", data_keys=list(data.keys()))

    # Process
    log.info("processing_action")

    # Complete
    log.info("request_completed", success=True)

    return {"status": "ok"}

# Test
process_request(user_id=42, action="update_profile", data={"name": "Alice"})
```

**Expected Output**:
```
2024-01-15T10:30:45 [info] request_started  request_id=abc-123 user_id=42 action=update_profile
2024-01-15T10:30:45 [debug] validating_request  request_id=abc-123 user_id=42 action=update_profile data_keys=['name']
2024-01-15T10:30:45 [info] processing_action  request_id=abc-123 user_id=42 action=update_profile
2024-01-15T10:30:45 [info] request_completed  request_id=abc-123 user_id=42 action=update_profile success=True
```

---

## Exercise 8: Environment-Based Configuration (Challenge)

**Bloom Level**: Create

Create a logging configuration system that adjusts based on environment:

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
    """
    Configure logging based on environment.

    Development:
    - DEBUG level
    - Colored console output
    - Human-readable format

    Staging:
    - INFO level
    - Console + file output
    - Structured JSON format

    Production:
    - WARNING level (INFO for important events)
    - JSON format for log aggregation
    - No console output
    """
    pass

def get_logger(name: str):
    """Get a configured logger."""
    pass

# Test different environments
env = Environment(os.getenv("APP_ENV", "development"))
configure_logging(env)

log = get_logger(__name__)
log.debug("Debug message")
log.info("Info message")
log.warning("Warning message")
log.error("Error message")
```

---

## Exercise 9: Log Filtering (Challenge)

**Bloom Level**: Create

Create a custom log filter that:
1. Redacts sensitive information (passwords, tokens, credit cards)
2. Filters out noisy log messages
3. Adds custom fields to all log records

```python
import logging
import re

class SensitiveDataFilter(logging.Filter):
    """Filter that redacts sensitive data from log messages."""

    PATTERNS = {
        'password': r'password["\']?\s*[:=]\s*["\']?[\w@#$%^&*]+["\']?',
        'token': r'token["\']?\s*[:=]\s*["\']?[\w\-\.]+["\']?',
        'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
        'ssn': r'\b\d{3}[-]?\d{2}[-]?\d{4}\b',
    }

    def filter(self, record):
        # Your implementation
        pass

class NoiseFilter(logging.Filter):
    """Filter out noisy/repetitive log messages."""

    NOISY_PATTERNS = [
        r'heartbeat',
        r'health.?check',
        r'ping',
    ]

    def filter(self, record):
        # Your implementation
        pass

class ContextFilter(logging.Filter):
    """Add custom context to all log records."""

    def __init__(self, app_name: str, version: str):
        super().__init__()
        self.app_name = app_name
        self.version = version

    def filter(self, record):
        # Your implementation
        pass

# Test
logging.basicConfig(
    level=logging.DEBUG,
    format='%(app_name)s v%(version)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.addFilter(SensitiveDataFilter())
logger.addFilter(NoiseFilter())
logger.addFilter(ContextFilter("MyApp", "1.0.0"))

logger.info("User login with password=secret123")  # Should redact password
logger.info("API token: abc123xyz")  # Should redact token
logger.debug("Heartbeat received")  # Should be filtered out
logger.info("Processing order 12345")  # Should pass through
logger.info("Credit card: 4111-1111-1111-1111")  # Should redact
```

---

## Deliverables

Submit your code for all exercises. Include your analysis for Exercise 4.

---

[← Back to Chapter](../14_logging.md) | [View Solutions](../solutions/sol_14_logging.md) | [← Back to Module 2](../README.md)
