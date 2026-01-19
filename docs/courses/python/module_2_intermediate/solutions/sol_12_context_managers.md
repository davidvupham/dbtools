# Solutions — 12: Context Managers

## Key Concepts Demonstrated

- Class-based context managers (`__enter__`/`__exit__`)
- `@contextmanager` decorator for simpler syntax
- Exception handling in context managers
- Nested and combined context managers
- `ExitStack` for dynamic context management
- Common patterns: timers, temp files, transactions

## Common Mistakes to Avoid

- Forgetting to return `self` or a value from `__enter__`
- Not handling exceptions in `__exit__`
- Forgetting to `yield` in `@contextmanager` functions
- Not using `finally` to ensure cleanup in `@contextmanager`

---

## Exercise 1 Solution

```python
import time

class Timer:
    """Context manager that measures execution time."""

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed = time.perf_counter() - self.start
        print(f"Elapsed time: {self.elapsed:.4f}s")
        return False  # Don't suppress exceptions

# Test
with Timer() as t:
    time.sleep(1)
    result = sum(range(1000000))

print(f"Block took {t.elapsed:.2f} seconds")
```

---

## Exercise 2 Solution

```python
import tempfile
from pathlib import Path

class TempFile:
    """Context manager for temporary files."""

    def __init__(self, suffix: str = ".txt", content: str = None):
        self.suffix = suffix
        self.content = content
        self.path = None

    def __enter__(self) -> Path:
        # Create temp file
        fd, path_str = tempfile.mkstemp(suffix=self.suffix)
        self.path = Path(path_str)

        # Write content if provided
        if self.content:
            self.path.write_text(self.content)

        return self.path

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Delete the temp file
        if self.path and self.path.exists():
            self.path.unlink()
        return False

# Test
with TempFile(suffix=".json", content='{"key": "value"}') as filepath:
    print(f"Temp file: {filepath}")
    print(f"Content: {filepath.read_text()}")

print(f"File exists: {filepath.exists()}")  # False
```

---

## Exercise 3 Solution

```python
class MockDatabase:
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
    def __init__(self, db: MockDatabase):
        self.db = db

    def __enter__(self):
        self.db.begin()
        return self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.db.commit()
        else:
            self.db.rollback()
        return False  # Don't suppress the exception

# Test
db = MockDatabase()

with Transaction(db):
    db.insert("user1", {"name": "Alice"})
    db.insert("user2", {"name": "Bob"})
print(db.data)

try:
    with Transaction(db):
        db.insert("user3", {"name": "Charlie"})
        raise ValueError("Something went wrong!")
except ValueError:
    pass
print(db.data)  # Rolled back - no user3
```

---

## Exercise 4 Solution

```python
from contextlib import contextmanager
import time
import tempfile
import os
from pathlib import Path

@contextmanager
def timer():
    """Context manager that measures execution time."""
    result = {}
    start = time.perf_counter()
    try:
        yield result
    finally:
        result['elapsed'] = time.perf_counter() - start
        print(f"Elapsed: {result['elapsed']:.4f}s")

@contextmanager
def temp_file(suffix: str = ".txt", content: str = None):
    """Context manager for temporary files."""
    fd, path_str = tempfile.mkstemp(suffix=suffix)
    path = Path(path_str)
    try:
        if content:
            path.write_text(content)
        yield path
    finally:
        if path.exists():
            path.unlink()

@contextmanager
def change_directory(path: str):
    """Temporarily change working directory."""
    original = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(original)

# Test
with timer() as t:
    time.sleep(0.5)
print(f"Elapsed: {t['elapsed']:.2f}s")

with temp_file(suffix=".txt", content="Hello") as path:
    print(path.read_text())

original = os.getcwd()
with change_directory("/tmp"):
    print(f"Now in: {os.getcwd()}")
print(f"Back to: {os.getcwd()}")
```

---

## Exercise 5 Solution

```python
from contextlib import contextmanager

@contextmanager
def suppress_errors(*exception_types, log: bool = False):
    """Suppress specified exceptions."""
    try:
        yield
    except exception_types as e:
        if log:
            print(f"Suppressed {type(e).__name__}: {e}")
        # Return from the except block without re-raising

# Test
with suppress_errors(ValueError, TypeError, log=True):
    int("not a number")
print("Continues after error")

with suppress_errors(KeyError):
    d = {}
    print(d["missing"])

try:
    with suppress_errors(ValueError):
        raise RuntimeError("Different error")
except RuntimeError:
    print("RuntimeError was not suppressed")
```

**Answer to question**:
- Return `True` from `__exit__` to suppress the exception
- Return `False` (or `None`) to propagate the exception

```python
def __exit__(self, exc_type, exc_val, exc_tb):
    if exc_type is SomeException:
        return True  # Suppress
    return False     # Propagate
```

---

## Exercise 6 Solution

```python
from contextlib import contextmanager, ExitStack

@contextmanager
def log_block(name: str):
    print(f"Entering {name}")
    try:
        yield
    finally:
        print(f"Exiting {name}")

@contextmanager
def acquire_lock(name: str):
    print(f"Acquiring lock: {name}")
    try:
        yield name
    finally:
        print(f"Releasing lock: {name}")

# Test nested
with log_block("outer"), log_block("inner"):
    print("Inside both blocks")

# Dynamic combination
resources = ["db", "cache", "queue"]

with ExitStack() as stack:
    locks = [stack.enter_context(acquire_lock(r)) for r in resources]
    print(f"Acquired locks: {locks}")
```

**Output**:
```
Entering outer
Entering inner
Inside both blocks
Exiting inner
Exiting outer
Acquiring lock: db
Acquiring lock: cache
Acquiring lock: queue
Acquired locks: ['db', 'cache', 'queue']
Releasing lock: queue
Releasing lock: cache
Releasing lock: db
```

---

## Exercise 7 Solution

```python
from contextlib import contextmanager
from typing import Generic, TypeVar, Callable
import threading
from queue import Queue, Empty

T = TypeVar('T')

class ResourcePool(Generic[T]):
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
        with self._lock:
            if self._size < self.max_size:
                self._size += 1
                return self.factory()
        return None

    @contextmanager
    def acquire(self):
        resource = None

        # Try to get from pool
        try:
            resource = self._pool.get_nowait()
        except Empty:
            # Pool empty, try to create new
            resource = self._create_resource()

        if resource is None:
            # Wait for one to be returned
            resource = self._pool.get(timeout=self.timeout)

        try:
            yield resource
        finally:
            # Return to pool
            self._pool.put(resource)

    def size(self) -> int:
        return self._size

# Test
class MockConnection:
    _counter = 0

    def __init__(self):
        MockConnection._counter += 1
        self.id = MockConnection._counter
        print(f"Creating connection {self.id}")

    def query(self, sql: str) -> str:
        return f"Connection {self.id} executed: {sql}"

pool = ResourcePool(MockConnection, max_size=3)

with pool.acquire() as conn1:
    print(conn1.query("SELECT 1"))
    with pool.acquire() as conn2:
        print(conn2.query("SELECT 2"))

print(f"Pool size: {pool.size()}")

with pool.acquire() as conn:
    print(f"Reused connection {conn.id}")
```

---

## Exercise 8 Solution

```python
from contextlib import contextmanager
import sys
from io import StringIO
from pathlib import Path

@contextmanager
def capture_output():
    """Capture stdout and stderr."""
    old_stdout = sys.stdout
    old_stderr = sys.stderr

    stdout_capture = StringIO()
    stderr_capture = StringIO()

    sys.stdout = stdout_capture
    sys.stderr = stderr_capture

    output = {'stdout': '', 'stderr': ''}

    try:
        yield output
    finally:
        output['stdout'] = stdout_capture.getvalue()
        output['stderr'] = stderr_capture.getvalue()
        sys.stdout = old_stdout
        sys.stderr = old_stderr

@contextmanager
def redirect_to_file(filepath: Path, mode: str = "w"):
    """Redirect stdout to a file."""
    old_stdout = sys.stdout
    with open(filepath, mode) as f:
        sys.stdout = f
        try:
            yield
        finally:
            sys.stdout = old_stdout

# Test capture_output
with capture_output() as output:
    print("Hello, stdout!")
    print("Error message", file=sys.stderr)

print(f"Captured stdout: {output['stdout']!r}")
print(f"Captured stderr: {output['stderr']!r}")

# Test redirect_to_file
with redirect_to_file(Path("output.txt")):
    print("This goes to file")
    print("So does this")

print(Path("output.txt").read_text())
Path("output.txt").unlink()
```

---

## Context Manager Protocol Summary

```python
class ContextManager:
    def __enter__(self):
        # Setup: acquire resource
        return resource  # Available as 'as' target

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Cleanup: release resource
        # Return True to suppress exception, False to propagate
        return False
```

---

[← Back to Exercises](../exercises/ex_12_context_managers.md) | [← Back to Chapter](../12_context_managers.md) | [← Back to Module 2](../README.md)
