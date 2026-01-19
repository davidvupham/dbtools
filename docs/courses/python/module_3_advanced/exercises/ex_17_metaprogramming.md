# Exercises — 17: Metaprogramming

## Learning Objectives

After completing these exercises, you will be able to:
- Implement practical dunder methods
- Create callable classes with `__call__`
- Use `__getattr__` for dynamic attribute access
- Understand `__slots__` for memory optimization
- Build simple descriptors
- Apply metaprogramming patterns appropriately

---

## Exercise 1: Callable Classes (Warm-up)

**Bloom Level**: Apply

Create callable classes that work like configurable functions:

```python
class PowerOf:
    """Callable that raises numbers to a configured power."""

    def __init__(self, exponent: int):
        pass

    def __call__(self, base: int) -> int:
        pass

# Test
square = PowerOf(2)
cube = PowerOf(3)

print(square(5))  # 25
print(cube(3))    # 27

# Should work in map/filter
numbers = [1, 2, 3, 4, 5]
print(list(map(square, numbers)))  # [1, 4, 9, 16, 25]
```

---

## Exercise 2: Retry Callable (Practice)

**Bloom Level**: Apply

Create a callable class that retries failed function calls:

```python
import random

class Retry:
    """
    Callable that retries a function on failure.

    Can be used as a decorator or called directly.
    """

    def __init__(self, max_attempts: int = 3, exceptions: tuple = (Exception,)):
        self.max_attempts = max_attempts
        self.exceptions = exceptions
        self.attempts = 0  # Track last attempt count

    def __call__(self, func):
        """Make this work as a decorator."""
        pass

# Test as decorator
@Retry(max_attempts=5, exceptions=(ValueError,))
def flaky_function():
    if random.random() < 0.7:
        raise ValueError("Random failure")
    return "Success!"

result = flaky_function()
print(result)
```

---

## Exercise 3: Lazy Attribute Loading (Practice)

**Bloom Level**: Apply

Use `__getattr__` to implement lazy loading of expensive attributes:

```python
class LazyConfig:
    """
    Configuration object that loads settings lazily.

    Settings are only fetched when first accessed.
    """

    def __init__(self, config_source: dict):
        self._source = config_source
        self._cache = {}

    def __getattr__(self, name: str):
        """Called when attribute not found normally."""
        pass

    def _load_setting(self, name: str):
        """Simulate expensive loading operation."""
        print(f"Loading setting: {name}")
        return self._source.get(name)

# Test
config_data = {
    "database_url": "postgresql://localhost/db",
    "api_key": "secret-key-123",
    "debug": True,
}

config = LazyConfig(config_data)

# First access loads the value
print(config.database_url)  # "Loading setting: database_url" then value
print(config.database_url)  # Just value (cached)

# Missing settings
print(config.missing)  # Should return None or raise AttributeError
```

---

## Exercise 4: Dictionary with Defaults (Practice)

**Bloom Level**: Apply

Use `__missing__` to create a smart dictionary:

```python
class ConfigDict(dict):
    """
    Dictionary that returns defaults for missing keys
    and supports nested key access with dot notation.
    """

    def __init__(self, data: dict = None, defaults: dict = None):
        super().__init__(data or {})
        self.defaults = defaults or {}

    def __missing__(self, key):
        pass

    def get_nested(self, path: str, default=None):
        """
        Get nested value using dot notation.
        Example: config.get_nested("database.host")
        """
        pass

# Test
defaults = {
    "timeout": 30,
    "retries": 3,
}

config = ConfigDict(
    {"host": "localhost", "database": {"name": "mydb", "port": 5432}},
    defaults=defaults
)

print(config["host"])          # "localhost"
print(config["timeout"])       # 30 (from defaults)
print(config["missing"])       # None or KeyError

print(config.get_nested("database.name"))  # "mydb"
print(config.get_nested("database.host", "localhost"))  # "localhost"
```

---

## Exercise 5: Memory-Efficient Point (Analyze)

**Bloom Level**: Analyze

Compare memory usage with and without `__slots__`:

```python
import sys

class PointRegular:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class PointSlots:
    __slots__ = ['x', 'y', 'z']

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

# Create instances
regular = PointRegular(1, 2, 3)
slotted = PointSlots(1, 2, 3)

# Compare sizes
print(f"Regular: {sys.getsizeof(regular)} bytes")
print(f"Slotted: {sys.getsizeof(slotted)} bytes")

# Try adding dynamic attribute
regular.w = 4  # Works
try:
    slotted.w = 4  # Should fail
except AttributeError as e:
    print(f"Error: {e}")

# Create many instances and compare total memory
# (Use a memory profiler for accurate measurement)
```

**Questions**:
1. How much memory is saved per instance?
2. What are the trade-offs of using `__slots__`?
3. When would you choose not to use `__slots__`?

---

## Exercise 6: Simple Descriptor (Practice)

**Bloom Level**: Apply

Create a descriptor for validated attributes:

```python
class PositiveNumber:
    """Descriptor that ensures values are positive."""

    def __init__(self, name):
        self.name = name
        self.private_name = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.private_name, None)

    def __set__(self, obj, value):
        pass  # Validate and set

class Rectangle:
    width = PositiveNumber("width")
    height = PositiveNumber("height")

    def __init__(self, width, height):
        self.width = width
        self.height = height

    @property
    def area(self):
        return self.width * self.height

# Test
rect = Rectangle(10, 5)
print(rect.area)  # 50

rect.width = 20
print(rect.area)  # 100

try:
    rect.width = -5  # Should raise ValueError
except ValueError as e:
    print(f"Error: {e}")
```

---

## Exercise 7: Type-Checked Descriptor (Challenge)

**Bloom Level**: Create

Create a descriptor that enforces type checking:

```python
class TypedAttribute:
    """
    Descriptor that enforces type checking.

    Usage:
        class Person:
            name = TypedAttribute(str)
            age = TypedAttribute(int)
    """

    def __init__(self, expected_type, default=None):
        self.expected_type = expected_type
        self.default = default

    def __set_name__(self, owner, name):
        """Called automatically when descriptor is assigned to class."""
        self.name = name
        self.private_name = f"_{name}"

    def __get__(self, obj, objtype=None):
        pass

    def __set__(self, obj, value):
        pass

class Person:
    name = TypedAttribute(str)
    age = TypedAttribute(int)
    active = TypedAttribute(bool, default=True)

    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

# Test
person = Person("Alice", 30)
print(person.name)    # "Alice"
print(person.age)     # 30
print(person.active)  # True

person.age = 31  # OK
try:
    person.age = "thirty"  # Should raise TypeError
except TypeError as e:
    print(f"Error: {e}")
```

---

## Exercise 8: Audit Trail Mixin (Challenge)

**Bloom Level**: Create

Create a mixin that tracks all attribute changes:

```python
from datetime import datetime
from typing import Any

class AuditTrailMixin:
    """
    Mixin that tracks all attribute modifications.

    Provides:
    - _changes: List of (timestamp, attribute, old_value, new_value)
    - get_changes(): Get all changes
    - get_changes_for(attr): Get changes for specific attribute
    """

    def __init__(self, *args, **kwargs):
        self._changes = []
        super().__init__(*args, **kwargs)

    def __setattr__(self, name: str, value: Any):
        pass  # Record change and set attribute

    def get_changes(self):
        """Return all recorded changes."""
        pass

    def get_changes_for(self, attribute: str):
        """Return changes for a specific attribute."""
        pass

class User(AuditTrailMixin):
    def __init__(self, name: str, email: str):
        super().__init__()
        self.name = name
        self.email = email

# Test
user = User("Alice", "alice@example.com")
user.name = "Alice Smith"
user.email = "alice.smith@example.com"
user.name = "Alice Johnson"

for change in user.get_changes():
    print(change)

print("\nName changes:")
for change in user.get_changes_for("name"):
    print(change)
```

---

## Exercise 9: When to Use Metaprogramming (Analyze)

**Bloom Level**: Evaluate

For each scenario, decide if metaprogramming is appropriate:

1. **ORM field validation**: You want all model fields to automatically validate types.
   - Use metaprogramming? Why or why not?
   - What approach would you use?

2. **API response caching**: You want to cache certain API endpoints.
   - Use metaprogramming? Why or why not?
   - What's a simpler alternative?

3. **Debug logging**: You want to log every method call in development.
   - Use metaprogramming? Why or why not?
   - What approach would you use?

4. **Configuration management**: You want type-safe configuration loading.
   - Use metaprogramming? Why or why not?
   - What's a simpler alternative?

Provide brief answers for each scenario.

---

## Deliverables

Submit your code for exercises 1-8 and your analysis for exercise 9.

---

[← Back to Chapter](../17_metaprogramming.md) | [View Solutions](../solutions/sol_17_metaprogramming.md) | [← Back to Module 3](../README.md)
