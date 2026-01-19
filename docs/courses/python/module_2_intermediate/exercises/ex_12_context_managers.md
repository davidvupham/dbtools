# Exercises — 12: Context Managers

## Learning Objectives

After completing these exercises, you will be able to:
- Use the `with` statement for resource management
- Create context managers using classes (`__enter__`/`__exit__`)
- Create context managers using `@contextmanager` decorator
- Handle exceptions in context managers
- Nest and combine context managers
- Apply context managers for common patterns

---

## Exercise 1: Basic Context Manager (Warm-up)

**Bloom Level**: Apply

Create a `Timer` context manager that measures block execution time:

```python
import time

class Timer:
    """Context manager that measures execution time."""

    def __enter__(self):
        # Record start time
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Calculate and print elapsed time
        pass

# Test
with Timer() as t:
    time.sleep(1)
    result = sum(range(1000000))
# Output: Elapsed time: 1.0234s

# Also capture the elapsed time
print(f"Block took {t.elapsed:.2f} seconds")
```

---

## Exercise 2: File-like Context Manager (Practice)

**Bloom Level**: Apply

Create a `TempFile` context manager that creates a temporary file and cleans it up:

```python
import os
import tempfile
from pathlib import Path

class TempFile:
    """
    Context manager for temporary files.

    Creates a temp file on enter, deletes it on exit.
    """

    def __init__(self, suffix: str = ".txt", content: str = None):
        self.suffix = suffix
        self.content = content
        self.path = None

    def __enter__(self) -> Path:
        # Create temp file and optionally write content
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Delete the temp file
        pass

# Test
with TempFile(suffix=".json", content='{"key": "value"}') as filepath:
    print(f"Temp file: {filepath}")
    print(f"Content: {filepath.read_text()}")
    # Do something with the file

# File is automatically deleted
print(f"File exists: {filepath.exists()}")  # False
```

---

## Exercise 3: Database Transaction (Practice)

**Bloom Level**: Apply

Create a `Transaction` context manager for database operations:

```python
class MockDatabase:
    """Simulated database for testing."""

    def __init__(self):
        self.data = {}
        self.in_transaction = False

    def begin(self):
        self.in_transaction = True
        self._backup = self.data.copy()
        print("Transaction started")

    def commit(self):
        self.in_transaction = False
        print("Transaction committed")

    def rollback(self):
        self.data = self._backup
        self.in_transaction = False
        print("Transaction rolled back")

    def insert(self, key, value):
        if not self.in_transaction:
            raise RuntimeError("Not in transaction")
        self.data[key] = value

class Transaction:
    """
    Context manager for database transactions.

    Automatically commits on success, rolls back on exception.
    """

    def __init__(self, db: MockDatabase):
        self.db = db

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Commit if no exception, rollback otherwise
        pass

# Test
db = MockDatabase()

# Successful transaction
with Transaction(db):
    db.insert("user1", {"name": "Alice"})
    db.insert("user2", {"name": "Bob"})
print(db.data)  # Has both users

# Failed transaction
try:
    with Transaction(db):
        db.insert("user3", {"name": "Charlie"})
        raise ValueError("Something went wrong!")
except ValueError:
    pass
print(db.data)  # Still only has user1 and user2 (rolled back)
```

---

## Exercise 4: Using @contextmanager (Practice)

**Bloom Level**: Apply

Rewrite the previous context managers using `@contextmanager`:

```python
from contextlib import contextmanager
import time
import tempfile
from pathlib import Path

@contextmanager
def timer():
    """Context manager that measures execution time."""
    pass

@contextmanager
def temp_file(suffix: str = ".txt", content: str = None):
    """Context manager for temporary files."""
    pass

@contextmanager
def change_directory(path: str):
    """Temporarily change working directory."""
    pass

# Test timer
with timer() as t:
    time.sleep(0.5)
print(f"Elapsed: {t['elapsed']:.2f}s")

# Test temp_file
with temp_file(suffix=".txt", content="Hello") as path:
    print(path.read_text())

# Test change_directory
import os
original = os.getcwd()
with change_directory("/tmp"):
    print(f"Now in: {os.getcwd()}")
print(f"Back to: {os.getcwd()}")  # Original directory
```

---

## Exercise 5: Exception Handling (Analyze)

**Bloom Level**: Analyze

Create a `suppress_errors` context manager and analyze exception handling:

```python
from contextlib import contextmanager

@contextmanager
def suppress_errors(*exception_types, log: bool = False):
    """
    Suppress specified exceptions.

    Args:
        *exception_types: Exception types to suppress.
        log: If True, print suppressed exceptions.
    """
    pass

# Test
with suppress_errors(ValueError, TypeError, log=True):
    int("not a number")  # ValueError - suppressed
print("Continues after error")

with suppress_errors(KeyError):
    d = {}
    print(d["missing"])  # KeyError - suppressed

# This should NOT be suppressed
try:
    with suppress_errors(ValueError):
        raise RuntimeError("Different error")
except RuntimeError:
    print("RuntimeError was not suppressed")
```

**Question**: What should `__exit__` return to suppress an exception? What about to propagate it?

---

## Exercise 6: Nested Context Managers (Practice)

**Bloom Level**: Apply

Create context managers that can be combined:

```python
from contextlib import contextmanager, ExitStack

@contextmanager
def log_block(name: str):
    """Log entry and exit from a code block."""
    print(f"Entering {name}")
    try:
        yield
    finally:
        print(f"Exiting {name}")

@contextmanager
def acquire_lock(name: str):
    """Simulate acquiring a lock."""
    print(f"Acquiring lock: {name}")
    try:
        yield name
    finally:
        print(f"Releasing lock: {name}")

# Test nested contexts
with log_block("outer"), log_block("inner"):
    print("Inside both blocks")

# Dynamically combine contexts using ExitStack
resources = ["db", "cache", "queue"]

with ExitStack() as stack:
    locks = [stack.enter_context(acquire_lock(r)) for r in resources]
    print(f"Acquired locks: {locks}")
    # All locks released when exiting
```

---

## Exercise 7: Resource Pool (Challenge)

**Bloom Level**: Create

Create a connection pool with context manager support:

```python
from contextlib import contextmanager
from typing import Generic, TypeVar, Callable
import threading
from queue import Queue, Empty

T = TypeVar('T')

class ResourcePool(Generic[T]):
    """
    A pool of reusable resources.

    Resources are acquired from the pool and returned when done.
    """

    def __init__(
        self,
        factory: Callable[[], T],
        max_size: int = 10,
        timeout: float = 5.0
    ):
        self.factory = factory
        self.max_size = max_size
        self.timeout = timeout
        self._pool: Queue[T] = Queue(maxsize=max_size)
        self._size = 0
        self._lock = threading.Lock()

    def _create_resource(self) -> T:
        """Create a new resource if pool not full."""
        pass

    @contextmanager
    def acquire(self):
        """
        Acquire a resource from the pool.

        Returns resource to pool when context exits.
        """
        pass

    def size(self) -> int:
        """Return current pool size."""
        return self._size

# Test with mock database connections
class MockConnection:
    _counter = 0

    def __init__(self):
        MockConnection._counter += 1
        self.id = MockConnection._counter
        print(f"Creating connection {self.id}")

    def query(self, sql: str) -> str:
        return f"Connection {self.id} executed: {sql}"

# Create pool
pool = ResourcePool(MockConnection, max_size=3)

# Acquire and use connections
with pool.acquire() as conn1:
    print(conn1.query("SELECT 1"))

    with pool.acquire() as conn2:
        print(conn2.query("SELECT 2"))

print(f"Pool size: {pool.size()}")  # 2 (connections returned to pool)

# Same connections reused
with pool.acquire() as conn:
    print(f"Reused connection {conn.id}")
```

---

## Exercise 8: Redirect Output (Challenge)

**Bloom Level**: Create

Create context managers for redirecting stdout/stderr:

```python
from contextlib import contextmanager
import sys
from io import StringIO
from pathlib import Path

@contextmanager
def capture_output():
    """
    Capture stdout and stderr.

    Yields dict with 'stdout' and 'stderr' keys.
    """
    pass

@contextmanager
def redirect_to_file(filepath: Path, mode: str = "w"):
    """Redirect stdout to a file."""
    pass

# Test capture_output
with capture_output() as output:
    print("Hello, stdout!")
    print("Error message", file=sys.stderr)

print(f"Captured stdout: {output['stdout']}")
print(f"Captured stderr: {output['stderr']}")

# Test redirect_to_file
with redirect_to_file(Path("output.txt")):
    print("This goes to file")
    print("So does this")

print(Path("output.txt").read_text())
Path("output.txt").unlink()  # Cleanup
```

---

## Deliverables

Submit your code for all exercises. Include your answer to the question in Exercise 5.

---

[← Back to Chapter](../12_context_managers.md) | [View Solutions](../solutions/sol_12_context_managers.md) | [← Back to Module 2](../README.md)
