# Python Utility Libraries

Production Python applications need more than the standard library. This guide covers battle-tested libraries that solve common problems: retries, caching, file monitoring, scheduling, serialization, and plugin systems.

---

## tenacity - Retry Logic That Works

[tenacity](https://tenacity.readthedocs.io/) provides declarative retry behavior with exponential backoff, jitter, and fine-grained control over when to retry.

### Installation

```bash
uv add tenacity
```

### Basic Usage

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(5), wait=wait_exponential())
def fetch_remote_config():
    return call_flaky_service()
```

This retries up to 5 times with exponential backoff (1s, 2s, 4s, 8s...).

### Retry on Specific Exceptions

```python
from tenacity import retry, retry_if_exception_type
import requests

@retry(retry=retry_if_exception_type(requests.RequestException))
def fetch_data(url: str):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()
```

### Combining Conditions

```python
from tenacity import (
    retry,
    stop_after_attempt,
    stop_after_delay,
    wait_exponential,
    wait_random,
    retry_if_exception_type,
)

@retry(
    stop=(stop_after_attempt(5) | stop_after_delay(30)),  # Stop after 5 tries OR 30 seconds
    wait=wait_exponential(multiplier=1, max=10) + wait_random(0, 2),  # Exp backoff + jitter
    retry=retry_if_exception_type((ConnectionError, TimeoutError)),
)
def resilient_call():
    ...
```

### Callbacks for Logging

```python
from tenacity import retry, before_sleep_log
import logging

logger = logging.getLogger(__name__)

@retry(
    stop=stop_after_attempt(3),
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
def important_operation():
    ...
```

### When to Use tenacity

- API calls to external services
- Database connections
- Any operation that can fail transiently

---

## diskcache - Disk-Backed Caching

[diskcache](https://grantjenks.com/docs/diskcache/) provides a cache that persists to disk. Thread-safe, process-safe, and survives restarts.

### Installation

```bash
uv add diskcache
```

### Basic Usage

```python
from diskcache import Cache

cache = Cache("./cache")

# Store and retrieve
cache["key"] = "value"
print(cache["key"])  # "value"

# Check existence
if "key" in cache:
    print("Found!")

# Delete
del cache["key"]
```

### Memoization Decorator

```python
from diskcache import Cache

cache = Cache("./cache")

@cache.memoize(expire=3600)  # Cache for 1 hour
def expensive_computation(x: int) -> int:
    # Slow calculation...
    return x ** 2

result = expensive_computation(42)  # Computed
result = expensive_computation(42)  # Cached!
```

### Size Limits and Eviction

```python
from diskcache import Cache

# Limit cache to 1GB, evict least-recently-used
cache = Cache("./cache", size_limit=1_000_000_000, eviction_policy="least-recently-used")
```

### Thread and Process Safety

```python
from diskcache import Cache
import threading

cache = Cache("./cache")

def worker(n):
    cache[f"key_{n}"] = n  # Thread-safe!

threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

### When to Use diskcache

| Scenario | Use diskcache | Alternative |
|----------|--------------|-------------|
| Single machine, persistent | Yes | - |
| Distributed systems | No | Redis, Memcached |
| In-memory only | No | `functools.lru_cache` |
| Large cached objects | Yes | - |

---

## watchdog - File System Monitoring

[watchdog](https://pythonhosted.org/watchdog/) monitors file system events (create, modify, delete) without polling.

### Installation

```bash
uv add watchdog
```

### Basic Usage

```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

class Handler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            print(f"File created: {event.src_path}")

    def on_modified(self, event):
        if not event.is_directory:
            print(f"File modified: {event.src_path}")

    def on_deleted(self, event):
        if not event.is_directory:
            print(f"File deleted: {event.src_path}")

# Start watching
observer = Observer()
observer.schedule(Handler(), path="./watched_folder", recursive=True)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
```

### Pattern Matching

```python
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

class CSVHandler(PatternMatchingEventHandler):
    patterns = ["*.csv"]

    def on_created(self, event):
        print(f"New CSV: {event.src_path}")
        process_csv(event.src_path)
```

### Use Cases

- Auto-reload configuration files
- Process incoming files (ETL pipelines)
- Trigger builds on file changes
- Log file monitoring

---

## schedule - Simple Task Scheduling

[schedule](https://schedule.readthedocs.io/) provides human-readable task scheduling in pure Python.

### Installation

```bash
uv add schedule
```

### Basic Usage

```python
import schedule
import time

def job():
    print("Running scheduled task...")

# Schedule examples
schedule.every(10).minutes.do(job)
schedule.every().hour.do(job)
schedule.every().day.at("10:30").do(job)
schedule.every().monday.do(job)
schedule.every().wednesday.at("13:15").do(job)

# Run the scheduler
while True:
    schedule.run_pending()
    time.sleep(1)
```

### Passing Arguments

```python
def greet(name):
    print(f"Hello, {name}!")

schedule.every().day.do(greet, name="World")
```

### One-Time Jobs

```python
def cleanup():
    print("Cleaning up...")
    return schedule.CancelJob  # Remove after running once

schedule.every().day.at("00:00").do(cleanup)
```

### Error Handling

```python
import schedule
import logging

logger = logging.getLogger(__name__)

def safe_job():
    try:
        risky_operation()
    except Exception:
        logger.exception("Job failed")

schedule.every(5).minutes.do(safe_job)
```

### When to Use schedule vs Alternatives

| Tool | Use Case |
|------|----------|
| `schedule` | Simple in-process scheduling |
| `cron` | System-level scheduling |
| `Prefect` | Complex workflows with dependencies |
| `Celery` | Distributed task queues |

---

## msgspec - Fast Serialization

[msgspec](https://jcristharif.com/msgspec/) provides extremely fast JSON/MessagePack serialization with type validation.

### Installation

```bash
uv add msgspec
```

### Basic Usage

```python
import msgspec

class Event(msgspec.Struct):
    id: int
    payload: str

# Encode to JSON
event = Event(id=1, payload="ok")
encoded = msgspec.json.encode(event)
print(encoded)  # b'{"id":1,"payload":"ok"}'

# Decode from JSON
decoded = msgspec.json.decode(encoded, type=Event)
print(decoded)  # Event(id=1, payload='ok')
```

### Validation

msgspec validates types during decoding:

```python
import msgspec

class User(msgspec.Struct):
    name: str
    age: int

# Valid data
msgspec.json.decode(b'{"name": "Alice", "age": 30}', type=User)  # Works

# Invalid data
msgspec.json.decode(b'{"name": "Alice", "age": "thirty"}', type=User)
# Raises msgspec.ValidationError
```

### Optional Fields and Defaults

```python
import msgspec

class Config(msgspec.Struct):
    host: str = "localhost"
    port: int = 8080
    debug: bool = False

config = msgspec.json.decode(b'{"host": "prod.example.com"}', type=Config)
print(config.port)  # 8080 (default)
```

### Performance Comparison

msgspec is significantly faster than alternatives:

| Library | Encode (ops/sec) | Decode (ops/sec) |
|---------|-----------------|-----------------|
| msgspec | 1,000,000+ | 1,000,000+ |
| orjson | 500,000 | 400,000 |
| json | 100,000 | 80,000 |

### When to Use msgspec

- High-throughput APIs
- Data pipelines
- Anywhere JSON performance matters
- When you need validation without Pydantic's overhead

---

## pluggy - Plugin Architecture

[pluggy](https://pluggy.readthedocs.io/) is the plugin system used by pytest. It enables building extensible applications.

### Installation

```bash
uv add pluggy
```

### Core Concepts

1. **Hook specification** - Define what plugins can implement
2. **Hook implementation** - Plugins implement the hooks
3. **Plugin manager** - Coordinates plugins and calls hooks

### Basic Example

```python
import pluggy

# Define the hook specification
hookspec = pluggy.HookspecMarker("myapp")
hookimpl = pluggy.HookimplMarker("myapp")

class MyAppSpec:
    @hookspec
    def process_data(self, data):
        """Process incoming data."""

# Create a plugin
class LoggingPlugin:
    @hookimpl
    def process_data(self, data):
        print(f"Processing: {data}")
        return data.upper()

class ValidationPlugin:
    @hookimpl
    def process_data(self, data):
        if not data:
            raise ValueError("Empty data!")
        return data

# Set up the plugin manager
pm = pluggy.PluginManager("myapp")
pm.add_hookspecs(MyAppSpec)
pm.register(LoggingPlugin())
pm.register(ValidationPlugin())

# Call hooks (all plugins run)
results = pm.hook.process_data(data="hello")
print(results)  # ['HELLO', 'hello']
```

### Hook Call Order

```python
class FirstPlugin:
    @hookimpl(tryfirst=True)  # Run first
    def process_data(self, data):
        return f"first: {data}"

class LastPlugin:
    @hookimpl(trylast=True)  # Run last
    def process_data(self, data):
        return f"last: {data}"
```

### When to Use pluggy

- Building extensible frameworks
- Plugin-based architectures
- When users need to customize behavior without modifying core code
- Test fixtures (like pytest)

---

## Quick Reference

| Library | Purpose | Install |
|---------|---------|---------|
| tenacity | Retry with backoff | `uv add tenacity` |
| diskcache | Persistent caching | `uv add diskcache` |
| watchdog | File system events | `uv add watchdog` |
| schedule | Task scheduling | `uv add schedule` |
| msgspec | Fast JSON/validation | `uv add msgspec` |
| pluggy | Plugin systems | `uv add pluggy` |
