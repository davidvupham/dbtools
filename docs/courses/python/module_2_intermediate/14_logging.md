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
