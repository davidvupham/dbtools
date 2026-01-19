# Exercises — 11: Decorators

## Learning Objectives

After completing these exercises, you will be able to:
- Write simple decorators
- Use `functools.wraps` to preserve metadata
- Create decorators with arguments
- Apply multiple decorators to a function
- Build class-based decorators
- Use decorators for common patterns (timing, logging, retry)

---

## Exercise 1: Basic Decorator (Warm-up)

**Bloom Level**: Apply

Write a `debug` decorator that prints function calls:

```python
from functools import wraps

def debug(func):
    """Print function name and arguments when called."""
    # Your implementation here
    pass

@debug
def add(a, b):
    return a + b

@debug
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

# Test
result = add(2, 3)
# DEBUG: Calling add(2, 3)
# DEBUG: add returned 5
print(result)  # 5

greet("Alice")
# DEBUG: Calling greet('Alice', greeting='Hello')
# DEBUG: greet returned 'Hello, Alice!'
```

---

## Exercise 2: Timer Decorator (Practice)

**Bloom Level**: Apply

Write a `timer` decorator that measures execution time:

```python
import time
from functools import wraps

def timer(func):
    """Measure and print execution time."""
    pass

@timer
def slow_function(n):
    """Simulate a slow function."""
    time.sleep(n)
    return f"Slept for {n} seconds"

@timer
def calculate_sum(n):
    """Calculate sum of first n numbers."""
    return sum(range(n))

# Test
slow_function(1)
# slow_function took 1.0012s

result = calculate_sum(1000000)
# calculate_sum took 0.0234s
print(result)
```

---

## Exercise 3: Decorator with Arguments (Practice)

**Bloom Level**: Apply

Write a `repeat` decorator that calls a function multiple times:

```python
from functools import wraps

def repeat(times: int):
    """Call the function multiple times and return list of results."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Your implementation
            pass
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
print(rolls)  # [3, 1, 6, 4, 2] (random)
```

---

## Exercise 4: Retry Decorator (Practice)

**Bloom Level**: Apply

Write a `retry` decorator for handling transient failures:

```python
import time
from functools import wraps
from typing import Type

def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    exceptions: tuple[Type[Exception], ...] = (Exception,)
):
    """
    Retry function on failure.

    Args:
        max_attempts: Maximum number of attempts.
        delay: Seconds to wait between attempts.
        exceptions: Tuple of exceptions to catch.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Your implementation
            pass
        return wrapper
    return decorator

# Test with simulated failures
attempt_count = 0

@retry(max_attempts=5, delay=0.1, exceptions=(ConnectionError,))
def flaky_connection():
    global attempt_count
    attempt_count += 1
    if attempt_count < 3:
        raise ConnectionError("Connection refused")
    return "Connected!"

result = flaky_connection()
print(result)  # "Connected!" (after 3 attempts)
print(f"Took {attempt_count} attempts")  # 3
```

---

## Exercise 5: Memoization Decorator (Practice)

**Bloom Level**: Apply

Write a custom `memoize` decorator (similar to `lru_cache`):

```python
from functools import wraps

def memoize(func):
    """
    Cache function results based on arguments.
    Only works with hashable arguments.
    """
    cache = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create cache key from arguments
        # Your implementation
        pass

    wrapper.cache = cache  # Expose cache for inspection
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
print(fibonacci(30))  # Fast due to memoization
print(f"Cache size: {len(fibonacci.cache)}")

print(expensive_calculation(5, 3))  # Computes
print(expensive_calculation(5, 3))  # Cached
print(expensive_calculation(5, 3, operation="multiply"))  # Computes
print(expensive_calculation(5, 3, operation="multiply"))  # Cached
```

---

## Exercise 6: Validate Decorator (Analyze)

**Bloom Level**: Analyze

Write a `validate` decorator that checks function arguments:

```python
from functools import wraps
from typing import Callable, Any

def validate(**validators: Callable[[Any], bool]):
    """
    Validate function arguments.

    Args:
        **validators: Parameter name to validation function mapping.
                     Validation function returns True if valid.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get function signature and bind arguments
            # Your implementation
            pass
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
print(create_transaction(100.0, "Payment"))  # Works

try:
    create_transaction(-50, "Invalid")
except ValueError as e:
    print(f"Error: {e}")  # Error: Invalid value for 'amount'

try:
    create_user("Alice", "not-an-email", 25)
except ValueError as e:
    print(f"Error: {e}")  # Error: Invalid value for 'email'
```

---

## Exercise 7: Class Decorator (Challenge)

**Bloom Level**: Create

Create a decorator that adds singleton behavior to a class:

```python
def singleton(cls):
    """
    Make a class a singleton (only one instance).
    """
    pass

@singleton
class DatabaseConnection:
    def __init__(self, host: str = "localhost"):
        self.host = host
        print(f"Creating connection to {host}")

    def query(self, sql: str):
        return f"Executing on {self.host}: {sql}"

# Test
conn1 = DatabaseConnection("db.example.com")  # Creates instance
conn2 = DatabaseConnection("other.host.com")  # Returns same instance

print(conn1 is conn2)  # True
print(conn2.host)      # "db.example.com" (first initialization wins)
```

Also create a `register` decorator that registers classes:

```python
class PluginRegistry:
    plugins = {}

    @classmethod
    def register(cls, name: str):
        """Decorator to register a plugin class."""
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
# {'json': <class 'JsonProcessor'>, 'csv': <class 'CsvProcessor'>}

processor = PluginRegistry.get("json")()
print(processor.process({"key": "value"}))  # '{"key": "value"}'
```

---

## Exercise 8: Stacking Decorators (Analyze)

**Bloom Level**: Analyze

Predict the output and explain the execution order:

```python
def decorator_a(func):
    def wrapper(*args, **kwargs):
        print("A before")
        result = func(*args, **kwargs)
        print("A after")
        return result
    return wrapper

def decorator_b(func):
    def wrapper(*args, **kwargs):
        print("B before")
        result = func(*args, **kwargs)
        print("B after")
        return result
    return wrapper

def decorator_c(func):
    def wrapper(*args, **kwargs):
        print("C before")
        result = func(*args, **kwargs)
        print("C after")
        return result
    return wrapper

@decorator_a
@decorator_b
@decorator_c
def greet(name):
    print(f"Hello, {name}!")
    return name

result = greet("World")
```

**Questions**:
1. What is the output?
2. In what order are the decorators applied?
3. In what order do they execute?

---

## Exercise 9: Logging Decorator (Challenge)

**Bloom Level**: Create

Create a comprehensive logging decorator:

```python
import logging
from functools import wraps
from datetime import datetime

def logged(
    level: int = logging.INFO,
    log_args: bool = True,
    log_result: bool = True,
    log_time: bool = True
):
    """
    Decorator that logs function calls.

    Args:
        level: Logging level.
        log_args: Whether to log arguments.
        log_result: Whether to log return value.
        log_time: Whether to log execution time.
    """
    pass

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
# DEBUG: Calling calculate(10, 5, operation='multiply')
# DEBUG: calculate returned 50 in 0.0001s

process_data([1, 2, 3, 4, 5])
# INFO: Calling process_data
# INFO: process_data returned 5
```

---

## Deliverables

Submit your code for all exercises. Include your analysis for Exercise 8.

---

[← Back to Chapter](../11_decorators.md) | [View Solutions](../solutions/sol_11_decorators.md) | [← Back to Module 2](../README.md)
