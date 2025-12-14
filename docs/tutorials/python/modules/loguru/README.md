# Loguru Tutorial

**Level**: Beginner to Intermediate
**Category**: Logging / Utilities

**Loguru** is a library which aims to make logging in Python enjoyable. It stops the frustration of configuring loggers and provides a modern, feature-rich interface right out of the box.

## 📦 Installation

```bash
pip install loguru
```

## 🚀 Basic Usage

The main concept of Loguru is that there is **one** logger object. You don't need to instantiate it; just import it.

```python
from loguru import logger

logger.debug("That's it, beautiful and colored logging!")
logger.info("If you're using a terminal, you'll see colors.")
logger.warning("And it's really easy to use.")
logger.error("No setup required!")
```

### No more boilerplate

Compare this to the standard `logging` module where you have to get a logger, set a handler, set a formatter, set a level... Loguru handles defaults sensibly.

## ⚙️ Configuration

Loguru defaults to logging to `stderr`. You can add new "sinks" (destinations) using `logger.add()`.

### Logging to a File

```python
from loguru import logger

# Simple file logging
logger.add("file_{time}.log")

# With rotation and retention
logger.add("app.log", rotation="500 MB", retention="10 days")

# Asynchronous logging (great for performance!)
logger.add("async_log.log", enqueue=True)
```

* **Rotation**: Rotate file when it reaches a size, time, etc. (e.g., `"500 MB"`, `"00:00"`, `"1 week"`).
* **Retention**: Cleanup old logs (e.g., `"10 days"`, `"1 month"`).
* **Compression**: Compress old logs (e.g., `"zip"`, `"tar.gz"`).

### Filtering and Levels

You can filter logs or set minimum levels easily.

```python
# Only log ERROR and above to this specific file
logger.add("errors.log", level="ERROR")

# Custom filter function
def my_filter(record):
    return "special" in record["message"]

logger.add("special.log", filter=my_filter)
```

## 🧠 Advanced Features

### Catching Exceptions

The `@logger.catch` decorator is a game-changer. It automatically logs exceptions with a complete traceback (including variable values!).

```python
from loguru import logger

@logger.catch
def my_function(x, y):
    return x / y

my_function(1, 0)
# Automatically logs the ZeroDivisionError with a beautiful traceback
```

### Contextual Logging

Add context to your logs to make debugging easier (especially in multi-threaded/async apps).

```python
logger.add(sys.stderr, format="{time} {level} {message} {extra}")

context_logger = logger.bind(request_id="12345", ip="192.168.0.1")
context_logger.info("Processing request")
# Output will include {'request_id': '12345', 'ip': '192.168.0.1'}
```

### Structured Logging (JSON)

For production systems (like when using ELK stack or Datadog), structured logging is essential.

```python
logger.add("app.json", serialize=True)
```

## ✅ Best Practices

1. **Use `logger.bind` for context**: Pass request IDs, user IDs, or job IDs around using bound loggers.
2. **Don't over-configure in libraries**: If you are writing a library, let the application configure the sink. Loguru works best in applications.
3. **Use `enqueue=True`**: For high-performance applications, use asynchronous logging to avoid blocking the main thread during I/O.
4. **Standardize your format**: Stick to a consistent format across your application.

## ⚠️ Common Pitfalls

* **Conflicting with Standard Logging**: If you use third-party libraries that use standard `logging`, you might want to intercept those logs and route them through Loguru.

    ```python
    import logging
    from loguru import logger

    class InterceptHandler(logging.Handler):
        def emit(self, record):
            # ... implementation to forward to loguru ...
            pass

    logging.basicConfig(handlers=[InterceptHandler()], level=0)
    ```

    *(See the official docs for the full InterceptHandler implementation)*

## 📚 Resources

### Videos

* [Python Logging Made EASY with Loguru](https://www.youtube.com/watch?v=urrfJgHwIJA) by Better Stack
* [Simplified Python Logging with Loguru!](https://www.youtube.com/watch?v=4y_WvXiC0f0) by Better Stack
* [Python - LoGuru](https://www.youtube.com/watch?v=53a7LqHwXw0) by R3ap3rPy

### Courses & Tutorials

* [How to Use Loguru for Simpler Python Logging](https://realpython.com/python-logging-source-code/#how-to-use-loguru-for-simpler-python-logging) (Real Python)
* [A Complete Guide to Logging in Python with Loguru](https://betterstack.com/community/guides/logging/loguru/)
* [Official Loguru Documentation](https://loguru.readthedocs.io/en/stable/index.html) - Highly recommended!

---

**Next Steps**: Try replacing your standard `print` statements or basic `logging` setup with `loguru` in your next script!
