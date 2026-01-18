# Metaprogramming

> **Note:** This is an advanced topic.

## What is Metaprogramming?

Metaprogramming is code that writes or manipulates code.
In Python, this often means:

1. **Decorators** (Changing functions)
2. **Metaclasses** (Changing classes)
3. **Descriptors** (Changing attributes)
4. **Dunder methods** (Hooking into Python's protocols)

## Practical Dunder Methods

Dunder (double underscore) methods are hooks into Python's core protocols. Mastering them lets you create objects that integrate seamlessly with Python's syntax.

### `__call__`: Making Objects Callable

Transform objects into callable entities - useful for configurable functions or stateful processors:

```python
class Multiplier:
    def __init__(self, factor):
        self.factor = factor
        self.call_count = 0

    def __call__(self, value):
        self.call_count += 1
        return value * self.factor

double = Multiplier(2)
triple = Multiplier(3)

print(double(5))  # 10
print(triple(5))  # 15
print(double.call_count)  # 1 - stateful!
```

Use cases: configurable processors, memoization wrappers, factory objects.

### `__getattr__` vs `__getattribute__`

These control attribute access but work differently:

- `__getattr__` - Called only when attribute is **not found** (safer)
- `__getattribute__` - Called for **every** attribute access (dangerous)

```python
class LazyLoader:
    def __init__(self):
        self._cache = {}

    def __getattr__(self, name):
        """Called ONLY when attribute not found normally."""
        if name not in self._cache:
            self._cache[name] = f"Loaded: {name}"
        return self._cache[name]

lazy = LazyLoader()
print(lazy.foo)  # "Loaded: foo" - triggers __getattr__
print(lazy.foo)  # "Loaded: foo" - still triggers (not in __dict__)
print(lazy._cache)  # {'foo': 'Loaded: foo'} - found normally, no trigger
```

**Rules:**
1. Prefer `__getattr__` for fallback behavior (much safer)
2. Only use `__getattribute__` when you need to intercept ALL access
3. Inside `__getattribute__`, use `object.__getattribute__(self, name)` to avoid recursion

### `__missing__`: Smart Dictionaries

Called by `dict` subclasses when a key is not found:

```python
class DefaultConfig(dict):
    """Dictionary with sensible defaults for missing keys."""

    defaults = {
        'timeout': 30,
        'retries': 3,
        'host': 'localhost',
    }

    def __missing__(self, key):
        return self.defaults.get(key)

config = DefaultConfig({'host': 'production.example.com'})
print(config['host'])     # 'production.example.com' - exists
print(config['timeout'])  # 30 - from defaults
print(config['unknown'])  # None - not in defaults either
```

Use cases: configuration objects, caching dictionaries, counter defaults.

### `__index__`: Custom Objects in Slicing

Makes your objects work with sequence indexing and slicing:

```python
class Hour:
    """Represents hours, convertible to seconds for indexing."""

    def __init__(self, hours):
        self.hours = hours

    def __index__(self):
        return self.hours * 3600  # Convert to seconds

data = list(range(10000))
offset = Hour(2)

print(data[offset])   # data[7200] - uses __index__
print(data[:offset])  # data[:7200] - works with slicing too
print(hex(offset))    # '0x1c20' - hex() uses __index__
```

Use cases: domain objects representing positions, offsets, or indices.

### `__slots__`: Memory Optimization

Eliminate per-instance `__dict__` for significant memory savings:

```python
class RegularPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class OptimizedPoint:
    __slots__ = ['x', 'y']

    def __init__(self, x, y):
        self.x = x
        self.y = y

import sys
regular = RegularPoint(1, 2)
optimized = OptimizedPoint(1, 2)

print(sys.getsizeof(regular))   # ~48 bytes + __dict__ overhead
print(sys.getsizeof(optimized)) # ~48 bytes (no __dict__)

# With millions of instances, __slots__ saves hundreds of MB
```

**Trade-offs:**
- Cannot add arbitrary attributes at runtime
- Cannot use `__dict__` for introspection
- Must declare `__slots__` in every subclass

Use when: creating millions of simple objects with fixed attributes.

### `__fspath__`: Path Protocol Compatibility

Make custom objects work with `open()`, `Path.exists()`, and other filesystem functions:

```python
from pathlib import Path
import os

class DataPath:
    """Custom path with data-specific logic."""

    def __init__(self, base, date, name):
        self.base = Path(base)
        self.date = date
        self.name = name

    def __fspath__(self):
        return str(self.base / self.date / f"{self.name}.csv")

data = DataPath("/data", "2024-01", "sales")

# Works with standard library functions!
print(os.path.exists(data))  # Uses __fspath__
# with open(data, 'r') as f:  # Would work if file exists
```

## Concepts

* `type()` is actually a class that creates classes.
* Every class is an instance of a metaclass (usually `type`).
* Descriptors (`__get__`, `__set__`, `__delete__`) control attribute behavior on classes.

## When to Use Metaprogramming

**Do use when:**
- Building frameworks or libraries
- Eliminating repetitive boilerplate
- Creating domain-specific languages (DSLs)

**Avoid when:**
- Simple solutions exist
- Code clarity would suffer
- Debugging would become difficult

> "Debugging is twice as hard as writing code. If you write code as cleverly as possible, you are by definition not smart enough to debug it." - Brian Kernighan
