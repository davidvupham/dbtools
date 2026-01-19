# Solutions — 17: Metaprogramming

## Key Concepts Demonstrated

- `__call__` for callable objects
- `__getattr__` for dynamic attribute access
- `__missing__` for custom dict behavior
- `__slots__` for memory optimization
- Descriptor protocol (`__get__`, `__set__`, `__set_name__`)
- When to use (and avoid) metaprogramming

## Common Mistakes to Avoid

- Using `__getattribute__` when `__getattr__` suffices (causes recursion)
- Forgetting that `__slots__` prevents dynamic attributes
- Overcomplicating code with unnecessary metaprogramming
- Not testing edge cases with descriptors

---

## Exercise 1 Solution

```python
class PowerOf:
    """Callable that raises numbers to a configured power."""

    def __init__(self, exponent: int):
        self.exponent = exponent

    def __call__(self, base: int) -> int:
        return base ** self.exponent

# Test
square = PowerOf(2)
cube = PowerOf(3)

print(square(5))  # 25
print(cube(3))    # 27

numbers = [1, 2, 3, 4, 5]
print(list(map(square, numbers)))  # [1, 4, 9, 16, 25]
```

---

## Exercise 2 Solution

```python
import random
from functools import wraps

class Retry:
    """Callable that retries a function on failure."""

    def __init__(self, max_attempts: int = 3, exceptions: tuple = (Exception,)):
        self.max_attempts = max_attempts
        self.exceptions = exceptions
        self.attempts = 0

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.attempts = 0
            last_exception = None

            for attempt in range(1, self.max_attempts + 1):
                self.attempts = attempt
                try:
                    return func(*args, **kwargs)
                except self.exceptions as e:
                    last_exception = e
                    print(f"Attempt {attempt} failed: {e}")

            raise last_exception

        return wrapper

# Test
@Retry(max_attempts=5, exceptions=(ValueError,))
def flaky_function():
    if random.random() < 0.7:
        raise ValueError("Random failure")
    return "Success!"

try:
    result = flaky_function()
    print(result)
except ValueError:
    print("All attempts failed")
```

---

## Exercise 3 Solution

```python
class LazyConfig:
    """Configuration object that loads settings lazily."""

    def __init__(self, config_source: dict):
        self._source = config_source
        self._cache = {}

    def __getattr__(self, name: str):
        # Avoid recursion with _cache and _source
        if name.startswith('_'):
            raise AttributeError(name)

        if name in self._cache:
            return self._cache[name]

        value = self._load_setting(name)
        self._cache[name] = value
        return value

    def _load_setting(self, name: str):
        print(f"Loading setting: {name}")
        if name not in self._source:
            return None  # Or raise AttributeError
        return self._source[name]

# Test
config_data = {
    "database_url": "postgresql://localhost/db",
    "api_key": "secret-key-123",
    "debug": True,
}

config = LazyConfig(config_data)

print(config.database_url)  # Loads and prints value
print(config.database_url)  # Uses cache
print(config.missing)       # None
```

---

## Exercise 4 Solution

```python
class ConfigDict(dict):
    """Dictionary with defaults and nested access."""

    def __init__(self, data: dict = None, defaults: dict = None):
        super().__init__(data or {})
        self.defaults = defaults or {}

    def __missing__(self, key):
        if key in self.defaults:
            return self.defaults[key]
        return None  # Or raise KeyError(key)

    def get_nested(self, path: str, default=None):
        keys = path.split('.')
        value = self

        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default

        return value

# Test
defaults = {"timeout": 30, "retries": 3}

config = ConfigDict(
    {"host": "localhost", "database": {"name": "mydb", "port": 5432}},
    defaults=defaults
)

print(config["host"])          # "localhost"
print(config["timeout"])       # 30
print(config["missing"])       # None

print(config.get_nested("database.name"))  # "mydb"
print(config.get_nested("database.host", "localhost"))  # "localhost"
```

---

## Exercise 5 Solution

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

regular = PointRegular(1, 2, 3)
slotted = PointSlots(1, 2, 3)

print(f"Regular: {sys.getsizeof(regular)} bytes")  # ~48 bytes
print(f"Slotted: {sys.getsizeof(slotted)} bytes")  # ~48 bytes
# Note: The __dict__ overhead isn't included in getsizeof

regular.w = 4  # Works
try:
    slotted.w = 4
except AttributeError as e:
    print(f"Error: {e}")
```

**Answers**:

1. **Memory saved**: ~200-300 bytes per instance on 64-bit Python (the `__dict__` overhead)

2. **Trade-offs**:
   - Cannot add attributes dynamically
   - Cannot use `__dict__` for introspection
   - Must declare `__slots__` in every subclass
   - Some serialization libraries may not work correctly

3. **When NOT to use**:
   - When you need dynamic attributes
   - When memory isn't a concern
   - When inheriting from classes without `__slots__`
   - When using mixins that need `__dict__`

---

## Exercise 6 Solution

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
        if not isinstance(value, (int, float)):
            raise TypeError(f"{self.name} must be a number")
        if value <= 0:
            raise ValueError(f"{self.name} must be positive, got {value}")
        setattr(obj, self.private_name, value)

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
    rect.width = -5
except ValueError as e:
    print(f"Error: {e}")  # Error: width must be positive, got -5
```

---

## Exercise 7 Solution

```python
class TypedAttribute:
    """Descriptor that enforces type checking."""

    def __init__(self, expected_type, default=None):
        self.expected_type = expected_type
        self.default = default
        self.name = None
        self.private_name = None

    def __set_name__(self, owner, name):
        self.name = name
        self.private_name = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.private_name, self.default)

    def __set__(self, obj, value):
        if not isinstance(value, self.expected_type):
            raise TypeError(
                f"{self.name} must be {self.expected_type.__name__}, "
                f"got {type(value).__name__}"
            )
        setattr(obj, self.private_name, value)

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

person.age = 31
try:
    person.age = "thirty"
except TypeError as e:
    print(f"Error: {e}")  # Error: age must be int, got str
```

---

## Exercise 8 Solution

```python
from datetime import datetime
from typing import Any, List, Tuple

class AuditTrailMixin:
    """Mixin that tracks all attribute modifications."""

    def __init__(self, *args, **kwargs):
        object.__setattr__(self, '_changes', [])
        super().__init__(*args, **kwargs)

    def __setattr__(self, name: str, value: Any):
        # Skip internal attributes
        if name.startswith('_'):
            object.__setattr__(self, name, value)
            return

        # Get old value if it exists
        old_value = getattr(self, name, '<not set>')

        # Record the change
        self._changes.append({
            'timestamp': datetime.now(),
            'attribute': name,
            'old_value': old_value,
            'new_value': value,
        })

        # Set the attribute
        object.__setattr__(self, name, value)

    def get_changes(self) -> List[dict]:
        return self._changes.copy()

    def get_changes_for(self, attribute: str) -> List[dict]:
        return [c for c in self._changes if c['attribute'] == attribute]

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

print("All changes:")
for change in user.get_changes():
    print(f"  {change['attribute']}: {change['old_value']} -> {change['new_value']}")

print("\nName changes:")
for change in user.get_changes_for("name"):
    print(f"  {change['old_value']} -> {change['new_value']}")
```

---

## Exercise 9 Solution

### 1. ORM Field Validation
**Use metaprogramming?** Yes, with caution.
- Descriptors or metaclasses can enforce validation across all models
- Simpler alternative: Use Pydantic or attrs which handle this built-in
- Best approach: Use existing libraries (SQLAlchemy, Django ORM)

### 2. API Response Caching
**Use metaprogramming?** No.
- A simple decorator is sufficient and more readable
- Metaprogramming would be overkill
- Simpler alternative: `@functools.lru_cache` or `@cache` decorator

### 3. Debug Logging
**Use metaprogramming?** Maybe, for development tools.
- Class decorator or metaclass could wrap all methods
- But this is complex and hard to maintain
- Simpler alternatives:
  - Debugger breakpoints
  - Strategic logging statements
  - IDE debugging features

### 4. Configuration Management
**Use metaprogramming?** No.
- Dataclasses or Pydantic handle this elegantly
- Type hints + runtime validation libraries are cleaner
- Simpler alternative: `pydantic.BaseSettings` or `dataclasses` with `dacite`

### General Guidelines

**Use metaprogramming when:**
- Building frameworks or libraries
- Eliminating significant boilerplate
- Creating DSLs (Domain Specific Languages)
- No simpler solution exists

**Avoid metaprogramming when:**
- A decorator or simple class suffices
- Existing libraries solve the problem
- Team members won't understand it
- The complexity outweighs the benefits

---

## Metaprogramming Decision Tree

```
Do you need custom behavior?
├── No → Use normal classes/functions
└── Yes → Can a decorator solve it?
    ├── Yes → Use decorator
    └── No → Can a descriptor solve it?
        ├── Yes → Use descriptor
        └── No → Is it attribute-related?
            ├── Yes → Use __getattr__/__setattr__
            └── No → Consider metaclass (rarely needed)
```

---

[← Back to Exercises](../exercises/ex_17_metaprogramming.md) | [← Back to Chapter](../17_metaprogramming.md) | [← Back to Module 3](../README.md)
