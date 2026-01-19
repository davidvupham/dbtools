# Solutions — 11: Decorators

## Key Concepts Demonstrated

- Basic decorator structure
- `functools.wraps` for metadata preservation
- Decorators with arguments (triple nesting)
- Class-based decorators
- Decorator stacking order
- Common patterns: timing, retry, memoization, validation

## Common Mistakes to Avoid

- Forgetting `@functools.wraps(func)`
- Forgetting to return the wrapper function
- Forgetting to return `func(*args, **kwargs)` result
- Wrong nesting level for decorators with arguments

---

## Exercise 1 Solution

```python
from functools import wraps

def debug(func):
    """Print function name and arguments when called."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        print(f"DEBUG: Calling {func.__name__}({signature})")
        result = func(*args, **kwargs)
        print(f"DEBUG: {func.__name__} returned {result!r}")
        return result
    return wrapper

@debug
def add(a, b):
    return a + b

@debug
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

# Test
result = add(2, 3)
print(result)

greet("Alice")
```

---

## Exercise 2 Solution

```python
import time
from functools import wraps

def timer(func):
    """Measure and print execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper

@timer
def slow_function(n):
    time.sleep(n)
    return f"Slept for {n} seconds"

@timer
def calculate_sum(n):
    return sum(range(n))

# Test
slow_function(1)
result = calculate_sum(1000000)
print(result)
```

---

## Exercise 3 Solution

```python
from functools import wraps

def repeat(times: int):
    """Call the function multiple times and return list of results."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return [func(*args, **kwargs) for _ in range(times)]
        return wrapper
    return decorator

@repeat(times=3)
def greet(name):
    return f"Hello, {name}!"

@repeat(times=5)
def roll_dice():
    import random
    return random.randint(1, 6)

# Test
results = greet("Alice")
print(results)  # ['Hello, Alice!', 'Hello, Alice!', 'Hello, Alice!']

rolls = roll_dice()
print(rolls)  # [random numbers]
```

---

## Exercise 4 Solution

```python
import time
from functools import wraps
from typing import Type

def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    exceptions: tuple[Type[Exception], ...] = (Exception,)
):
    """Retry function on failure."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    print(f"Attempt {attempt} failed: {e}")
                    if attempt < max_attempts:
                        time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator

# Test
attempt_count = 0

@retry(max_attempts=5, delay=0.1, exceptions=(ConnectionError,))
def flaky_connection():
    global attempt_count
    attempt_count += 1
    if attempt_count < 3:
        raise ConnectionError("Connection refused")
    return "Connected!"

result = flaky_connection()
print(result)
print(f"Took {attempt_count} attempts")
```

---

## Exercise 5 Solution

```python
from functools import wraps

def memoize(func):
    """Cache function results based on arguments."""
    cache = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create hashable key from arguments
        key = (args, tuple(sorted(kwargs.items())))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    wrapper.cache = cache
    wrapper.clear_cache = lambda: cache.clear()
    return wrapper

@memoize
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

@memoize
def expensive_calculation(x, y, operation="add"):
    print(f"  Computing {operation}({x}, {y})...")
    if operation == "add":
        return x + y
    elif operation == "multiply":
        return x * y

# Test
print(fibonacci(30))
print(f"Cache size: {len(fibonacci.cache)}")

print(expensive_calculation(5, 3))
print(expensive_calculation(5, 3))  # Cached, no print
print(expensive_calculation(5, 3, operation="multiply"))
print(expensive_calculation(5, 3, operation="multiply"))  # Cached
```

---

## Exercise 6 Solution

```python
from functools import wraps
from typing import Callable, Any
import inspect

def validate(**validators: Callable[[Any], bool]):
    """Validate function arguments."""
    def decorator(func):
        sig = inspect.signature(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Bind arguments to parameter names
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()

            # Validate each parameter with a validator
            for param_name, validator in validators.items():
                if param_name in bound.arguments:
                    value = bound.arguments[param_name]
                    if not validator(value):
                        raise ValueError(f"Invalid value for '{param_name}': {value!r}")

            return func(*args, **kwargs)
        return wrapper
    return decorator

# Validation functions
def is_positive(x):
    return isinstance(x, (int, float)) and x > 0

def is_non_empty_string(s):
    return isinstance(s, str) and len(s) > 0

def is_valid_email(email):
    return isinstance(email, str) and "@" in email and "." in email

@validate(amount=is_positive, description=is_non_empty_string)
def create_transaction(amount: float, description: str):
    return {"amount": amount, "description": description}

@validate(email=is_valid_email, age=is_positive)
def create_user(name: str, email: str, age: int):
    return {"name": name, "email": email, "age": age}

# Test
print(create_transaction(100.0, "Payment"))

try:
    create_transaction(-50, "Invalid")
except ValueError as e:
    print(f"Error: {e}")

try:
    create_user("Alice", "not-an-email", 25)
except ValueError as e:
    print(f"Error: {e}")
```

---

## Exercise 7 Solution

```python
def singleton(cls):
    """Make a class a singleton."""
    instances = {}

    @wraps(cls, updated=[])
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance

@singleton
class DatabaseConnection:
    def __init__(self, host: str = "localhost"):
        self.host = host
        print(f"Creating connection to {host}")

    def query(self, sql: str):
        return f"Executing on {self.host}: {sql}"

# Test
conn1 = DatabaseConnection("db.example.com")
conn2 = DatabaseConnection("other.host.com")

print(conn1 is conn2)  # True
print(conn2.host)      # "db.example.com"

# Plugin Registry
class PluginRegistry:
    plugins = {}

    @classmethod
    def register(cls, name: str):
        def decorator(plugin_cls):
            cls.plugins[name] = plugin_cls
            return plugin_cls
        return decorator

    @classmethod
    def get(cls, name: str):
        return cls.plugins.get(name)

@PluginRegistry.register("json")
class JsonProcessor:
    def process(self, data):
        import json
        return json.dumps(data)

@PluginRegistry.register("csv")
class CsvProcessor:
    def process(self, data):
        return ",".join(str(v) for v in data)

# Test
print(PluginRegistry.plugins)
processor = PluginRegistry.get("json")()
print(processor.process({"key": "value"}))
```

---

## Exercise 8 Solution

```python
@decorator_a
@decorator_b
@decorator_c
def greet(name):
    print(f"Hello, {name}!")
    return name

result = greet("World")
```

**Output**:
```
A before
B before
C before
Hello, World!
C after
B after
A after
```

**Answers**:

1. **Output**: See above. The decorators wrap each other like layers.

2. **Application order**: Bottom to top
   - First `@decorator_c` wraps `greet`
   - Then `@decorator_b` wraps the result
   - Finally `@decorator_a` wraps everything
   - Equivalent to: `greet = decorator_a(decorator_b(decorator_c(greet)))`

3. **Execution order**: Outside to inside, then inside to outside
   - A's "before" runs first (outermost)
   - B's "before" runs second
   - C's "before" runs third
   - Original function runs
   - C's "after" runs (innermost wrapper returns first)
   - B's "after" runs
   - A's "after" runs last

Think of it like nested function calls or Russian dolls.

---

## Exercise 9 Solution

```python
import logging
import time
from functools import wraps
from datetime import datetime

def logged(
    level: int = logging.INFO,
    log_args: bool = True,
    log_result: bool = True,
    log_time: bool = True
):
    """Decorator that logs function calls."""
    def decorator(func):
        logger = logging.getLogger(func.__module__)

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Build log message for call
            if log_args:
                args_repr = [repr(a) for a in args]
                kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
                signature = ", ".join(args_repr + kwargs_repr)
                call_msg = f"Calling {func.__name__}({signature})"
            else:
                call_msg = f"Calling {func.__name__}"

            logger.log(level, call_msg)

            # Execute function
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                logger.log(level, f"{func.__name__} raised {type(e).__name__}: {e}")
                raise

            elapsed = time.perf_counter() - start

            # Build result message
            parts = [func.__name__]
            if log_result:
                parts.append(f"returned {result!r}")
            if log_time:
                parts.append(f"in {elapsed:.4f}s")

            logger.log(level, " ".join(parts))
            return result

        return wrapper
    return decorator

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

@logged(level=logging.DEBUG, log_args=True, log_result=True, log_time=True)
def calculate(x, y, operation="add"):
    if operation == "add":
        return x + y
    elif operation == "multiply":
        return x * y

@logged(level=logging.INFO, log_args=False)
def process_data(data):
    return len(data)

# Test
calculate(10, 5, operation="multiply")
process_data([1, 2, 3, 4, 5])
```

---

## Decorator Pattern Summary

| Pattern | Use Case |
|---------|----------|
| Basic | Add behavior before/after function |
| With arguments | Configurable decoration |
| Class decorator | Modify class behavior |
| Stacking | Combine multiple behaviors |
| Memoization | Cache expensive computations |
| Validation | Check inputs |
| Retry | Handle transient failures |
| Logging | Track function calls |

---

[← Back to Exercises](../exercises/ex_11_decorators.md) | [← Back to Chapter](../11_decorators.md) | [← Back to Module 2](../README.md)
