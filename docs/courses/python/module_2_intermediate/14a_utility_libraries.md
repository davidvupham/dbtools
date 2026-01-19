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

---

## retry - Simple Retry Decorator

[retry](https://github.com/invl/retry) is a simpler alternative to tenacity. When you need basic retry logic without the complexity of exponential backoff configuration.

### Installation

```bash
uv add retry
```

### Basic Usage

```python
from retry import retry

@retry(tries=4, delay=2)
def unstable_task():
    do_something_risky()

# Retries up to 4 times with 2 second delay between attempts
```

### Retry on Specific Exceptions

```python
from retry import retry
import requests

@retry(exceptions=requests.RequestException, tries=3, delay=1)
def fetch_data(url: str):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()
```

### Exponential Backoff

```python
from retry import retry

@retry(tries=5, delay=1, backoff=2)  # 1s, 2s, 4s, 8s delays
def connect_to_service():
    establish_connection()
```

### retry vs tenacity

| Feature | retry | tenacity |
|---------|-------|----------|
| Simplicity | Very simple | More complex |
| Configuration | Decorator args | Composable objects |
| Async support | No | Yes |
| Custom conditions | Limited | Extensive |
| Dependencies | None | None |

**Use retry** for simple scripts where you need basic retry logic.

**Use tenacity** when you need async support, complex retry conditions, or callbacks.

---

## cachetools - In-Memory Caching

[cachetools](https://cachetools.readthedocs.io/) provides in-memory caching with various eviction policies. Unlike diskcache, it's pure memory with no persistence.

### Installation

```bash
uv add cachetools
```

### TTL Cache (Time-To-Live)

Cache items expire after a set time:

```python
from cachetools import TTLCache, cached

# Cache up to 100 items, each expires after 300 seconds
cache = TTLCache(maxsize=100, ttl=300)

@cached(cache)
def get_user_profile(user_id: int) -> dict:
    # Expensive database query
    return fetch_from_database(user_id)

# First call: hits database
profile = get_user_profile(42)

# Second call within 5 minutes: returns cached value
profile = get_user_profile(42)
```

### LRU Cache (Least Recently Used)

```python
from cachetools import LRUCache, cached

# Keep only the 1000 most recently accessed items
cache = LRUCache(maxsize=1000)

@cached(cache)
def expensive_computation(x: int) -> int:
    return x ** x
```

### LFU Cache (Least Frequently Used)

```python
from cachetools import LFUCache, cached

# Evict least frequently accessed items
cache = LFUCache(maxsize=100)

@cached(cache)
def get_config(key: str) -> str:
    return load_config_from_file(key)
```

### Thread-Safe Caching

```python
from cachetools import TTLCache, cached
from threading import Lock

cache = TTLCache(maxsize=100, ttl=60)
lock = Lock()

@cached(cache, lock=lock)
def thread_safe_lookup(key: str) -> str:
    return slow_operation(key)
```

### Manual Cache Operations

```python
from cachetools import TTLCache

cache = TTLCache(maxsize=100, ttl=300)

# Manual operations
cache["key"] = "value"
value = cache.get("key", "default")
del cache["key"]

# Check cache stats
print(f"Items: {len(cache)}")
print(f"Max size: {cache.maxsize}")
```

### cachetools vs diskcache vs functools.lru_cache

| Feature | cachetools | diskcache | lru_cache |
|---------|-----------|-----------|-----------|
| Storage | Memory | Disk | Memory |
| TTL support | Yes | Yes | No |
| Multiple policies | Yes (LRU, LFU, TTL) | Yes | LRU only |
| Thread-safe | Optional | Yes | Yes |
| Survives restart | No | Yes | No |
| External dependency | Yes | Yes | No (stdlib) |

---

## more-itertools - Extended Iteration

[more-itertools](https://more-itertools.readthedocs.io/) extends the standard `itertools` with commonly needed operations for processing sequences, streams, and batches.

### Installation

```bash
uv add more-itertools
```

### Chunking Data

Process large datasets in batches:

```python
from more_itertools import chunked, ichunked

# Split into fixed-size chunks (returns lists)
data = range(10)
for batch in chunked(data, 3):
    print(batch)
# [0, 1, 2]
# [3, 4, 5]
# [6, 7, 8]
# [9]

# Memory-efficient chunking (returns iterators)
for batch in ichunked(large_stream, 1000):
    process_batch(list(batch))
```

### First, Last, and Only

Safe access to sequence elements:

```python
from more_itertools import first, last, only

items = [1, 2, 3]

first(items)              # 1
first([], default=None)   # None (no IndexError)

last(items)               # 3
last([], default=0)       # 0

# only() ensures exactly one item
only([42])                # 42
only([])                  # None
only([1, 2])              # Raises ValueError (too many items)
```

### Sliding Windows

Process overlapping groups:

```python
from more_itertools import sliding_window, pairwise

data = [1, 2, 3, 4, 5]

# Sliding window of size 3
list(sliding_window(data, 3))
# [(1, 2, 3), (2, 3, 4), (3, 4, 5)]

# Pairs (window of 2)
list(pairwise(data))
# [(1, 2), (2, 3), (3, 4), (4, 5)]
```

### Grouping

```python
from more_itertools import grouper, split_at, split_when

# Fixed-size groups with fill value
list(grouper([1, 2, 3, 4, 5], 2, fillvalue=0))
# [(1, 2), (3, 4), (5, 0)]

# Split at a condition
list(split_at([1, 2, 0, 3, 0, 4], lambda x: x == 0))
# [[1, 2], [3], [4]]

# Split when condition becomes true
list(split_when([1, 2, 5, 6, 3, 4], lambda x, y: y < x))
# [[1, 2, 5, 6], [3, 4]]
```

### Flattening

```python
from more_itertools import flatten, collapse

# Flatten one level
nested = [[1, 2], [3, 4], [5]]
list(flatten(nested))  # [1, 2, 3, 4, 5]

# Flatten deeply nested structures
deeply_nested = [[1, [2, 3]], [[4, 5], 6]]
list(collapse(deeply_nested))  # [1, 2, 3, 4, 5, 6]
```

### Unique and Deduplication

```python
from more_itertools import unique_everseen, unique_justseen

# Remove all duplicates (preserves order)
list(unique_everseen([1, 2, 1, 3, 2, 1]))  # [1, 2, 3]

# Remove consecutive duplicates only
list(unique_justseen([1, 1, 2, 2, 1, 1]))  # [1, 2, 1]

# Unique by key
data = [{"name": "Alice"}, {"name": "Bob"}, {"name": "Alice"}]
list(unique_everseen(data, key=lambda x: x["name"]))
# [{"name": "Alice"}, {"name": "Bob"}]
```

### Spy and Peek

Inspect iterators without consuming them:

```python
from more_itertools import spy, peekable

# Peek at first n items
head, iterable = spy(range(10), 3)
print(head)  # [0, 1, 2]
print(list(iterable))  # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] (still complete!)

# Peekable iterator
p = peekable(range(5))
print(p.peek())  # 0 (doesn't consume)
print(next(p))   # 0 (consumes)
print(p.peek())  # 1
```

---

## boltons - The Missing Pieces of Python

[boltons](https://boltons.readthedocs.io/) is a collection of pure-Python utilities that fill gaps in the standard library. Think of it as "batteries included, but actually included."

### Installation

```bash
uv add boltons
```

### OrderedMultiDict (Deterministic Multi-Value Dicts)

Regular dicts can only hold one value per key. OMD handles multiple values while preserving order:

```python
from boltons.dictutils import OMD

# Multiple values per key, order preserved
data = OMD()
data["tag"] = "python"
data["tag"] = "automation"
data["tag"] = "tutorial"

data.getlist("tag")  # ['python', 'automation', 'tutorial']
data["tag"]          # 'python' (first value)

# Great for parsing query strings, HTTP headers, etc.
```

### iterutils - More Iteration Helpers

```python
from boltons.iterutils import remap, get_path

# Deep transformation of nested structures
data = {"users": [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]}

def anonymize(path, key, value):
    if key == "name":
        return key, "REDACTED"
    return key, value

remap(data, visit=anonymize)
# {'users': [{'name': 'REDACTED', 'age': 30}, {'name': 'REDACTED', 'age': 25}]}
```

### get_path - Safe Nested Access

```python
from boltons.iterutils import get_path

data = {"user": {"profile": {"email": "alice@example.com"}}}

get_path(data, ("user", "profile", "email"))           # 'alice@example.com'
get_path(data, ("user", "missing", "key"), default=None)  # None (no KeyError)
```

### cachedproperty

```python
from boltons.cacheutils import cachedproperty

class ExpensiveObject:
    @cachedproperty
    def computed_value(self):
        print("Computing...")
        return sum(range(1000000))

obj = ExpensiveObject()
obj.computed_value  # Prints "Computing...", returns result
obj.computed_value  # Returns cached result (no print)
```

### timeutils

```python
from boltons.timeutils import daterange, relative_time
from datetime import date, datetime

# Iterate over date ranges
for d in daterange(date(2024, 1, 1), date(2024, 1, 5)):
    print(d)  # 2024-01-01, 2024-01-02, 2024-01-03, 2024-01-04

# Human-readable relative times
relative_time(datetime(2024, 1, 1), datetime(2024, 1, 2))  # '1 day'
```

---

## deepdiff - Spot Differences That Matter

[deepdiff](https://zepworks.com/deepdiff/current/) compares Python objects recursively and shows exactly what changed. Essential for config validation, testing, and auditing.

### Installation

```bash
uv add deepdiff
```

### Basic Comparison

```python
from deepdiff import DeepDiff

old = {"name": "Alice", "age": 30, "tags": ["admin"]}
new = {"name": "Alice", "age": 31, "tags": ["admin", "vip"]}

diff = DeepDiff(old, new)
print(diff)
# {'values_changed': {"root['age']": {'new_value': 31, 'old_value': 30}},
#  'iterable_item_added': {"root['tags'][1]": 'vip'}}
```

### Detecting Types of Changes

```python
from deepdiff import DeepDiff

old_config = {"timeout": 30, "retries": 3, "enabled": True}
new_config = {"timeout": 60, "retries": 3, "debug": True}

diff = DeepDiff(old_config, new_config)

# What was added?
diff.get("dictionary_item_added")  # {"root['debug']"}

# What was removed?
diff.get("dictionary_item_removed")  # {"root['enabled']"}

# What values changed?
diff.get("values_changed")  # {"root['timeout']": {'old_value': 30, 'new_value': 60}}
```

### Ignoring Differences

```python
from deepdiff import DeepDiff

old = {"id": 1, "name": "Alice", "updated_at": "2024-01-01"}
new = {"id": 2, "name": "Alice", "updated_at": "2024-01-02"}

# Ignore specific paths
diff = DeepDiff(old, new, exclude_paths=["root['id']", "root['updated_at']"])
print(diff)  # {} (no differences when ignoring id and updated_at)

# Ignore by regex
diff = DeepDiff(old, new, exclude_regex_paths=[r"root\['.*_at'\]"])
```

### Compare with Tolerance

```python
from deepdiff import DeepDiff

old = {"value": 1.0000001}
new = {"value": 1.0000002}

# Exact comparison finds difference
DeepDiff(old, new)  # Shows change

# With tolerance, considers equal
DeepDiff(old, new, significant_digits=5)  # {} (no diff)
```

### Use Cases

- **Config validation**: Ensure deployments don't accidentally change settings
- **API testing**: Compare expected vs actual responses
- **Audit logging**: Track exactly what changed in database records
- **Snapshot testing**: Detect unintended changes in test output

---

## glom - Data Transformation Without Tears

[glom](https://glom.readthedocs.io/) extracts and transforms nested data with readable path specifications. No more chains of `.get()` calls and defensive checks.

### Installation

```bash
uv add glom
```

### Basic Path Access

```python
from glom import glom

data = {"user": {"profile": {"email": "test@example.com"}}}

# Simple path
email = glom(data, "user.profile.email")  # 'test@example.com'

# vs the manual way
email = data.get("user", {}).get("profile", {}).get("email")  # Ugly!
```

### Accessing Lists

```python
from glom import glom

data = {
    "users": [
        {"name": "Alice", "role": "admin"},
        {"name": "Bob", "role": "user"},
    ]
}

# Get all names
names = glom(data, ("users", ["name"]))  # ['Alice', 'Bob']

# Get first user's name
first_name = glom(data, "users.0.name")  # 'Alice'
```

### Default Values

```python
from glom import glom, Coalesce, SKIP

data = {"user": {"name": "Alice"}}

# With default
email = glom(data, "user.email", default=None)  # None (no KeyError)

# Coalesce: try multiple paths
value = glom(data, Coalesce("user.email", "user.backup_email", default="no-email"))
```

### Transformation

```python
from glom import glom, T

data = {"users": [{"name": "alice"}, {"name": "bob"}]}

# Transform during extraction
spec = ("users", [{"name": ("name", T.upper())}])
result = glom(data, spec)
# [{'name': 'ALICE'}, {'name': 'BOB'}]
```

### Complex Restructuring

```python
from glom import glom

api_response = {
    "data": {
        "user": {"firstName": "Alice", "lastName": "Smith"},
        "account": {"balance": 1000, "currency": "USD"}
    }
}

# Restructure to your format
spec = {
    "full_name": ("data.user.firstName", lambda x: x),  # or use Coalesce for combining
    "balance": "data.account.balance",
    "currency": "data.account.currency",
}

result = glom(api_response, spec)
# {'full_name': 'Alice', 'balance': 1000, 'currency': 'USD'}
```

### glom vs Manual Access

```python
# Without glom
def get_user_emails(data):
    emails = []
    if "users" in data and data["users"]:
        for user in data["users"]:
            if "contact" in user and "email" in user["contact"]:
                emails.append(user["contact"]["email"])
    return emails

# With glom
from glom import glom
emails = glom(data, ("users", ["contact.email"]), default=[])
```

---

## filelock - Stop Race Conditions Cold

[filelock](https://py-filelock.readthedocs.io/) provides cross-platform file locking. Essential when multiple processes need to access shared resources.

### Installation

```bash
uv add filelock
```

### Basic Usage

```python
from filelock import FileLock

lock = FileLock("data.lock")

with lock:
    # Only one process can be here at a time
    with open("data.txt", "a") as f:
        f.write("Safe write\n")
```

### Timeout

```python
from filelock import FileLock, Timeout

lock = FileLock("resource.lock")

try:
    with lock.acquire(timeout=10):  # Wait up to 10 seconds
        process_resource()
except Timeout:
    print("Could not acquire lock within 10 seconds")
```

### Non-Blocking Check

```python
from filelock import FileLock

lock = FileLock("task.lock")

# Try to acquire without blocking
if lock.acquire(blocking=False):
    try:
        do_exclusive_work()
    finally:
        lock.release()
else:
    print("Another process is working on this")
```

### Soft vs Hard Locks

```python
from filelock import FileLock, SoftFileLock

# FileLock: Uses OS-level locking (fcntl on Unix, msvcrt on Windows)
# Stronger guarantees, but may not work across all filesystems
hard_lock = FileLock("data.lock")

# SoftFileLock: Uses lock files (works everywhere, including network drives)
# Slightly less reliable, but more portable
soft_lock = SoftFileLock("data.lock")
```

### Common Use Cases

```python
from filelock import FileLock
import json

# Protect shared configuration file
def update_config(key: str, value: str):
    lock = FileLock("config.lock")
    with lock:
        with open("config.json") as f:
            config = json.load(f)
        config[key] = value
        with open("config.json", "w") as f:
            json.dump(config, f)

# Ensure only one instance of a script runs
def singleton_task():
    lock = FileLock("/tmp/my_task.lock")
    try:
        lock.acquire(blocking=False)
    except:
        print("Task already running!")
        return

    try:
        run_task()
    finally:
        lock.release()
```

### When to Use filelock

| Scenario | Use filelock | Alternative |
|----------|-------------|-------------|
| Multiple processes, same file | Yes | - |
| Single process, multiple threads | No | `threading.Lock` |
| Distributed systems | No | Redis/etcd locks |
| Singleton scripts | Yes | - |
| Shared network resources | Yes (SoftFileLock) | - |

---

## Quick Reference

| Library | Purpose | Install |
|---------|---------|---------|
| tenacity | Retry with backoff | `uv add tenacity` |
| retry | Simple retry | `uv add retry` |
| diskcache | Persistent caching | `uv add diskcache` |
| cachetools | In-memory caching | `uv add cachetools` |
| watchdog | File system events | `uv add watchdog` |
| schedule | Task scheduling | `uv add schedule` |
| msgspec | Fast JSON/validation | `uv add msgspec` |
| pluggy | Plugin systems | `uv add pluggy` |
| more-itertools | Extended iteration | `uv add more-itertools` |
| boltons | Missing stdlib utils | `uv add boltons` |
| deepdiff | Object comparison | `uv add deepdiff` |
| glom | Nested data access | `uv add glom` |
| filelock | File locking | `uv add filelock` |
