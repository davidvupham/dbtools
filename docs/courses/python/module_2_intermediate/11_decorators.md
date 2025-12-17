# Decorators and Closures

## Inner Functions and Closures

### What is an Inner Function?

An **inner function** (or nested function) is simply a function defined inside another function.

```python
def outer_function():
    print("This is the outer function")

    def inner_function():
        print("This is the inner function")

    inner_function()

outer_function()
```

Inner functions are hidden from the outside world (Encapsulation).

### Closures

A **closure** is an inner function that remembers values from its enclosing scope even after the outer function has finished executing.

```python
def make_multiplier(factor):
    def multiplier(number):
        return number * factor
    return multiplier

doubler = make_multiplier(2)
print(doubler(10))  # 20
```

## Decorators

A **decorator** is a design pattern in Python that allows you to modify the behavior of a function or class. It's essentially a wrapper.

### Syntax

```python
@decorator_name
def my_function():
    pass
```

### Creating a Decorator

```python
def make_bold(func):
    def wrapper():
        return f"<b>{func()}</b>"
    return wrapper

@make_bold
def hello():
    return "Hello"

print(hello())  # <b>Hello</b>
```

### Decorators with Arguments

```python
def repeat(times):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(times):
                func(*args, **kwargs)
        return wrapper
    return decorator

@repeat(3)
def greet(name):
    print(f"Hello, {name}")

greet("Alice")
```

### Real World Example: Retry Logic

```python
import time
from functools import wraps

def with_retry(max_attempts=3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(1)
        return wrapper
    return decorator
```
